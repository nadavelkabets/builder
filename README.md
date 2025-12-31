# builder

A deployment utility for embedded Linux projects that simplifies dependency management and image bundling for Jetson and Raspberry Pi devices.

## Overview

Builder streamlines the process of preparing embedded Linux rootfs images by automating:

- **Docker Compose deployment** - Build or pull Docker images and deploy multi-container applications via compose files
- **Package installation** - Install system packages into the rootfs via chroot
- **Component deployment** - Install systemd services, copy files with proper permissions
- **Flashable bundle creation** - Generate self-extracting makeself bundles ready for deployment
- **Unified package management** - All components wrapped in deb packages for clean installation, upgrade, and removal

## How It Works

Builder uses two main techniques to prepare your embedded Linux rootfs:

1. **Docker-in-Docker with Volume Mounting**: Docker images are built or pulled and then loaded into the target system by mounting the rootfs's `/var/lib/docker` directory as a volume. This ensures containers are ready to run on first boot.

2. **Chroot Package Installation**: System packages are installed directly into the rootfs using chroot, providing a native installation environment without requiring the actual target hardware.

### Package Management Strategy

Builder generates deb packages for all component types to enable proper lifecycle management:

- **Master Package**: A global deb package (`<name>`) that declares dependencies on all component packages. Removing the master package triggers removal of all components, including Docker images and containers.

- **Component Packages**: Each `docker-compose`, `deb`, `service`, and `copy` component generates its own deb package (`<name>-<component>`). These packages handle:
  - **Installation**: Pull/build Docker images, deploy files, enable services
  - **Upgrade**: Update images, migrate configurations
  - **Removal**: Stop containers, remove images, clean up files

Docker Compose packages do not embed image layers. Instead, they pull from the registry or build locally during installation, keeping packages lightweight.

## Configuration

Create a YAML configuration file to define your build. The root level supports four component types: `docker-compose`, `deb`, `service`, and `copy`.

```yaml
# builder.yaml

name: product-bundle
version: 1.0.0  # Optional: defaults to git tag if available

components:
  # Docker Compose components - deploy multi-container applications
  # Generates: product-bundle-app-stack deb package (version 1.0.0)
  - type: docker-compose
    name: app-stack
    version: 1.0.0
    path: ./compose/backend.yaml
    target: /opt/myapp
    operation: build
    services:
      - api
      - worker
      - scheduler
    packages:
      - curl
      - jq

  # Generates: product-bundle-monitoring deb package (version 2.1.0)
  - type: docker-compose
    name: monitoring
    version: 2.1.0
    path: ./compose/monitoring.yaml
    target: /opt/monitoring
    operation: pull
    services:
      - prometheus
      - grafana
      - alertmanager

  # Deb components - install system packages
  # Generates: product-bundle-core deb package (version 1.0.0)
  - type: deb
    name: core
    version: 1.0.0
    packages:
      - python3
      - python3-pip
      - nginx

  # Generates: product-bundle-ssh deb package (version 1.0.0)
  - type: deb
    name: ssh
    version: 1.0.0
    packages:
      - openssh-server

  # Service components - deploy and manage systemd services
  # Generates: product-bundle-app-services deb package (version 1.2.0)
  - type: service
    name: app-services
    version: 1.2.0
    services:
      - systemd: path/to/app.service
        enable: true
      - systemd: path/to/worker.service
        enable: true

  # Generates: product-bundle-sshd deb package (version 1.0.0)
  - type: service
    name: sshd
    version: 1.0.0
    services:
      - systemd: path/to/sshd-custom.service
        enable: false

  # Copy components - deploy files with permissions
  # Generates: product-bundle-scripts deb package (version 1.0.0)
  - type: copy
    name: scripts
    version: 1.0.0
    files:
      - name: start_script
        source: ./scripts/start.sh
        target: /usr/local/bin
        chmod: u+x

  # Generates: product-bundle-configs deb package (version 1.1.0)
  - type: copy
    name: configs
    version: 1.1.0
    files:
      - name: app_config
        source: ./config/app.conf
        target: /etc/myapp
        chmod: 644
        chown: root:root
      - name: sshd_config
        source: ./config/sshd_config
        target: /etc/ssh
        chmod: 600
```

### Generated Package Structure

From the above configuration, builder generates:

```
product-bundle                    # Master package (depends on all below)
├── product-bundle-app-stack      # Docker Compose component
├── product-bundle-monitoring     # Docker Compose component
├── product-bundle-core           # Deb component
├── product-bundle-ssh            # Deb component
├── product-bundle-app-services   # Service component
├── product-bundle-sshd           # Service component
├── product-bundle-scripts        # Copy component
└── product-bundle-configs        # Copy component
```

