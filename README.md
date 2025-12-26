# OpenNetOs

**OpenNetOs** is a comprehensive collection of open networking lab environments and tools for experimenting with modern network operating systems, routing protocols, and network telemetry. This project provides Infrastructure-as-Code (IaaC) frameworks for building repeatable, containerized networking labs.

---

## 🎯 Project Overview

OpenNetOs combines multiple approaches to network lab orchestration:

- **Containerlab** - Industry-standard tool for orchestrating container-based networking labs
- **FRR Labs** - Python-based lab generator for Free Range Routing (FRR) experiments

---

## 📁 Project Structure

```
OpenNetOs/
├── containerlabs/
│   ├── containerlab/          # Containerlab tool (git submodule)
│   ├── clab-frr/              # Containerlab topology for FRR
│   └── srl-telemetry-lab/     # Nokia SR Linux streaming telemetry lab
└── labs/                      # Python-based FRR lab builder
    └── build_frr_lab.py       # Lab generator script
```

---

## 🚀 Quick Start

### Prerequisites

**Operating System:**  
macOS or Linux (Docker Desktop supported)

**Required Software:**
- Docker Desktop or Docker Engine
- Docker Compose v2 (`docker compose`)
- Python 3.9+ (for FRR labs)

**Verify Prerequisites:**
```bash
docker version
docker compose version
python3 --version
```

---

## 📦 Components

### 1. FRR Labs (Python-based)

**Location:** `labs/`

A Python-based lab generator that creates repeatable FRR (Free Range Routing) labs using Docker Compose. This framework emphasizes configuration-as-code and mirrors how modern open network operating systems operate.

**Key Features:**
- Lab-as-code framework with Python generation
- Per-lab Docker Compose files
- Configuration files as the source of truth
- Multiple independent labs can run simultaneously
- Automatic subnet selection to avoid conflicts

**Quick Start:**
```bash
# Generate and start a lab
python3 labs/build_frr_lab.py --lab labs/lab1 --spines 1 --leafs 2 --up

# Access a node
docker exec -it lab1-spine1 vtysh -c "show ip bgp summary"

# Stop the lab
docker compose --env-file labs/lab1/.env -f labs/lab1/docker-compose.yml down
```

**Default Topology:**
- **spine1**: ASN 65000, IP 172.20.0.11
- **leaf1**: ASN 65101, IP 172.20.0.12
- **leaf2**: ASN 65102, IP 172.20.0.13

**Documentation:** See [`labs/README.md`](labs/README.md) for detailed usage instructions.

---

### 2. Containerlab

**Location:** `containerlabs/containerlab/`

Containerlab is a powerful tool for orchestrating and managing container-based networking labs. It provides a declarative way to define network topologies using YAML files and supports a wide range of containerized Network Operating Systems.

**Key Features:**
- Infrastructure-as-Code approach with declarative topology definitions
- Support for 50+ network operating systems (Nokia SR Linux, Arista cEOS, Cisco XRd, SONiC, Juniper cRPD, FRR, and more)
- Fast lab deployment and lifecycle management
- Automated TLS certificate provisioning
- Lab catalog with pre-built examples

**Getting Started:**
- Recommend using the Containerlab IDE extension to easily manage labs
- To update the git submodule: 
```bash
git submodule update --remote --merge
git add containerlabs/containerlab
git commit -m "Update containerlab submodule"
```

**Documentation:** See [`containerlabs/containerlab/README.md`](containerlabs/containerlab/README.md) for detailed documentation.

---

### 3. SR Linux Telemetry Lab

**Location:** `containerlabs/srl-telemetry-lab/`

A complete lab demonstrating Nokia SR Linux streaming telemetry with a full observability stack. This lab showcases a Clos fabric topology with SR Linux switches integrated with modern telemetry and logging infrastructure.

**Key Features:**
- Clos fabric topology with SR Linux switches (3 leaves, 2 spines)
- Complete telemetry stack: gnmic, Prometheus, and Grafana
- Real-time telemetry visualization with interactive topology maps
- Modern logging stack: Loki and Promtail for log aggregation
- Traffic generation scripts for testing and validation
- Pre-configured Grafana dashboards with FlowPlugin integration

**Getting Started:**
```bash
cd containerlabs/srl-telemetry-lab
containerlab deploy --reconfigure

# Access services:
# - Grafana: http://localhost:3000 (anonymous access enabled)
# - Prometheus: http://localhost:9090

# Generate traffic between nodes
bash traffic.sh start all

# Stop traffic
bash traffic.sh stop

# Destroy lab
containerlab destroy --cleanup
```

**Topology:**
- **Spines**: spine1, spine2 (IXR-D3L chassis)
- **Leaves**: leaf1, leaf2, leaf3 (IXR-D2 chassis)
- **Clients**: client1, client2, client3 (Linux endpoints)
- **Telemetry Stack**: gnmic, Prometheus, Grafana
- **Logging Stack**: Promtail, Loki

**Documentation:** See [`containerlabs/srl-telemetry-lab/README.md`](containerlabs/srl-telemetry-lab/README.md) for detailed instructions.

---

### 4. Containerlab FRR Topology

**Location:** `containerlabs/clab-frr/`

A containerlab topology definition for running FRR labs using the containerlab orchestration tool.

**Usage:**
```bash
cd containerlabs/clab-frr
containerlab deploy -t topology.clab.yml
```

