# Split APK Handling & GApps Patching

> This reference file is loaded on demand from ../SKILL.md.

## Split APK Handling

### Understanding Split APK Formats

Modern Play Store apps use Android App Bundles (AAB), split into multiple APKs:

| Format | Source | Extension | Contents |
|---|---|---|---|
| **Bundletool** | Google Play | `.apks` | ZIP with base + splits + toc.pb |
| **APKMirror** | APKMirror | `.apkm` | Same as .apks, renamed |
| **APKPure** | APKPure | `.xapk` | Similar, different metadata |
| **Individual** | Manual | `.apk` | Each split separate |

**Split types**:
- `base.apk` — Core app code, shared resources, manifest
- `split_config.arm64_v8a.apk` — ARM64 native libraries
- `split_config.armeabi_v7a.apk` — ARMv7 native libraries
- `split_config.x86_64.apk` — x86_64 native libraries
- `split_config.xxhdpi.apk` — Screen density resources
- `split_config.en.apk` — Language resources
- `split_config.google_apis.apk` — Google APIs integration
- `split_config.firebase.apk` — Firebase integration

### Extraction & Merging Workflow

```bash
# Extract splits from bundle format
mkdir splits/ && cd splits/
unzip ../input.apks  # or .apkm, .xapk
# Produces: base.apk, split_config.*.apk, toc.pb

# Merge into single "fat APK"
java -jar APKEditor.jar m -i base.apk split_config.arm64_v8a.apk \
    split_config.xxhdpi.apk split_config.en.apk -o merged.apk

# Decompile merged APK
apktool d merged.apk -o decompiled/ -f

# Make modifications

# Recompile
apktool b decompiled/ -o modified_base.apk

# Align and sign
zipalign -v -p 4 modified_base.apk modified_base_aligned.apk
apksigner sign --ks ~/.android/debug.keystore \
    --ks-pass pass:android --key-pass pass:android \
    modified_base_aligned.apk
```

### Re-installing Modified Split APKs

**Option A: Replace base APK only (recommended)**

```bash
# Uninstall first (signature mismatch blocks update)
adb uninstall com.example.app

# Install base + original splits
adb install-multiple modified_base_aligned.apk \
    splits/split_config.arm64_v8a.apk \
    splits/split_config.xxhdpi.apk \
    splits/split_config.en.apk
```

**Option B: Re-sign ALL APKs**

```bash
# Sign every APK with same keystore
for apk in modified_base_aligned.apk splits/split_config.*.apk; do
    apksigner sign --ks ~/.android/debug.keystore \
        --ks-pass pass:android --key-pass pass:android \
        "$apk"
done

# Install all at once
adb install-multiple modified_base_aligned.apk splits/split_config.*.apk
```

**Option C: Create new bundle**

```bash
java -jar bundletool.jar build-bundle \
    --modules=modified_base_aligned.apk,splits/split_config.arm64_v8a_apk \
    --output=patched.apks
```

### Split APK Pitfalls

| Pitfall | Fix |
|---|---|
| Missing native libs after merge | Manually copy missing `.so` files into merged APK's `lib/` |
| Resource conflicts during merge | Merge base + arch split first, then add others one at a time |
| `toc.pb` metadata mismatch | Use `adb install-multiple` directly, not bundletool |
| Feature module splits | Decompile feature split separately, merge smali directories |
| Base APK produces `null` resources | Merge with APKEditor first, or use `--ignore-missing-resources` |

---

## GApps Patching Strategies

### The GApps Dependency Problem

Apps depending on Google Play Services are hardest to patch:

1. **Split APK hell**: Play Services is ~100+ dynamic feature modules
2. **Runtime signature verification**: OS and GApps verify Play Services signature
3. **DroidGuard attestation**: Deeply integrated into Play Services core
4. **Auto-updates**: Play Store overwrites patches
5. **Play Integrity API**: Impossible to fully bypass on emulators

**Bottom line**: Do NOT directly patch `com.google.android.gms`. Use strategies below.

### Strategy 1: MicroG (Recommended)

MicroG is open-source replacement for Google Play Services.

```bash
# MicroG provides:
# - Location services (UnifiedNlp / OpenStreetMap)
# - Push notifications (ntfy or custom)
# - Device registration
# - Maps API (OpenStreetMap)
# - Limited Google account support

# MicroG does NOT provide:
# - Play Integrity passing
# - Full DroidGuard attestation
# - SafetyNet compatibility
# - All Google API parity

# Setup:
# 1. Download GmsCore.apk from https://github.com/microg/GmsCore/releases
#    Or "MicroG RE" (Redesign for ReVanced)
# 2. Install on device/emulator
# 3. Install push provider (e.g., ntfy)
# 4. Configure signature spoofing (see below)
```

### Strategy 2: Patching Individual GApps

**ReVanced** provides pre-made patches:
- https://github.com/ReVanced/revanced-patches
- Patches: YouTube, YouTube Music, Google Photos, etc.
- Handles: signature bypass, ad removal, background play

**Manual patching**:

GApps perform runtime signature verification against Google certificate fingerprint.

```bash
# 1. Decompile
apktool d google_app.apk -o decompiled/

# 2. Find signature verification code
# Search smali for: getPackageInfo, GET_SIGNATURES, PackageManager,
# MessageDigest, equals, toByteArray

# 3. Patch or NOP the check
# Common pattern:
#   const-string v0, "308203e3..."
#   invoke-virtual {v0}, Ljava/lang/String;->getBytes()[B
#   invoke-static {...}, Ljava/security/MessageDigest;->getInstance(...)
#   # Replace with: const/4 v_result, 0x1 (return true/valid)
```

### Strategy 3: Signature Spoofing

Makes MicroG's signature appear as real Google Play Services.

**ROM-level support**:
- LineageOS: Settings → System → Developer options → "Allow signature spoofing"
- AXP.OS, /e/OS, CalyxOS: Built-in with per-app control

**Magisk module** (stock ROMs):
- Patches `framework.jar` at runtime
- MicroG declares spoofing support in manifest
- Apps query MicroG signature, receive Google bytes

```bash
# Install signature spoofing Magisk module
# Search "FakeGApps" or "sigspoof" in Magisk Modules
# Or: https://github.com/microg/android_packages_apps_GmsCore/wiki/Installation
```

### Strategy 4: Play Integrity Bypass (2025)

| Tool | Type | Works On | Status |
|---|---|---|---|
| **TrickyStore** | Magisk module | Android 8+ (Zygisk) | Active |
| **Play Integrity Fix NEXT** | Magisk module | Android 8+ (Zygisk) | Active |
| **PIFork** | Magisk module | Pre-Android 13 | Active (osm0sis) |

**Stack for passing Play Integrity (2025)**:
1. Root via Magisk / KernelSU / APatch
2. Install ZygiskNext
3. Install Play Integrity Fix (or NEXT/fork)
4. Install TrickyStore + TrickyStore Addon
5. Do NOT put `com.google.android.gms` on Magisk DenyList

**CRITICAL**: Play Integrity does NOT pass on any emulator. Hardware attestation cannot be spoofed in software. For Play Integrity testing, use physical device.