**Uninstall behavior:**
```bash
# Remove everything
apt remove product-bundle

# Remove only the monitoring stack
apt remove product-bundle-monitoring
```

### Including Other Configuration Files

Use the `!INCLUDE` tag to include other YAML files:

```yaml
# builder.yaml

name: product-bundle

components:
  - !INCLUDE compose-components.yaml
  - !INCLUDE app-deb.yaml
  - !INCLUDE networking-deb.yaml
```

### Environment Variables

Use the `!ENV` tag to reference environment variables in your configuration:

```yaml
# builder.yaml

name: product-bundle

components:
  - type: docker-compose
    name: app
    version: !ENV APP_VERSION
    path: ./compose/app.yaml
    target: !ENV ${INSTALL_DIR:/opt/myapp}  # With default value
    operation: pull
    services:
      - api

  - type: copy
    name: configs
    version: 1.0.0
    files:
      - name: api_config
        source: !ENV CONFIG_PATH
        target: /etc/myapp
```

## Usage

Builder provides two commands: `build` for rootfs preparation and `bundle` for creating flashable packages.

### Build Command

Prepare the rootfs with all configured components:

```bash
builder build --rootfs <path> --config <path>
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `--rootfs` | Path to the mounted rootfs directory |
| `--config` | Path to the YAML configuration file |
| `--version` | Override global package version (optional) |

#### Examples

```bash
# Jetson device
builder build --rootfs /mnt/jetson-rootfs --config ./jetson-config.yaml

# Raspberry Pi
builder build --rootfs /media/user/rootfs --config ./rpi-config.yaml
```

### Bundle Command

Generate a self-extracting makeself bundle for deployment. The build process runs in a temporary directory that is automatically cleaned up after completion.

```bash
builder bundle --rootfs <path-or-url> --config <path> --target <jetson|rpi> --output <path>
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `--rootfs` | Path or URL to the rootfs image (`.img` for RPi, `.tar` for Jetson) |
| `--config` | Path to the YAML configuration file |
| `--target` | Target platform: `jetson` or `rpi` |
| `--output` | Output directory (default: `./bundle`) |
| `--name` | Override output filename (optional, see naming conventions below) |
| `--bsp` | (Jetson only) Path or URL to the NVIDIA JetPack BSP |
| `--workdir` | Optional custom working directory (default: tmpdir, auto-cleaned) |
| `--version` | Override global package version (optional) |

#### Output Naming Conventions

By default, the output filename is automatically generated based on git state:

**Tagged release:**
```
<bundle-name>-<version>.run
```
Example: `product-bundle-1.0.0.run`

**Development build (no tag):**
```
<bundle-name>-<dd/mm/yyyy>-<branch-name>-<commit-hash>.run
```
Example: `product-bundle-31/12/2025-feature-auth-a1b2c.run`

Use `--name` to override the auto-generated filename.

#### Jetson Bundle

Generates a makeself bundle containing:
- Compressed rootfs tarball
- NVIDIA flashing script for Jetson devices

Requires the rootfs tar and JetPack BSP:

```bash
# Uses default output: ./bundle/product-bundle-<version>.run
builder bundle \
  --rootfs ./jetson-rootfs.tar \
  --bsp ./jetpack-bsp.tar \
  --config ./config.yaml \
  --target jetson

# Custom output directory
builder bundle \
  --rootfs ./jetson-rootfs.tar \
  --bsp ./jetpack-bsp.tar \
  --config ./config.yaml \
  --target jetson \
  --output ./dist

# Using URLs with custom filename
builder bundle \
  --rootfs https://example.com/jetson-rootfs.tar \
  --bsp https://example.com/jetpack-bsp.tar \
  --config ./config.yaml \
  --target jetson \
  --name my-custom-bundle.run
```

#### Raspberry Pi Bundle

Generates a makeself bundle containing:
- Compressed `.img` file
- SD card flashing script

```bash
# Uses default output: ./bundle/product-bundle-<version>.run
builder bundle \
  --rootfs ./raspios.img \
  --config ./config.yaml \
  --target rpi

# Custom output directory
builder bundle \
  --rootfs ./raspios.img \
  --config ./config.yaml \
  --target rpi \
  --output ./dist

# Using a URL with custom filename
builder bundle \
  --rootfs https://example.com/raspios.img \
  --config ./config.yaml \
  --target rpi \
  --name my-rpi-bundle.run
```

## Requirements

- Docker with Docker-in-Docker support
- Root privileges (for chroot operations)
- makeself (for bundle generation)
- dpkg-deb (for package generation)

## License

MIT