---

## 🎓 Use Cases

### Labs and Demos
- Validate network features and topologies
- Perform interoperability testing
- Datapath testing
- Rapid demo environments

### Testing and CI
- Single-binary packaging for CI/CD integration
- Code-based lab definitions
- GitLab CI, GitHub Actions compatible

### Telemetry Validation
- Test telemetry stacks with containerized network functions
- Validate monitoring and observability solutions
- Practice with modern network telemetry protocols

### Learning and Training
- Understand open networking principles
- Practice with routing protocols (BGP, OSPF, etc.)
- Learn Infrastructure-as-Code for networking
- Experiment with network operating systems

---

## 🛠️ Installation

### Containerlab

#### macOS or Windows (WSL)

For macOS and Windows (WSL) users, the recommended approach is to use **Dev Containers** in VS Code or other compatible IDEs. This provides a consistent Linux environment with containerlab pre-installed.

**Using VS Code Dev Containers:**

1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) in VS Code
2. Open the `containerlabs/containerlab` directory in VS Code
3. Press `Cmd+Shift+P` (or `F1` on Windows) and select **"Dev Containers: Reopen in Container"**
4. Choose one of the available devcontainer configurations:
   - `docker-in-docker` - Full Docker-in-Docker setup
   - `docker-outside-of-docker` - Uses host Docker socket (recommended)

Containerlab will be automatically installed in the devcontainer environment. You can verify the installation with:
```bash
containerlab version
```

**Note:** The devcontainer configurations are located in `containerlabs/.devcontainer/`

#### Linux

On Linux systems, install containerlab using the official installation script:

```bash
bash -c "$(curl -sL https://containerlab.dev/setup | sudo -E bash -s "all")"
```

This script automatically detects your Linux distribution and installs the appropriate package. For more installation options and details, see the [official containerlab installation documentation](https://containerlab.dev/install).

### FRR Labs

No installation required - just ensure Python 3.9+ and Docker are available.

```bash
# Verify Python
python3 --version

# Install dependencies (if any)
# Currently, the script uses only standard library
```

---

## 📚 Documentation

Each component has its own detailed documentation:

- **Containerlab**: [`containerlabs/containerlab/README.md`](containerlabs/containerlab/README.md) and [containerlab.dev](https://containerlab.dev)
- **FRR Labs**: [`labs/README.md`](labs/README.md)
- **SR Linux Telemetry Lab**: [`containerlabs/srl-telemetry-lab/README.md`](containerlabs/srl-telemetry-lab/README.md)

---

## 🏗️ Architecture Principles

### Infrastructure-as-Code
All labs are defined declaratively using YAML or generated from code, ensuring repeatability and version control.

### Configuration-as-Code
Network device configurations are stored as files, not CLI commands, aligning with modern open NOS practices.

### Container-First
Leverages containerization for fast deployment, easy cleanup, and resource efficiency.

### Multi-Lab Support
Multiple independent labs can run simultaneously with isolated networks and configurations.

---

## 🔧 Common Operations

### Starting a Lab

**FRR Labs (Python):**
```bash
python3 labs/build_frr_lab.py --lab labs/lab1 --spines 1 --leafs 2 --up
```

**Containerlab:**
```bash
containerlab deploy -t <topology>.clab.yml
```

### Accessing Nodes

**Docker Compose labs:**
```bash
docker exec -it <container-name> bash
# For FRR: docker exec -it <container-name> vtysh
```

**Containerlab labs:**
```bash
ssh admin@<node-name>
# Or use containerlab exec
containerlab exec -t <topology>.clab.yml --label <node-name> --cmd "<command>"
```

### Stopping Labs

**FRR Labs:**
```bash
docker compose --env-file labs/lab1/.env -f labs/lab1/docker-compose.yml down
```

**Containerlab:**
```bash
containerlab destroy -t <topology>.clab.yml
```

### Inspecting Lab Status

**Containerlab:**
```bash
containerlab list
containerlab inspect -t <topology>.clab.yml
containerlab graph -t <topology>.clab.yml
```

---

## 🤝 Contributing

This project combines multiple open-source networking tools and lab examples. When contributing:

1. Follow the coding standards of each component
2. Ensure labs are documented and reproducible
3. Test on both macOS and Linux when possible
4. Update relevant README files

---

## 📄 License

See the [LICENSE](LICENSE) file for license information. Individual components may have their own licenses:
- Containerlab: BSD 3-Clause License
- FRR Labs: See component-specific license

---

## 🔗 Related Projects

- [Containerlab](https://github.com/srl-labs/containerlab) - Main containerlab project
- [FRR (Free Range Routing)](https://frrouting.org/) - Open-source routing suite
- [Nokia SR Linux](https://learn.srlinux.dev/) - Network operating system

---

## 📞 Support

For issues and questions:
- Containerlab: [GitHub Issues](https://github.com/srl-labs/containerlab/issues) or [Discord](https://discord.gg/vAyddtaEV9)
- FRR: [FRR Documentation](https://docs.frrouting.org/)
- General project questions: Open an issue in this repository

---

## 🎯 Roadmap

- [ ] Additional lab examples
- [ ] Integration between containerlab and Python-based labs
- [ ] More telemetry stack examples
- [ ] CI/CD examples for automated testing
- [ ] Multi-vendor interoperability labs

---

**Happy Labbing! 🚀**

