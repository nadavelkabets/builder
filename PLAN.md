# Builder Implementation Plan

## Executive Summary

Builder is a deployment utility for embedded Linux projects (Jetson and Raspberry Pi) that automates rootfs preparation and bundle creation. This plan outlines the architecture, technology choices, and implementation phases.

---

## 1. Software Architecture

### 1.1 High-Level Architecture

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│              │     │               │     │              │
│  CLI Layer   ├────►│  Core Engine  ├────►│ Output Layer │
│   (click)    │     │               │     │              │
└──────────────┘     └───────┬───────┘     └──────────────┘
                             │
               ┌─────────────┼─────────────┐
               │             │             │
         ┌─────▼────┐  ┌─────▼────┐  ┌─────▼────┐
         │  Config  │  │Component │  │ Package  │
         │  Parser  │  │ Handlers │  │ Builder  │
         └──────────┘  └──────────┘  └──────────┘
```

### 1.2 Module Structure

```
builder/
├── __init__.py              # Package initialization, version
├── __main__.py              # Entry point: python -m builder
├── cli.py                   # CLI argument parsing and command dispatch
├── config/
│   ├── __init__.py
│   ├── loader.py            # YAML loading with !include and !ENV support
│   ├── schema.py            # Pydantic models for configuration validation
│   └── env.py               # Custom !ENV tag implementation
├── components/
│   ├── __init__.py
│   ├── base.py              # Abstract base component class
│   ├── docker_compose.py    # Docker Compose component handler
│   ├── systemd.py           # Systemd service component handler
│   ├── file.py              # File deployment component handler
│   └── directory.py         # Directory deployment component handler
├── builders/
│   ├── __init__.py
│   ├── rootfs.py            # Rootfs preparation (build command)
│   ├── deb.py               # Debian package generation
│   └── bundle.py            # Makeself bundle creation
├── platforms/
│   ├── __init__.py
│   ├── base.py              # Abstract platform class
│   ├── jetson.py            # Jetson-specific handling (BSP, flashing)
│   └── rpi.py               # Raspberry Pi-specific handling
├── utils/
│   ├── __init__.py
│   ├── docker.py            # Docker/Docker-in-Docker operations
│   ├── chroot.py            # Chroot operations for package installation
│   ├── download.py          # URL download with progress
│   ├── git.py               # Git operations for versioning
│   └── shell.py             # Shell command execution wrapper
└── templates/
    ├── deb/
    │   ├── control.j2       # Debian control file template
    │   ├── preinst.j2       # Pre-installation script
    │   ├── postinst.j2      # Post-installation script
    │   ├── prerm.j2         # Pre-removal script
    │   └── postrm.j2        # Post-removal script
    └── scripts/
        ├── flash-jetson.sh.j2   # Jetson flashing script
        └── flash-rpi.sh.j2      # RPi SD card writing script
```

### 1.3 Data Flow

```
1. CLI parses arguments
         │
         ▼
2. Config loader reads YAML
   - Resolves !include directives (pyyaml-include)
   - Expands !ENV variables
   - Validates against Pydantic schema
         │
         ▼
3. Command dispatcher routes to:
   ┌─────────────────┬─────────────────┐
   │  build command  │  bundle command │
   └────────┬────────┴────────┬────────┘
            │                 │
            ▼                 ▼
4a. RootfsBuilder        4b. BundleBuilder
    - Mount Docker vol       - Download rootfs/BSP
    - Process components     - Create temp workdir
    - Generate deb           - Run RootfsBuilder
    - Install to rootfs      - Compress image
                             - Generate flash script
                             - Create makeself bundle
            │                      │
            ▼                      ▼
5. Output: Modified rootfs   Output: .run file
```

---

## 2. Technology Stack

### 2.1 Python vs Bash Decision

**Recommendation: Python with Bash helper scripts**

| Aspect | Python | Bash |
|--------|--------|------|
| YAML processing | Excellent (pyyaml, pyyaml-include) | Poor (requires yq) |
| Error handling | Robust try/except, typed exceptions | Limited |
| Code organization | Modules, classes, clean structure | Unwieldy at scale |
| Testing | pytest, excellent tooling | Difficult |
| Docker SDK | Official docker-py library | CLI only |

**Hybrid Approach:**
- **Python**: Core logic, configuration parsing, orchestration
- **Bash**: Flash scripts embedded in bundles (must run standalone)

### 2.2 Python Version

- **Minimum**: Python 3.10 (pattern matching, better typing)
- **Recommended**: Python 3.11+

---

## 3. Key Libraries

### 3.1 Dependencies

```toml
# pyproject.toml
dependencies = [
    # Core
    "pyyaml>=6.0",
    "pyyaml-include>=2.0",    # !include directive with flatten
    "pydantic>=2.0",          # Config validation
    "docker>=7.0.0",          # Docker SDK
    "jinja2>=3.0",            # Template engine

    # Utilities
    "rich>=13.0",             # Terminal output, progress bars
    "httpx>=0.25",            # HTTP downloads
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "ruff>=0.1",
]
```

### 3.2 Custom !ENV Tag Implementation

```python
# builder/config/env.py
import os
import re
import yaml

