# Testing Without Physical Device

> This reference file is loaded on demand from ../SKILL.md.

## Emulator Selection Matrix

| Emulator | Root Support | ARM Translation | GApps Support | Best For | Verdict |
|---|---|---|---|---|---|
| **Android Studio AVD** | Magisk via rootAVD | Native ARM / Translated x86 | Google APIs / Play | Dev, security testing | **Best choice** |
| **Genymotion** | Built-in basic root | libhoudini (not default since 3.x) | Manual GApps flash | CI/CD testing | Good for automation |
| **Waydroid** | Magisk via script | libndk_translation (SSE 4.2 required) | Manual via script | Linux desktop apps | Good for Linux users |
| **BlueStacks** | Difficult, no Magisk | Built-in | Pre-installed | Gaming only | **Not recommended** |
| **Nox** | Clunky, unreliable | Built-in | Partial | Gaming/automation | **Not recommended** |

---

## Android Studio AVD Setup

### Creating and Rooting AVD

```bash
# Step 1: Install Android Studio
# Download from https://developer.android.com/studio

# Step 2: Create AVD
# Android Studio → Tools → Device Manager → Create Device
# Recommended:
# - Device: Pixel 7 (or recent phone profile)
# - System Image: API 35 (Android 15), x86_64 (speed) OR ARM64 (native libs)
# - RAM: 4096 MB minimum (8192 MB preferred)
# - AVD Name: "test_device_api35"

# Step 3: Root AVD with rootAVD
pip3 install rootAVD
rootAVD -s test_device_api35  # Root by AVD name

# Step 4: Verify root
emulator -avd test_device_api35 -no-snapshot-load
adb shell su -c "id"
# Expected: uid=0(root) gid=0(root)

# Step 5: Install Magisk modules
adb push module.zip /sdcard/Download/
# Flash in Magisk Manager app on emulator

# Step 6: Install patched APK
adb install -r patched.apk

# For split APKs:
adb install-multiple base.apk split_config.arm64_v8a.apk split_config.en.apk

# Force downgrade:
adb install -r -d -t patched.apk

# Clean install (signature mismatch):
adb uninstall com.example.app
adb install patched.apk
```

### GApps Testing on Emulator

**Option A: AVD with Google APIs image**

```bash
# Create AVD with "Google APIs" system image (not "Google Play")
# Includes Play Services but allows more flexibility

# Caveat: Pre-installed Google Play Services CANNOT be replaced
# with patched versions (system expects Google's signature)
```

**Option B: AVD without Google APIs + MicroG (recommended)**

```bash
# Create AVD with "No Google APIs" / AOSP system image

# Install MicroG
adb install GmsCore.apk
adb install ntfy.apk  # Push notification provider

# Install patched app
adb install patched.apk

# Verify MicroG self-check
# Open MicroG app → Self-check → All green (except Play Integrity)
```

### x86 vs ARM Translation

**Android Studio AVD**:
- **x86_64 images**: ~10x faster than ARM emulation
- **ARM64 images**: Slower but runs ARM native libraries directly
- **ARM translation**: When running x86_64 image with ARM APKs, emulator translates ARM to x86
- **Problem**: Anti-tamper, anti-debug, DRM detect translation and refuse to run
- **Fix**: Use ARM64 system images for apps with ARM-specific native code

**Genymotion**:
- Runs x86 images by default
- libhoudini for ARM translation (not included since Genymotion 3.x)
- Install via: https://github.com/vnsh01/Nyx (Android 11)
- macOS Apple Silicon: native ARM64, no translation needed

**Waydroid**:
- Uses host Linux kernel directly (container, not emulation)
- ARM translation via libndk_translation
- Requires SSE 4.2 CPU instructions
- Install via waydroid_script: https://github.com/casualsnek/waydroid_script

---

## Frida Setup on Emulator

```bash
# Install Frida tools
pip install frida-tools

# Download frida-server for emulator architecture
# Check architecture: adb shell getprop ro.product.cpu.abi
# For x86_64 emulator: download frida-server-x86_64.xz
# For arm64 emulator: download frida-server-arm64.xz

# Push and run frida-server
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server -D &"

# Verify connection
frida-ps -U  # Should list running processes

# Run Frida REPL against running app
frida -U -n com.example.app

# Spawn app with Frida injected
frida -U -f com.example.app -l hook.js --no-pause

# Run JavaScript hook script
frida -U -l bypass_signature.js -n com.example.app
```

---

## ADB Commands Reference

### Installation

```bash
adb install -r app.apk              # Replace existing app
adb install -d app.apk              # Allow version downgrade
adb install -t app.apk              # Allow test APKs
adb install-multiple base.apk s1.apk s2.apk  # Split APKs
adb uninstall com.example.app       # Remove app + data
```

### Debugging

```bash
adb logcat                          # View logs
adb logcat -s "ActivityManager"     # Filter by tag
adb logcat | grep -i "FATAL"        # Filter crash logs
adb shell dumpsys package com.example.app  # Package info
```

### File Operations

```bash
adb push file.txt /sdcard/          # Upload file
adb pull /sdcard/file.txt ./        # Download file
```

### Root Operations

```bash
adb shell su -c "command"           # Run as root
adb shell su -c "mount -o rw,remount /system"
adb push patched.apk /system/app/TargetApp/target.apk
adb shell su -c "chmod 644 /system/app/TargetApp/target.apk"
```

### Emulator-specific

```bash
emulator -avd NAME -no-snapshot-load  # Start emulator fresh
adb reboot                          # Reboot emulator
```

---

## ADB Install Flags Reference

| Flag | Meaning | Use Case |
|---|---|---|
| `-r` | Replace/reinstall existing app | Updating patched APK |
| `-d` | Allow version downgrade | Installing older patched version |
| `-t` | Allow test APKs (`android:testOnly="true"`) | Debug/test builds |
| `-g` | Grant all runtime permissions | Testing with all permissions |
| `--force-install` | Force install (Android 13+) | Bypass signature/version checks |
| `-p` | Partial install (split APK mode) | Internal use for install-multiple |