# bundle

A deployment utility for embedded Linux projects that simplifies dependency management for Jetson and Raspberry Pi devices.

## Overview

Bundle streamlines the process of preparing embedded Linux rootfs images by automating:

- **Docker image deployment** - Build or pull Docker images and load them directly into the target rootfs using a Docker-in-Docker approach
- **Package installation** - Install system packages into the rootfs via chroot

## How It Works

Bundle uses two main techniques to prepare your embedded Linux rootfs:

1. **Docker-in-Docker with Volume Mounting**: Docker images are built or pulled and then loaded into the target system by mounting the rootfs's `/var/lib/docker` directory as a volume. This ensures containers are ready to run on first boot.

2. **Chroot Package Installation**: System packages are installed directly into the rootfs using chroot, providing a native installation environment without requiring the actual target hardware.

## Configuration

Create a `bundle.yaml` file in your project root to define your dependencies:

```yaml
# bundle.yaml

packages:
  - python3
  - python3-pip
  - nginx
  - openssh-server

docker:
  images:
    # Pull from registry
    - name: redis:alpine

    # Build from local Dockerfile
    - name: my-app:latest
      build:
        context: ./app
        dockerfile: Dockerfile
```

## Usage

```bash
bundle <rootfs-path>
```

### Examples

**Jetson device:**
```bash
bundle /mnt/jetson-rootfs
```

**Raspberry Pi:**
```bash
bundle /media/user/rootfs
```

## Requirements

- Docker with Docker-in-Docker support
- Root privileges (for chroot operations)
- Target rootfs mounted and accessible

## License

MIT