class EnvVarLoader(yaml.SafeLoader):
    pass

def env_constructor(loader, node):
    """
    Handle !ENV tag for environment variable substitution.

    Supports:
      !ENV VARNAME              # Required variable
      !ENV ${VARNAME}           # Required variable (explicit)
      !ENV ${VARNAME:default}   # With default value
    """
    value = loader.construct_scalar(node)
    pattern = r'\$\{([^}:]+)(?::([^}]*))?\}|(\w+)'
    match = re.match(pattern, value)

    if match:
        var_name = match.group(1) or match.group(3)
        default = match.group(2)

        result = os.environ.get(var_name)
        if result is None:
            if default is not None:
                return default
            raise ValueError(f"Environment variable '{var_name}' not set")
        return result
    return value

EnvVarLoader.add_constructor('!ENV', env_constructor)
```

### 3.3 Configuration Schema

```python
# builder/config/schema.py
from pydantic import BaseModel, Field
from typing import Literal, Union
from pathlib import Path

class DockerComposeComponent(BaseModel):
    type: Literal['docker-compose']
    path: Path
    target: Path
    operation: Literal['build', 'pull']
    services: list[str]

class SystemdComponent(BaseModel):
    type: Literal['systemd']
    service: Path
    enable: bool = True

class FileComponent(BaseModel):
    type: Literal['file']
    source: Path
    target: Path
    chmod: str | int = '644'
    chown: str = 'root:root'

class DirectoryComponent(BaseModel):
    type: Literal['directory']
    source: Path
    target: Path
    chmod: str | int = '755'
    chown: str = 'root:root'

Component = Union[
    DockerComposeComponent,
    SystemdComponent,
    FileComponent,
    DirectoryComponent
]

class BuilderConfig(BaseModel):
    depends: list[str] = Field(default_factory=list)
    components: list[Component]
```

---

## 4. Project File Structure

```
builder/
├── pyproject.toml
├── README.md
├── PLAN.md
├── LICENSE
├── .gitignore
│
├── src/
│   └── builder/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config/
│       ├── components/
│       ├── builders/
│       ├── platforms/
│       ├── utils/
│       └── templates/
│
├── tests/
│   ├── conftest.py
│   ├── test_config/
│   ├── test_components/
│   ├── test_builders/
│   └── fixtures/
│
└── examples/
    ├── jetson/
    └── rpi/
