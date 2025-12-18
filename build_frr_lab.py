#!/usr/bin/env python3
"""
build_frr_lab.py
Generate an FRR lab directory:
  - frr/<node>/{daemons,frr.conf,vtysh.conf}
  - .env file compatible with a shared docker-compose.base.yml

Example:
  python3 build_frr_lab.py \
    --lab labs/lab1 \
    --subnet 172.20.0.0/24 \
    --spines 1 \
    --leafs 2 \
    --write-env
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import subprocess
from pathlib import Path
from typing import List


DAEMONS = """\
zebra=yes
bgpd=yes
staticd=yes
mgmtd=yes
"""

VTYSH = """\
# vtysh.conf
"""

FRR_HEADER = """\
frr defaults traditional
hostname {hostname}
service integrated-vtysh-config
!
"""

FRR_FOOTER = """\
!
line vty
!
"""


def router_id(ip: ipaddress.IPv4Address) -> str:
    return f"1.1.1.{ip.packed[-1]}"


def _extract_used_subnets_from_ipam(ipam_config) -> List[ipaddress.IPv4Network]: # noqa
    used: List[ipaddress.IPv4Network] = []
    for cfg in ipam_config:
        subnet = cfg.get("Subnet")
        if not subnet:
            continue
        try:
            n = ipaddress.ip_network(subnet, strict=False)
            if isinstance(n, ipaddress.IPv4Network):
                used.append(n)
        except ValueError:
            pass
    return used


def _docker_used_subnets() -> List[ipaddress.IPv4Network]:
    """
    Returns IPv4 subnets currently used by Docker networks (best-effort).
    Requires docker CLI access.
    """
    try:
        cmd = ["docker", "network", "ls", "-q"]
        net_ids = subprocess.check_output(cmd, text=True).split()
        if not net_ids:
            return []
        raw = subprocess.check_output(
            ["docker", "network", "inspect", *net_ids],
            text=True
        )
        data = json.loads(raw)
    except Exception:
        # If Docker isn't available, fall back to "no known subnets"
        return []

    used: List[ipaddress.IPv4Network] = []
    for net in data:
        ipam = (net.get("IPAM") or {}).get("Config") or []
        used.extend(_extract_used_subnets_from_ipam(ipam))
    return used


def _overlaps_any(
    candidate: ipaddress.IPv4Network,
    used: List[ipaddress.IPv4Network],
) -> bool:
    return any(candidate.overlaps(u) for u in used)


def _auto_pick_subnet() -> ipaddress.IPv4Network:
    """
    Pick the first free /24 from 172.31.1.0/24..172.31.254.0/24 that doesn't
    overlap Docker networks.
    """
    used = _docker_used_subnets()

    for x in range(1, 255):
        cand = ipaddress.ip_network(f"172.31.{x}.0/24", strict=False)
        if not _overlaps_any(cand, used):
            return cand

    raise RuntimeError(
        "Unable to find a free /24 in 172.31.0.0/16 (1..254). "
        "Try specifying --subnet."
    )


def _compose_header() -> str:
    return """\
x-frr-node: &frr_node
  image: quay.io/frrouting/frr:9.1.0
  privileged: true
  entrypoint:
    - /bin/sh
    - -lc
    - |
      mkdir -p /var/run/frr
      chown -R frr:frr /etc/frr /var/run/frr || true
      /usr/lib/frr/docker-start
      tail -f /dev/null

services:
"""


def _compose_service_block(node_name: str) -> str:
    var_ip = f"{node_name.upper()}_IP"
    return f"""\
  {node_name}:
    <<: *frr_node
    container_name: ${{LAB_NAME}}-{node_name}
    hostname: {node_name}
    volumes:
      - ${{FRR_DIR}}/{node_name}:/etc/frr
    networks:
      fabric:
        ipv4_address: ${{{var_ip}}}

"""


def _compose_footer() -> str:
    return """\
networks:
  fabric:
    driver: bridge
    ipam:
      config:
        - subnet: ${FABRIC_SUBNET}
