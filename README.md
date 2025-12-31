# builder

A deployment utility for embedded Linux projects that simplifies dependency management and image bundling for Jetson and Raspberry Pi devices.

## Overview

Builder streamlines the process of preparing embedded Linux rootfs images by automating:

- **Docker image deployment** - Build or pull Docker images and load them directly into the target rootfs using a Docker-in-Docker approach
- **Package installation** - Install system packages into the rootfs via chroot
- **Component deployment** - Install systemd services, copy files with proper permissions
- **Flashable bundle creation** - Generate self-extracting makeself bundles ready for deployment

## How It Works

Builder uses two main techniques to prepare your embedded Linux rootfs:

1. **Docker-in-Docker with Volume Mounting**: Docker images are built or pulled and then loaded into the target system by mounting the rootfs's `/var/lib/docker` directory as a volume. This ensures containers are ready to run on first boot.

2. **Chroot Package Installation**: System packages are installed directly into the rootfs using chroot, providing a native installation environment without requiring the actual target hardware.

## Configuration

Create a YAML configuration file to define your build. The root level supports two component types: `docker` and `deb`.

```yaml
# builder.yaml

name: product-bundle
arch: arm64

components:
  # Docker components - pull or build container images
  - type: docker
    images:
      - name: redis:alpine
      - name: my-app:latest
        build:
          context: ./app
          dockerfile: Dockerfile

  - type: docker
    images:
      - name: postgres:15

  # Deb components - install packages and deploy files/services
  - type: deb
    packages:
      - python3
      - python3-pip
      - nginx
    services:
      - systemd: path/to/app.service
        enable: true
      - systemd: path/to/worker.service
        enable: true
    files:
      - name: start_script
        source: ./scripts/start.sh
        target: /usr/local/bin
        chmod: u+x
      - name: config
        source: ./config/app.conf
        target: /etc/myapp
        chmod: 644
        chown: root:root

  - type: deb
    packages:
      - openssh-server
    services:
      - systemd: path/to/sshd-custom.service
        enable: false
    files:
      - name: sshd_config
        source: ./config/sshd_config
        target: /etc/ssh
        chmod: 600
```

### Including Other Configuration Files

Use the `!INCLUDE` tag to include other YAML files:

```yaml
# builder.yaml

name: product-bundle
arch: arm64

components:
  - !INCLUDE docker-components.yaml
  - !INCLUDE app-deb.yaml
  - !INCLUDE networking-deb.yaml
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

#### Examples

```bash
# Jetson device
builder build --rootfs /mnt/jetson-rootfs --config ./jetson-config.yaml

# Raspberry Pi
builder build --rootfs /media/user/rootfs --config ./rpi-config.yaml
```

### Bundle Command

Generate a self-extracting makeself bundle for deployment:

```bash
builder bundle --rootfs <path> --config <path> --target <jetson|rpi> --output <path>
```

#### Arguments

| Argument | Description |
|----------|-------------|
| `--rootfs` | Path to the mounted rootfs directory |
| `--config` | Path to the YAML configuration file |
| `--target` | Target platform: `jetson` or `rpi` |
| `--output` | Output path for the generated bundle |

#### Jetson Bundle

Generates a makeself bundle containing:
- Compressed rootfs tarball
- NVIDIA flashing script for Jetson devices

```bash
builder bundle --rootfs /mnt/jetson-rootfs --config ./config.yaml --target jetson --output ./dist/jetson-bundle.run
```

#### Raspberry Pi Bundle

Generates a makeself bundle containing:
- Compressed `.img` file
- SD card flashing script

```bash
builder bundle --rootfs /mnt/rpi-rootfs --config ./config.yaml --target rpi --output ./dist/rpi-bundle.run
```

## Requirements

- Docker with Docker-in-Docker support
- Root privileges (for chroot operations)
- Target rootfs mounted and accessible
- makeself (for bundle generation)

## License

MIT
