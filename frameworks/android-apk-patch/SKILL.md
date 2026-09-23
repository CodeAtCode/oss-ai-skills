---
name: android-apk-patch
description: "Use when modifying Android APKs - decompiling and recompiling with apktool, editing smali or resources, handling split APKs, APK signing v1/v2/v3 and key rotation, resolving AAPT2 and dependency errors, patching GApps-dependent apps, or testing modified APKs on emulators, Redroid, or Waydroid"
metadata:
  author: mte90
  version: "2.0.0"
  tags:
    - android
    - apk
    - gapps
    - reveng
    - patch
---

## Table of Contents

1. [Toolchain Setup](#1-toolchain-setup)
2. [Decompile/Recompile Workflow](#2-decompile-recompile-workflow)
3. [Signing](#3-signing)
4. [Deep Dives](#4-deep-dives)

---

## 1. Toolchain Setup & Version Requirements

### 1.1 Mandatory Tools

| Tool | Version | Purpose | URL |
|---|---|---|---|
| **Apktool** | **v2.11.0** | Decompile/recompile APKs | https://github.com/iBotPeaches/Apktool |
| **jadx** | **v1.5.1** | Read-only Java decompiler | https://github.com/skylot/jadx |
| **smali/baksmali** | **v3.0.9** | DEX bytecode assembly/disassembly | https://github.com/baksmali/smali |
| **APKEditor** | Latest | Merge/split APK handling | https://github.com/pxb1988/APKEditor |
| **apksigner** | SDK Build Tools **35.0.x** | APK signing (v1/v2/v3/v4) | Part of Android SDK |
| **zipalign** | SDK Build Tools **35.0.x** | APK alignment before signing | Part of Android SDK |
| **Frida** | **v17.9.0** | Dynamic instrumentation | https://frida.re |
| **ADB** | Platform Tools **35.0.x** | Device/emulator communication | Part of Android SDK |

### 1.2 Version Requirements

- **Apktool < 2.9.0** — Cannot handle API 34+ resources
- **Apktool < 2.6.0** — Uses legacy AAPT (v1) instead of AAPT2
- **smali < 3.0.5** — Cannot disassemble DEX format 038+ (Android 13+)
- **jarsigner** — Only produces v1 signatures; modern Android requires v2

### 1.3 Environment Setup

```bash
# Java 11+ required (Java 17 recommended)
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk

# Install Android SDK Build Tools
sdkmanager "build-tools;35.0.0"
sdkmanager "platform-tools"

# Install Frida
pip install frida-tools
```

---

## 2. Decompile/Recompile Workflow

### 2.1 Standard Workflow

```bash
# Step 1: Analyze with jadx
jadx-gui target.apk  # GUI
jadx -d analysis_output/ target.apk  # CLI

# Step 2: Decompile with apktool
apktool d target.apk -o decompiled/ -f

# Step 3: Make modifications (smali, resources, manifest)

# Step 4: Recompile
apktool b decompiled/ -o rebuilt.apk

# Step 5: Align (CRITICAL - must be BEFORE signing)
zipalign -v -p 4 rebuilt.apk rebuilt_aligned.apk

# Step 6: Sign
apksigner sign --ks ~/.android/debug.keystore \
    --ks-pass pass:android --key-pass pass:android \
    rebuilt_aligned.apk

# Step 7: Verify
apksigner verify --verbose --print-certs rebuilt_aligned.apk

# Step 8: Install
adb install -r rebuilt_aligned.apk
```

### 2.2 Decompilation Flags

```bash
# Force specific API level
apktool d target.apk -o out/ -f --api 35

# Ignore missing resources (Apktool 2.11.x)
apktool d target.apk -o out/ -f --ignore-missing-resources

# Skip resources (faster, Java-only)
apktool d target.apk -o out/ -f -s

# Decode only resources
apktool d target.apk -o out/ -f -r

# Use custom framework (OEM system APKs)
apktool if /path/to/oem-framework.apk
apktool d system_app.apk -o out/ -f
```

### 2.3 Decompiled Structure

```
decompiled/
├── AndroidManifest.xml
├── apktool.yml
├── assets/
├── lib/              # Native .so files
│   ├── arm64-v8a/
│   ├── armeabi-v7a/
│   └── x86_64/
├── res/              # Resources
│   ├── values/
│   ├── layout/
│   └── drawable/
├── smali/            # Main code (DEX bytecode)
│   └── com/example/app/
└── smali_classes2/   # Multi-DEX apps
```

### 2.4 Smali Editing Basics

```smali
# Force boolean method to return true
.method public isPremium()Z
    .registers 2
    const/4 v0, 0x1
    return v0
.end method

# NOP out a method call
# Replace: invoke-virtual {v0}, Lcom/example/Payroll;->show()V
# With:    nop

# Remove permission check
# Replace: if-eqz v0, :cond_deny
# With:    nop
```

### 2.5 Resource Editing

```xml
<!-- res/values/strings.xml -->
<string name="app_name">Patched App</string>

<!-- AndroidManifest.xml - Add permission -->
<uses-permission android:name="android.permission.QUERY_ALL_PACKAGES" />

<!-- AndroidManifest.xml - Export activity -->
<activity android:name=".HiddenActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

---

## 3. Signing: Schemes, Pitfalls, and Procedures

### 3.1 Signature Schemes

| Scheme | Since | Mechanism |
|---|---|---|
| **v1 (JAR)** | API 1 | Signs individual files in META-INF/ |
| **v2** | API 24 | Binary signature block; verifies entire APK |
| **v3** | API 28 | v2 + key rotation support |
| **v4** | API 30 | Merkle hash tree; streaming verification |

**Critical**: v2/v3 are whole-APK signatures. Any byte modification invalidates them.

### 3.2 apksigner vs jarsigner

| Feature | apksigner | jarsigner |
|---|---|---|
| Schemes | v1, v2, v3, v4 | v1 only |
| Whole-APK verification | Yes | No |
| Required for API 24+ | **Yes** | **No — rejected** |

**NEVER use jarsigner for APK signing.**

### 3.3 Signing Procedure

```bash
# Create custom keystore (one-time)
keytool -genkey -v -keystore ~/release.keystore \
    -alias myapp -keyalg RSA -keysize 2048 -validity 10000

# Debug keystore (testing only)
# Location: ~/.android/debug.keystore
# Password: android
# Alias: androiddebugkey

# Full workflow
# Step 1: ALIGN first (critical!)
zipalign -v -p 4 rebuilt.apk rebuilt_aligned.apk

# Step 2: Sign
apksigner sign \
    --ks ~/release.keystore \
    --ks-key-alias myapp \
    --ks-pass pass:your_password \
    --key-pass pass:your_password \
    --v1-signing-enabled true \
    --v2-signing-enabled true \
    --v3-signing-enabled true \
    rebuilt_aligned.apk

# Step 3: Verify
apksigner verify --verbose --print-certs rebuilt_aligned.apk
```

### 3.4 uber-apk-signer (Alternative)

```bash
# Download from https://github.com/patrickfav/uber-apk-signer/releases

# Quick debug signing
java -jar uber-apk-signer.jar --apks rebuilt.apk

# With custom keystore
java -jar uber-apk-signer.jar \
    --apks rebuilt.apk \
    --ks ~/apk-testing.keystore \
    --ksAlias testing \
    --ksPass your_password
```

### 3.5 Common Signing Errors

| Error | Cause | Fix |
|---|---|---|
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | Different signing key | `adb uninstall` then reinstall |
| `INSTALL_PARSE_FAILED_NO_CERTIFICATES` | Not signed | Sign with `apksigner` |
| `INSTALL_FAILED_SESSION_INVALID` | Splits with different keys | Sign ALL splits with same keystore |
| zipalign after sign | Signature broken | Always zipalign first |

### 3.6 Key Rotation (v3)

```bash
# Sign with new key, providing old key's lineage
apksigner sign \
    --ks new-release.keystore \
    --ks-key-alias newkey \
    --v3-signing-enabled true \
    --lineage /path/to/lineage-file \
    rebuilt_aligned.apk
```

---

## 4. Deep Dives

The following reference files contain detailed information on specific topics. Load them on demand based on your task:

| Topic | File | Covers |
|---|---|---|
| **Split APKs & GApps** | [references/split-and-gapps.md](references/split-and-gapps.md) | Split APK formats, merging, MicroG, signature spoofing, Play Integrity |
| **Testing & Containers** | [references/testing-containers.md](references/testing-containers.md) | Redroid, Waydroid setup and workflows |
| **Emulator Testing** | [references/emulator-testing.md](references/emulator-testing.md) | AVD setup, Frida, ADB commands, x86/ARM translation |
| **Troubleshooting** | [references/troubleshooting.md](references/troubleshooting.md) | AAPT2 errors, advanced patching, delivery, E2E workflow |

---

## References

- Redroid: https://github.com/remote-android/redroid-doc
- Waydroid: https://waydro.id
- apktool: https://ibotpeaches.github.io/Apktool/
- Frida: https://frida.re