"""


def _render_compose(spines, leafs) -> str:
    out = [_compose_header()]
    for name, _, _ in spines + leafs:
        out.append(_compose_service_block(name))
    out.append(_compose_footer())
    return "".join(out)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--lab", required=True, help="Lab directory (e.g. labs/lab1)"
    )
    p.add_argument(
        "--subnet",
        default=None,
        help="Optional. If omitted, auto-pick a free /24 subnet."
    )
    p.add_argument("--spines", type=int, default=1)
    p.add_argument("--leafs", type=int, default=2)
    p.add_argument("--spine-as", type=int, default=65000)
    p.add_argument("--leaf-as-start", type=int, default=65101)
    p.add_argument("--ip-offset", type=int, default=11)
    p.add_argument("--write-env", action="store_true")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    lab = Path(args.lab).expanduser().resolve()
    if lab.exists() and any(lab.iterdir()) and not args.force:
        raise SystemExit(
            f"Lab directory '{lab}' already exists and is not empty. "
            "Use --force to overwrite."
        )

    frr_root = lab / "frr"
    lab.mkdir(parents=True, exist_ok=True)
    frr_root.mkdir(exist_ok=True)

    if args.subnet:
        subnet = ipaddress.ip_network(args.subnet, strict=False)
    else:
        subnet = _auto_pick_subnet()
        print(f"[auto] Selected free subnet: {subnet.with_prefixlen}")

    hosts = list(subnet.hosts())
    idx = args.ip_offset - 1

    spines = []
    leafs = []

    for i in range(args.spines):
        ip = hosts[idx + i]
        spines.append(("spine" + str(i + 1), ip, args.spine_as))

    for i in range(args.leafs):
        ip = hosts[idx + args.spines + i]
        leafs.append(("leaf" + str(i + 1), ip, args.leaf_as_start + i))

    # Write FRR trees
    for name, ip, asn in spines + leafs:
        node = frr_root / name
        node.mkdir(parents=True, exist_ok=True)

        (node / "daemons").write_text(DAEMONS)
        (node / "vtysh.conf").write_text(VTYSH)

        if name.startswith("spine"):
            neighbors = "\n".join(
                f" neighbor {lip} remote-as {lasn}"
                for _, lip, lasn in leafs
            )
            activates = "\n".join(
                f"  neighbor {lip} activate" for _, lip, _ in leafs
            )
        else:
            spine_ip = spines[0][1]
            neighbors = f" neighbor {spine_ip} remote-as {args.spine_as}"
            activates = f"  neighbor {spine_ip} activate"

        frr_conf = (
            FRR_HEADER.format(hostname=name)
            + f"router bgp {asn}\n"
            + f" bgp router-id {router_id(ip)}\n"
            + neighbors + "\n"
            + " !\n"
            + " address-family ipv4 unicast\n"
            + activates + "\n"
            + " exit-address-family\n"
            + FRR_FOOTER
        )

        (node / "frr.conf").write_text(frr_conf)

    # Always generate per-lab docker-compose.yml
    compose_path = lab / "docker-compose.yml"
    if compose_path.exists() and not args.force:
        raise SystemExit(
            f"{compose_path} already exists. Re-run with --force to overwrite."
        )

    compose_text = _render_compose(spines, leafs)
    compose_path.write_text(compose_text)
    print(f"Generated compose: {compose_path}")

    # Optional .env
    if args.write_env:
        # FRR_DIR must be relative to where docker compose is run (repo root)
        # args.lab is already the correct relative path (e.g. labs/lab1)
        frr_dir = f"./{Path(args.lab).as_posix()}/frr"

        env = [
            f"COMPOSE_PROJECT_NAME={lab.name}",
            f"LAB_NAME={lab.name}",
            f"FRR_DIR={frr_dir}",
            f"FABRIC_SUBNET={subnet.with_prefixlen}",
        ]
        for name, ip, _ in spines + leafs:
            env.append(f"{name.upper()}_IP={ip}")

        (lab / ".env").write_text("\n".join(env) + "\n")

    print(f"Lab created: {lab}")
    print("Nodes:")
    for n, ip, asn in spines + leafs:
        print(f"  - {n:6} {ip} AS{asn}")
    if args.write_env:
        print("Generated .env (use with docker-compose.base.yml)")


if __name__ == "__main__":
    main()