```

---

## 5. Implementation Phases

### Phase 1: Foundation
- Initialize project structure with pyproject.toml
- Implement !ENV custom YAML tag
- Implement config loader with !include support
- Define Pydantic schemas for all component types
- Create CLI with click

### Phase 2: Component Handlers
- Create abstract base component handler
- Implement FileComponent handler
- Implement DirectoryComponent handler
- Implement SystemdComponent handler
- Implement DockerComposeComponent handler

### Phase 3: Docker and Chroot
- Implement Docker manager with DinD support
- Add docker-compose build/pull operations
- Implement chroot execution wrapper
- Add package installation via chroot

### Phase 4: Deb Package Generation
- Create Jinja2 templates for DEBIAN files
- Implement control file generation
- Implement maintainer scripts (preinst, postinst, prerm, postrm)
- Add dpkg-deb build invocation
- Implement version detection from git

### Phase 5: Build Command
- Implement RootfsBuilder orchestrator
- Wire up component processing pipeline
- Add deb installation to rootfs
- Add progress reporting with Rich

### Phase 6: Platform Support
- Create abstract Platform base class
- Implement JetsonPlatform (BSP handling, flash script)
- Implement RaspberryPiPlatform (img handling, flash script)
- Add URL download utility

### Phase 7: Bundle Command
- Implement BundleBuilder orchestrator
- Add temporary workdir management
- Implement image compression
- Add makeself bundle creation
- Add output naming conventions

### Phase 8: Polish
- Comprehensive error messages
- Logging
- Example configurations
- CI/CD setup

---

## 6. Execution Environment

### 6.1 Docker-in-Docker with Custom data-root

Builder requires a specialized execution environment to pre-load Docker images into the rootfs during build time (not first boot). This is achieved using Docker-in-Docker with a custom `data-root` configuration.

#### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  ubuntu-dind container (x86_64)                             │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ dockerd                                                │ │
│  │   data-root: /rootfs/var/lib/docker                    │ │
│  │                                                        │ │
│  │ daemon.json:                                           │ │
│  │ {                                                      │ │
│  │   "data-root": "/rootfs/var/lib/docker"                │ │
│  │ }                                                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                  │
│                          ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ /rootfs (mounted rootfs volume)                        │ │
│  │                                                        │ │
│  │   /var/lib/docker/     ← Image layers extracted here   │ │
│  │   /var/run/docker.sock ← Bind mount from host DinD     │ │
│  │                                                        │ │
│  │   chroot + qemu-aarch64 (for ARM rootfs)               │ │
│  │   └── docker CLI uses x86 daemon via socket            │ │
│  │       (10x faster than QEMU-emulated extraction)       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### Why This Approach?

| Alternative | Problem |
|-------------|---------|
| Load images on first boot | Slow boot, requires extra disk space for tarballs |
| Rootless Docker | Requires user namespaces, not available in most CI |
| containerd direct write | Experimental, requires Docker's containerd image store |
| skopeo to overlay2 | Docker's storage format is internal, unsupported |

#### Setup Steps

1. **Start ubuntu-dind container** matching rootfs Ubuntu version:
   ```bash
   docker run --privileged -v /path/to/rootfs:/rootfs \
     -v /path/to/daemon.json:/etc/docker/daemon.json \
     cruizba/ubuntu-dind:latest
   ```

2. **daemon.json configuration**:
   ```json
   {
     "data-root": "/rootfs/var/lib/docker"
   }
   ```

3. **Before chroot, bind mount the socket**:
   ```bash
   mount --bind /var/run/docker.sock /rootfs/var/run/docker.sock
   ```

4. **Docker commands in chroot use x86 daemon**:
   ```bash
   chroot /rootfs docker pull myimage:tag
   # Layers extracted by x86 dockerd, not QEMU-emulated ARM
   ```

### 6.2 CI Environment Requirements

**⚠️ Privileged access required** - Standard SaaS CI runners do not support this workflow.

| CI Platform | Supported Configuration |
|-------------|------------------------|
| GitHub Actions | Self-hosted runners with Docker privileged access |
| GitLab CI | Self-managed runners with `privileged = true` |
| Jenkins | Agents with Docker socket access |
| CircleCI | Machine executors (not Docker executors) |

#### Example GitLab CI Configuration

```yaml
# .gitlab-ci.yml
build:
  image: cruizba/ubuntu-dind:22.04
  services:
    - docker:dind
  variables:
    DOCKER_HOST: tcp://docker:2375
  script:
    - builder build --rootfs /rootfs --config builder.yaml --name myapp
  tags:
    - privileged  # Requires runner with privileged = true
```

---

## 7. Critical Considerations

### 7.1 Security

| Concern | Mitigation |
|---------|------------|
| Privileged containers | Use only in controlled CI environments |
| Root privileges | Document clearly; consider fakeroot for deb building |
| Chroot execution | Validate all paths; prevent directory traversal |
| Shell injection | Use subprocess with list args, never shell=True with user input |
| Environment variables | Never log values of !ENV expansions |
| Downloads | Use HTTPS only; verify checksums when available |

### 7.2 Error Handling

```python
# builder/exceptions.py
class BuilderError(Exception):
    """Base exception for builder errors."""
    pass

class ConfigError(BuilderError):
    """Configuration loading or validation error."""
    pass

class ComponentError(BuilderError):
    """Component processing error."""
    pass

class DockerError(BuilderError):
    """Docker operation error."""
    pass
```

### 7.3 Upgrade Flow (Layer Cache Optimization)

```bash
# In postinst script:
# 1. Pull new images first (benefits from layer cache)
docker compose -f /opt/app/docker-compose.yaml pull

# 2. Stop and remove old containers
docker compose -f /opt/app/docker-compose.yaml down --remove-orphans

# 3. Start new containers
docker compose -f /opt/app/docker-compose.yaml up -d
```

---

## 8. Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.10+ | YAML processing, Docker SDK, maintainability |
| CLI | click | Clean decorator syntax, better than argparse |
| Config validation | Pydantic v2 | Type safety, great error messages |
| YAML !include | pyyaml-include | Supports glob patterns and flatten |
| Docker integration | DinD + custom data-root | Pre-load images during build, not first boot |
| Docker SDK | docker-py | Official SDK, Pythonic API |
| Deb packaging | dpkg-deb (shell) | Simple, no library needed |
| Makeself | Shell invocation | No wrapper needed |
| Templates | Jinja2 | Industry standard |
| Terminal output | Rich | Beautiful progress bars |
| CI requirement | Privileged runners | No SaaS CI alternative for image pre-loading |
