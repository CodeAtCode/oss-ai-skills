# Testing with Redroid & Waydroid

> This reference file is loaded on demand from ../SKILL.md.

## Redroid: Android in Docker

### What Is Redroid?

Redroid (Remote-android) runs full Android inside Docker container using LXC primitives on host Linux kernel.

**Key characteristics**:
- Runs as Docker container — fully containerized, reproducible, scriptable
- Root by default (uid=0 inside container)
- ADB access via TCP on port 5555
- No display by default (headless) — use scrcpy for screen mirroring
- Supports Android 11 through 15
- Perfect for CI/CD, batch testing, automated APK validation

**Resources**:
- Docs: https://github.com/remote-android/redroid-doc
- Docker Hub: https://hub.docker.com/r/redroid/redroid

### Prerequisites & Kernel Setup

```bash
# Install Docker
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER

# Install binder kernel module
sudo apt install linux-modules-extra-$(uname -r)

# Load binder module
sudo modprobe binder_linux

# Verify binder available
ls /dev/binderfs 2>/dev/null && echo "OK" || echo "MISSING"

# For Android 11: also load ashmem
sudo modprobe ashmem_linux
```

**Kernel requirement**: 4.14+

**WSL2**: Requires custom WSL2 kernel with binder modules. See https://github.com/remote-android/redroid-doc/blob/master/deploy/wsl.md

**macOS**: NOT directly supported (Docker Desktop lacks binder)

### Basic Docker Setup

**Minimal headless container**:
```bash
docker run -d --privileged --name redroid14 -p 5555:5555 redroid/redroid:14.0.0-latest
```

**With GPU acceleration**:
```bash
docker run -d --privileged --name redroid14 -p 5555:5555 \
    -v /dev/dri:/dev/dri \
    redroid/redroid:14.0.0-latest \
    androidboot.redroid_width=1080 \
    androidboot.redroid_height=1920 \
    androidboot.redroid_dpi=320
```

**With persistent data**:
```bash
docker volume create redroid_data

docker run -d --privileged --name redroid14 -p 5555:5555 \
    -v /dev/dri:/dev/dri -v redroid_data:/data \
    redroid/redroid:14.0.0-latest \
    androidboot.redroid_width=1080 \
    androidboot.redroid_height=1920 \
    androidboot.redroid_dpi=320
```

**Docker Compose**:
```yaml
# docker-compose.yml
services:
  redroid:
    image: redroid/redroid:14.0.0-latest
    container_name: redroid14
    privileged: true
    ports:
      - "5555:5555"
    volumes:
      - /dev/dri:/dev/dri
      - redroid_data:/data
    command:
      - "androidboot.redroid_width=1080"
      - "androidboot.redroid_height=1920"
      - "androidboot.redroid_dpi=320"

volumes:
  redroid_data:
```

```bash
docker compose up -d      # Start
docker compose logs -f    # View boot logs (wait for "Boot completed")
docker compose down       # Stop
```

### Available Docker Image Tags

| Tag | Android | Notes |
|---|---|---|
| `redroid/redroid:11.0.0-latest` | 11 | Stable, legacy |
| `redroid/redroid:12.0.0-latest` | 12 | Stable |
| `redroid/redroid:13.0.0-latest` | 13 | Stable |
| `redroid/redroid:14.0.0-latest` | 14 | **Recommended** |
| `redroid/redroid:15.0.0-latest` | 15 | Newer, check stability |
| `redroid/redroid:14.0.0_64only-latest` | 14 | 64-bit only (smaller) |
| `erstt/redroid` | Various | Pre-built with ARM translation |

### ADB Connection & APK Installation

```bash
# Wait for boot
docker logs redroid14 2>&1 | tail -5

# Connect ADB
adb connect localhost:5555
adb devices
# Expected: localhost:5555    device

# Install patched APK
adb -s localhost:5555 install rebuilt_aligned.apk
adb -s localhost:5555 install -r rebuilt_aligned.apk  # Reinstall
adb -s localhost:5555 install -d -t --force-install rebuilt_aligned.apk  # Force

# Install split APKs
adb -s localhost:5555 install-multiple base_aligned.apk \
    split_config.arm64_v8a_aligned.apk \
    split_config.xxhdpi_aligned.apk

# Grant all runtime permissions
adb -s localhost:5555 install -r -g rebuilt_aligned.apk

# App management
adb -s localhost:5555 shell pm list packages          # List all
adb -s localhost:5555 shell pm list packages -3       # Third-party only
adb -s localhost:5555 uninstall com.example.app        # Remove
adb -s localhost:5555 shell am force-stop com.example.app  # Force stop
adb -s localhost:5555 shell am start -n com.example.app/.MainActivity  # Launch

# Root shell (redroid is root by default!)
adb -s localhost:5555 shell
whoami   # root
id       # uid=0(root) gid=0(root)

# Screen mirroring
scrcpy -s localhost:5555
```

### GApps, Magisk & ARM Translation

