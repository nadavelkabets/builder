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

Create a YAML configuration file to define your build:

```yaml
# builder.yaml

name: product-bundle
type: deb
arch: arm64

packages:
  - python3
  - python3-pip
  - nginx

docker:
  images:
    # Pull from registry
    - name: redis:alpine

    # Build from local Dockerfile
    - name: my-app:latest
      build:
        context: ./app
        dockerfile: Dockerfile

components:
  - type: service
    systemd: path/to/systemd.service
    enable: true

  - type: copy
    chmod: 775
    chown: root
    files:
      - name: start_script
        source: ./path/to/script.sh
        target: /bin
        chmod: u+x
```

### Including Other Configuration Files

Use the `!INCLUDE` tag to include other YAML files:

```yaml
# builder.yaml

name: product-bundle
type: deb
arch: arm64

packages: !INCLUDE packages.yaml
docker: !INCLUDE docker.yaml
components: !INCLUDE components.yaml
```

## Usage

```bash
builder <rootfs-path> <config-path>
```

### Arguments

| Argument | Description |
|----------|-------------|
| `rootfs-path` | Path to the mounted rootfs directory |
| `config-path` | Path to the YAML configuration file |

### Examples

**Jetson device:**
```bash
builder /mnt/jetson-rootfs ./jetson-config.yaml
```

**Raspberry Pi:**
```bash
builder /media/user/rootfs ./rpi-config.yaml
```

## Makeself Bundle Output

Builder can generate self-extracting makeself bundles for easy deployment:

### Jetson

Generates a makeself bundle containing:
- Compressed rootfs tarball
- NVIDIA flashing script for Jetson devices

```bash
builder --output-bundle jetson /mnt/jetson-rootfs ./config.yaml
```

### Raspberry Pi

Generates a makeself bundle containing:
- Compressed `.img` file
- SD card flashing script

```bash
builder --output-bundle rpi /mnt/rpi-rootfs ./config.yaml
```

## Requirements

- Docker with Docker-in-Docker support
- Root privileges (for chroot operations)
- Target rootfs mounted and accessible
- makeself (for bundle generation)

## License

MIT
