# builder

A deployment utility for embedded Linux projects that simplifies dependency management and image bundling for Jetson and Raspberry Pi devices.

## Overview

Builder streamlines the process of preparing embedded Linux rootfs images by automating:

- **Docker Compose deployment** - Build or pull Docker images and deploy multi-container applications via compose files
- **Package installation** - Install system packages into the rootfs via chroot
- **Component deployment** - Install systemd services, deploy files with proper permissions
- **Flashable bundle creation** - Generate self-extracting makeself bundles ready for deployment
- **Unified package management** - All components wrapped in a single deb package for clean installation, upgrade, and removal

## How It Works

Builder uses two main techniques to prepare your embedded Linux rootfs:

1. **Docker-in-Docker with Volume Mounting**: Docker images are built or pulled and then loaded into the target system by mounting the rootfs's `/var/lib/docker` directory as a volume. This ensures containers are ready to run on first boot.

2. **Chroot Package Installation**: System packages are installed directly into the rootfs using chroot, providing a native installation environment without requiring the actual target hardware.

### Package Management Strategy

Builder generates a single deb package containing all components:

- **Installation**: Pull/build Docker images, deploy files, enable services
- **Upgrade**: Pull new images before removing old ones (maximizes layer cache reuse), then migrate configurations
- **Removal**: Stop containers, remove images, clean up files

Docker Compose components do not embed image layers. Instead, they pull from the registry or build locally during installation, keeping packages lightweight.

## Configuration

Create a YAML configuration file to define your build. Components are a flat list with four types: `docker-compose`, `systemd`, `file`, and `directory`.

```yaml
# builder.yaml

# External apt dependencies
depends:
  - docker-ce
  - docker-compose-plugin

components:
  # Docker Compose deployments
  - type: docker-compose
    path: ./compose/backend.yaml
    target: /opt/backend
    operation: build
    services:
      - api
      - worker

  - type: docker-compose
    path: ./compose/cache.yaml
    target: /opt/cache
    operation: pull
    services:
      - redis

  - type: docker-compose
    path: ./compose/monitoring.yaml
    target: /opt/monitoring
    operation: pull
    services:
      - prometheus
      - grafana
      - alertmanager

  # Systemd services
  - type: systemd
    service: ./systemd/backend.service
    enable: true

  - type: systemd
    service: ./systemd/worker.service
    enable: true

  - type: systemd
    service: ./systemd/monitoring.service
    enable: true

  # File deployments
  - type: file
    source: ./config/backend.conf
    target: /etc/myapp/backend.conf
    chmod: 644
    chown: root:root

  - type: file
    source: ./scripts/start.sh
    target: /usr/local/bin/start.sh
    chmod: u+x

  - type: file
    source: ./config/sshd_config
    target: /etc/ssh/sshd_config
    chmod: 600

  # Directory deployments
  - type: directory
    source: ./config/myapp
    target: /etc/myapp
    chmod: 755
    chown: root:root
```

### Including Other Configuration Files

Use the `!INCLUDE` tag to include other YAML files:

```yaml
# builder.yaml

components:
  - !INCLUDE compose-components.yaml
  - !INCLUDE systemd-components.yaml
  - !INCLUDE file-components.yaml
```

### Environment Variables

Use the `!ENV` tag to reference environment variables in your configuration:

```yaml
# builder.yaml

components:
  - type: docker-compose
    path: ./compose/app.yaml
    target: !ENV ${INSTALL_DIR:/opt/myapp}  # With default value
    operation: pull
    services:
      - api

  - type: file
    source: !ENV CONFIG_PATH
    target: /etc/myapp/config.yaml
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
| `--name` | Bundle name (used for package naming) |

#### Examples

```bash
# Jetson device
builder build --name my-product --rootfs /mnt/jetson-rootfs --config ./config.yaml

# Raspberry Pi
builder build --name my-product --rootfs /media/user/rootfs --config ./config.yaml
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
| `--name` | Bundle name (used for package naming) |
| `--target` | Target platform: `jetson` or `rpi` |
| `--output` | Output directory (default: `./bundle`) |
| `--bsp` | (Jetson only) Path or URL to the NVIDIA JetPack BSP |
| `--workdir` | Optional custom working directory (default: tmpdir, auto-cleaned) |

#### Output Naming Conventions

By default, the output filename is automatically generated based on git state.

**Version Requirements:**

Git tags must be valid Debian package versions (must start with a digit). Invalid tags are rejected:
- `1.0.0` - valid
- `2.1.0-beta` - valid
- `v1.0.0` - invalid (starts with letter)
- `release-1.0` - invalid (starts with letter)

**Tagged release:**
```
<bundle-name>-<version>.run
```
Example: `my-product-1.0.0.run`

**Development build (no tag):**

Development versions always start with the date to ensure proper version ordering:
```
<bundle-name>-<yyyymmdd>-<branch-name>-<commit-hash>-dev.run
```
Example: `my-product-20251231-feature-auth-a1b2c-dev.run`

The date-first format ensures that deb packages sort correctly and newer development builds always have a higher version number.

#### Jetson Bundle

Generates a makeself bundle containing:
- Compressed rootfs tarball
- NVIDIA flashing script for Jetson devices

Requires the rootfs tar and JetPack BSP:

```bash
# Uses default output: ./bundle/my-product-<version>.run
builder bundle \
  --name my-product \
  --rootfs ./jetson-rootfs.tar \
  --bsp ./jetpack-bsp.tar \
  --config ./config.yaml \
  --target jetson

# Custom output directory
builder bundle \
  --name my-product \
  --rootfs ./jetson-rootfs.tar \
  --bsp ./jetpack-bsp.tar \
  --config ./config.yaml \
  --target jetson \
  --output ./dist

# Using URLs
builder bundle \
  --name my-product \
  --rootfs https://example.com/jetson-rootfs.tar \
  --bsp https://example.com/jetpack-bsp.tar \
  --config ./config.yaml \
  --target jetson
```

#### Raspberry Pi Bundle

Generates a makeself bundle containing:
- Compressed `.img` file
- SD card flashing script

```bash
# Uses default output: ./bundle/my-product-<version>.run
builder bundle \
  --name my-product \
  --rootfs ./raspios.img \
  --config ./config.yaml \
  --target rpi

# Custom output directory
builder bundle \
  --name my-product \
  --rootfs ./raspios.img \
  --config ./config.yaml \
  --target rpi \
  --output ./dist

# Using a URL
builder bundle \
  --name my-product \
  --rootfs https://example.com/raspios.img \
  --config ./config.yaml \
  --target rpi
```

### Running the Bundle

Execute the generated makeself bundle with root privileges:

```bash
# Jetson - flashes the device
sudo ./my-product-1.0.0.run

# Raspberry Pi - writes to SD card
sudo ./my-product-1.0.0.run
```

## Requirements

- Docker with Docker-in-Docker support
- Root privileges (for chroot operations)
- makeself (for bundle generation)
- dpkg-deb (for package generation)

<!-- TODO: Consider using fakeroot or debhelper for building deb packages without requiring root privileges -->

## License

MIT
