---
name: waydroid
description: Use when setting up or troubleshooting Waydroid on Linux - installation and initialization, waydroid CLI, GPU and networking setup, GApps and Play certification, ADB integration, file sharing, or desktop environment integration
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - waydroid
    - android
    - container
    - linux
    - wayland
    - android-emulation
    - gapps
    - lineagos
---

# Waydroid

Container-based Android for Linux with native Wayland integration.

## Overview

Waydroid runs Android in a Linux container with near-native performance using namespaces (user, pid, uts, net, mount, ipc).

Key features:
- **Wayland Integration**: Full support for Wayland compositors
- **GPU Acceleration**: Hardware-accelerated graphics
- **Native Performance**: Near-native speed vs emulators
- **LineageOS-based**: Custom Android system images
- **binderfs**: Android IPC mechanism for container-host communication

## Installation

### Ubuntu/Debian

```bash
sudo apt install curl ca-certificates python3-gbinder python3-trio -y
curl https://repo.waydro.id | sudo bash
sudo apt install waydroid -y
```

Supported: focal, jammy, kinetic, lunar, mantic, noble (Ubuntu); bullseye, bookworm, trixie, sid (Debian).

### Fedora

```bash
sudo dnf copr enable aleasto/waydroid
sudo dnf install waydroid
```

For Silverblue/Kinoite: `rpm-ostree install waydroid`

### Arch Linux

```bash
yay -S waydroid
# Or from git:
git clone https://aur.archlinux.org/waydroid.git && cd waydroid && makepkg -si
```

### openSUSE

```bash
sudo zypper addrepo https://download.opensuse.org/repositories/openSUSE:Tools/openSUSE_Tools.repo
sudo zypper install waydroid
```

### Void Linux

```bash
sudo xbps-install -S waydroid
```

## Initialization

### Basic

```bash
sudo waydroid init
```

### With GApps

```bash
sudo waydroid init -s GAPPS
```

### Manual OTA URLs

```bash
sudo waydroid init \
  -s https://ota.waydro.id/system \
  -v https://ota.waydro.id/vendor
```

## Starting Waydroid

### Using systemd (recommended)

```bash
sudo systemctl start waydroid-container.service
sudo systemctl enable waydroid-container.service
waydroid session start
```

### Manual (without systemd)

```bash
sudo waydroid container start
waydroid session start
```

## CLI Commands

### App Management

```bash
waydroid app install /path/to/app.apk
waydroid app list
waydroid app launch com.package.name
waydroid app uninstall com.package.name
```

### Shell Access

```bash
waydroid shell
waydroid shell pm list packages
waydroid shell getprop ro.product.model
waydroid shell su -c "ls -la /sdcard/"
```

### UI Control

```bash
waydroid show-full-ui
waydroid screenshot
waydroid window set <fullscreen|windowed|tablet> [position]
```

### Status and Info

```bash
waydroid status
waydroid log
waydroid log -cat main
waydroid log -cat all
waydroid prop get
waydroid prop get ro.product.model
```

### Container Control

```bash
waydroid session stop
sudo waydroid container stop
sudo waydroid container restart
```

### Configuration

```bash
waydroid config set <property> <value>
waydroid config set ro.orientation.portrait 1
```

## Deep Dives

These reference files contain detailed information loaded on demand:

- **[GPU, Networking, Window Modes](references/gpu-networking.md)** — Architecture, GPU support verification/tuning, network setup, fullscreen/windowed modes
- **[GApps, ADB, File Sharing](references/gapps-adb-files.md)** — GApps installation/certification, ADB integration, internal storage and shared folders
- **[Desktop Integration, Troubleshooting](references/desktop-troubleshooting.md)** — GNOME/Sway/i3 setup, common issues, reset/uninstall procedures
- **[Advanced Configuration](references/advanced-config.md)** — Custom images, HAL config, boot animation, Magisk root

## Best Practices

1. **Use Wayland session**: Required for Waydroid
2. **Keep system updated**: Ensures compatibility
3. **Use GAPPS if needed**: Required for many apps
4. **Check logs first**: `waydroid log` for troubleshooting
5. **Use proper GPU drivers**: Install appropriate drivers
6. **Enable ADB for complex tasks**: More control
7. **Back up data**: Located in `/var/lib/waydroid/`

## References

- **Official Documentation**: https://docs.waydro.id/
- **Waydroid GitHub**: https://github.com/waydroid/waydroid
- **Arch Wiki**: https://wiki.archlinux.org/title/Waydroid
- **OTA Images**: https://ota.waydro.id/
- **LineageOS**: https://lineageos.org/