All three via [redroid-script](https://github.com/abing7k/redroid-script):

```bash
git clone https://github.com/abing7k/redroid-script.git
cd redroid-script

# Everything at once
sudo python3 redroid-script.py redroid14 --gapps --magisk --libndk

# Individually
sudo python3 redroid-script.py redroid14 --gapps    # OpenGApps
sudo python3 redroid-script.py redroid14 --magisk   # Magisk
sudo python3 redroid-script.py redroid14 --libndk   # ARM translation
sudo python3 redroid-script.py redroid14 --houdini  # Intel Houdini

# Restart after installation
docker restart redroid14
```

**Note**: Magisk may require 2-3 container restarts to fully initialize.

### Complete Redroid APK Testing Workflow

```bash
# === One-time setup ===
sudo modprobe binder_linux
docker volume create redroid_data
docker run -d --privileged --name redroid14 -p 5555:5555 \
    -v redroid_data:/data redroid/redroid:14.0.0-latest
# Wait ~30s for boot
adb connect localhost:5555

# === GApps + ARM translation (optional) ===
git clone https://github.com/abing7k/redroid-script.git
sudo python3 redroid-script.py redroid14 --gapps --libndk
docker restart redroid14
sleep 30
adb connect localhost:5555

# === Per-APK test cycle ===
# 1. Decompile, modify, recompile
apktool d target.apk -o dec/ -f
# ... modifications ...
apktool b dec/ -o rebuilt.apk

# 2. Sign
zipalign -v -p 4 rebuilt.apk rebuilt_aligned.apk
apksigner sign --ks ~/apk-testing.keystore \
    --ks-key-alias testing --ks-pass pass:your_password \
    --key-pass pass:your_password rebuilt_aligned.apk

# 3. Uninstall previous
adb -s localhost:5555 uninstall com.example.app 2>/dev/null

# 4. Install
adb -s localhost:5555 install rebuilt_aligned.apk

# 5. Launch and check logs
adb -s localhost:5555 shell am start -n com.example.app/.MainActivity
adb -s localhost:5555 logcat -s "AndroidRuntime:E" "*:S"

# 6. Screen mirror if needed
scrcpy -s localhost:5555

# === Cleanup ===
docker stop redroid14
docker rm redroid14
docker volume rm redroid_data
```

### Redroid Known Issues

| Issue | Workaround |
|---|---|
| Container won't start (binder missing) | `sudo modprobe binder_linux` + `linux-modules-extra-$(uname -r)` |
| Apps can't access internet | Use `--net=host` in docker run |
| Long first boot on WSL2 | Store data as Docker volume (not bind mount) |
| ARM app crashes on x86 host | Install ARM translation: `redroid-script.py <id> --libndk` |
| No audio output | Expected in headless mode |
| Magisk instability | Restart container 2-3 times |
| GPU artifacts on NVIDIA | Remove `-v /dev/dri:/dev/dri` |

---

## Waydroid: Testing Patched APKs

> General Waydroid usage — installation, initialization, CLI, GPU support, networking, window modes, troubleshooting — lives in the dedicated `waydroid` skill (`tool/waydroid/SKILL.md`). This section only covers what is specific to testing patched APKs.

Waydroid runs Android as an LXC container with native desktop window integration. Unlike redroid, apps appear as regular desktop windows, clipboard and audio are shared with the host, and it requires a Wayland compositor.

### GApps, Magisk & ARM Translation via waydroid_script

[casualsnek/waydroid_script](https://github.com/casualsnek/waydroid_script):

```bash
git clone https://github.com/casualsnek/waydroid_script.git
cd waydroid_script
sudo pip3 install requests pyyaml

# Install everything
sudo python3 waydroid_script.py -g -m -l
# -g = GApps (OpenGApps)
# -m = Magisk
# -l = libndk_translation (ARM)

# Minimal GApps, or MicroG instead of OpenGApps
sudo python3 waydroid_script.py -g --variant pico
sudo python3 waydroid_script.py -g --microg

# Restart after installation
waydroid session stop
sudo systemctl restart waydroid-container
waydroid session start && waydroid show-full-ui
```

**ARM translation requirement**: CPU must support SSE 4.2 (`grep sse4_2 /proc/cpuinfo` — empty output means unsupported).

### Per-APK Test Cycle

```bash
# Sign the rebuilt APK first (see SKILL.md → Signing)
waydroid app remove com.example.app 2>/dev/null   # Uninstall previous
waydroid app install rebuilt_aligned.apk          # Install patched APK
waydroid app launch com.example.app               # Launch
adb logcat -s "AndroidRuntime:E" "*:S"            # Check for crashes

# Split APKs must go through ADB
adb install-multiple base.apk split_config.arm64_v8a.apk
```

**NVIDIA note**: Waydroid relies on Mesa/GBM — on NVIDIA proprietary drivers use `WAYDROID_DISABLE_GPU=1 waydroid session start` or switch to the iGPU. Full GPU troubleshooting in the dedicated `waydroid` skill.