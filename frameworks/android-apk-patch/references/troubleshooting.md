# Troubleshooting, Advanced Patching & Delivery

> This reference file is loaded on demand from ../SKILL.md.

## Dependency Hell: Frameworks, AndroidX, OEM Resources

### Common Resource Dependency Errors

```
# Error 1: Missing AndroidX resources
error: resource 'com.example:id/material_textinput' not found

# Error 2: Styleable attribute not found
error: style attribute 'attr/layout_constraintBaseline_toBaselineOf' not found

# Error 3: AAPT2 crash
ERROR: AAPT2 aapt2(...) exited with code 1
brut.androlib.AndrolibException

# Error 4: Duplicate resource
error: resource 'style/Theme.MaterialComponents' has already been defined

# Error 5: Missing framework resource
error: resource '@android:configui_configFlags' not found
```

### Systematic Dependency Resolution

**Step 1: Install ROM-specific frameworks**

```bash
# Install standard Android framework (usually automatic)
apktool if framework-res.apk

# Pull framework files from rooted device
adb pull /system/framework/ ./device_frameworks/

# Install OEM-specific frameworks
# Samsung:
apktool if device_frameworks/sec_platform_library.jar
apktool if device_frameworks/com.samsung.device.jar
apktool if device_frameworks/frameworksSamsungSDK.jar

# Xiaomi/MIUI:
apktool if device_frameworks/framework-miui-res.apk
apktool if device_frameworks/MiuiSdk.jar
apktool if device_frameworks/framework-mi.jar

# Huawei:
apktool if device_frameworks/HWExtension.jar
apktool if device_frameworks/hwsdk.jar

# OnePlus/Oplus:
apktool if device_frameworks/oplus-framework.jar
apktool if device_frameworks/oplus-res.apk

# Check installed frameworks
ls ~/.local/share/apktool/framework/
```

**Step 2: Install shared library APKs**

```bash
# Find shared library APKs
adb shell pm list packages -f | grep shared
adb shell pm list packages -f | grep library

# Pull and install as framework
adb pull /system/app/SomeSharedLib/SomeSharedLib.apk
apktool if SomeSharedLib.apk
```

**Step 3: Force API level**

```bash
# Resources from newer APIs not found
apktool d target.apk -o out/ -f --api 35

# Legacy frameworks
apktool d target.apk -o out/ -f --api 29
```

**Step 4: Ignore non-critical missing resources**

```bash
# Apktool 2.11.x
apktool d target.apk -o out/ -f --ignore-missing-resources
```

### AndroidX-Specific Issues

**Issue A: Cross-library resource references**

AndroidX migrated `android.support.*` to `androidx.*`. Issues:
- Cross-library resource references may resolve incorrectly when decompiled
- R8 obfuscation may strip unused AndroidX resources

**Fix**: Use Apktool 2.11.0+. For R8-obfuscated apps, manually add required `.aar` files as frameworks.

**Issue B: Obfuscation**

R8/ProGuard/DexGuard can strip resources. Options:
1. Decompile original APK without modification and immediately recompile
2. Manually add missing resource definition to `res/values/` files
3. Use `--ignore-missing-resources` and accept some features may break

### AAPT2 Error Catalog

| Error | Cause | Fix |
|---|---|---|
| `resource has already been defined` | Duplicate resource entry | Apktool 2.11.0+ handles most. Search for duplicates in `res/values/*.xml` |
| `failed to compile values files` | Style/attr references to undefined resources | Check `attrs.xml`, `styles.xml`, `themes.xml` |
| `malformed compiled jar` | Samsung DEX format 039 in framework | `apktool d -api 29` |
| `no resource identifier found for attribute` | Missing library dependency | Install required library APK as framework |
| `invalid file path` | Windows path length limit or special characters | Move project to short path, rename files |
| `unmarshalling resource table` | Corrupted `resources.arsc` | Try `--ignore-missing-resources`, or use APKEditor |
| `Error: java.nio.BufferOverflowException` | Very large resource table (>2GB) | Use 64-bit Java: `JAVA_OPTS="-Xmx4g" apktool b ...` |

---

## Advanced Patching Techniques

### Dynamic Instrumentation with Frida

**SSL Pinning Bypass**:

```javascript
// ssl_pinning_bypass.js
Java.perform(function() {
    var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
    var SSLContext = Java.use('javax.net.ssl.SSLContext');

    // Bypass TrustManager
    var TrustManager = Java.registerClass({
        name: 'com.example.MalliciousTrustManager',
        implements: [X509TrustManager],
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() { return []; }
        }
    });

    // Pass our TrustManager to SSLContext
    var TrustManagers = [TrustManager.$new()];
    SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom').implementation = function(a, b, c) {
        this.init(a, TrustManagers, c);
    };
});

// Run: frida -U -l ssl_pinning_bypass.js -n target_app
```

**Root Detection Bypass**:

```javascript
// root_detection_bypass.js
Java.perform(function() {
    // Common root detection patterns
    var Runtime = Java.use('java.lang.Runtime');
    var ProcessBuilder = Java.use('java.lang.ProcessBuilder');

    // Hook exec/popen calls
    Runtime.exec.overload('[Ljava.lang.String;').implementation = function(cmd) {
        var cmdStr = cmd.toString();
        if (cmdStr.includes('su') || cmdStr.includes('which') || cmdStr.includes('test')) {
            console.log('Blocked root check: ' + cmdStr);
            return null;
        }
        return this.exec(cmd);
    };

    // File existence checks
    var File = Java.use('java.io.File');
    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        if (path.includes('su') || path.includes('magisk') || path.includes('busybox')) {
            console.log('Blocked file check: ' + path);
            return false;
        }
        return this.exists();
    };
});
```

### Dealing with Obfuscation

**R8/ProGuard/DexGuard**:

1. **Decompile with jadx first** to see what names survived
2. **Search by string literals** - strings survive obfuscation
3. **Follow the logic** - obfuscated names still have patterns
4. **Use apktool's `--ignore-missing-resources`** if R8 stripped resources

**Finding the right class**:

```bash
# Search for strings in decompiled output
grep -r "premium_feature" decompiled/smali/
grep -r "purchase" decompiled/smali/

# Search in jadx output
jadx -d jadx_output/ target.apk
# Then use jadx-gui for interactive exploration
```

### Bypassing App Integrity Checks

**File Hash Verification**:

```smali
# Find hash computation in smali
# Look for: MessageDigest, MessageDigest.getInstance, SHA-256, MD5
# Look for: readFile, openFileInput, getPackageCodePath

# Patch: Force the hash to match expected value
# Or: Skip the comparison entirely (NOP the if-eq check)
```

**DEX Integrity Check**:

```smali
# Look for: DEX checksum verification, DEX header validation
# Common pattern: compute checksum of DEX file, compare with embedded value

# Patch: NOP the verification method
# Or: Modify the embedded checksum to match modified DEX (hard)
```

**Tamper Detection**:

```smali
# Look for: signature checks, file modification time checks
# Common pattern: getPackageInfo with GET_SIGNATURES, compare with expected

# Patch: NOP the check, or force return valid result
```

### Creating Magisk Modules

Alternative to direct patching - overlay modifications at runtime:

```bash
# Basic Magisk module structure
magisk_module/
├── module.prop
├── post-fs-data.sh    # Runs early in boot
├── service.sh         # Runs later, after Zygote
└── system/            # Files to overlay
    └── app/
        └── TargetApp/
            └── target.apk
```

**module.prop**:
```
id=targetpatch
name=Target App Patch
version=1.0
versionCode=1
author=You
description=Patched Target App with features X, Y, Z
```

---

## Adding Features to an APK

### Creating New Smali Classes

```smali
.class public Lcom/example/app/DebugUtils;
.super Ljava/lang/Object;


.method public static logDebug(Ljava/lang/String;)V
    .registers 2

    const-string v0, "PATCHED"
    const-string v1, "%s"
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    return-void
.end method
```

### Adding a New Activity

**1. Create the smali class**:

```smali
.class public Lcom/example/app/DebugActivity;
.super Landroidx/appcompat/app/AppCompatActivity;

.method public onCreate(Landroid/os/Bundle;)V
    .registers 2
    invoke-super {p0, p1}, Landroidx/appcompat/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V

    const-string v0, "DebugActivity created"
    invoke-static {v0}, Lcom/example/app/DebugUtils;->logDebug(Ljava/lang/String;)V

    return-void
.end method
```

**2. Register in AndroidManifest.xml**:

```xml
<activity android:name=".DebugActivity" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

### Adding External Libraries

**1. Extract .aar or .jar from dependency**

**2. Convert to framework**:

```bash
# For .aar files, extract classes.jar
unzip library.aar classes.jar -d temp/

# Install as framework
apktool if temp/classes.jar
```

**3. Reference in smali**:

```smali
# Use the library classes normally
invoke-static {v0}, Lcom/library/Utility;->doSomething()V
```

### Handling Multi-DEX

When adding code increases method count beyond 65535:

1. Decompile will create `smali_classes2/`, `smali_classes3/`, etc.
2. Put new classes in `smali/` (first DEX) if possible
3. If method count exceeds, apktool handles multi-DEX automatically on recompile

---

## Delivering the APK to End User

### Release Signing (Not Debug!)

```bash
# Create release keystore (one-time, BACKUP SECURELY)
keytool -genkey -v -keystore ~/release.keystore \
    -alias myapp -keyalg RSA -keysize 4096 -validity 10000

# Sign release build
zipalign -v -p 4 rebuilt.apk rebuilt_aligned.apk
apksigner sign \
    --ks ~/release.keystore \
    --ks-key-alias myapp \
    --ks-pass pass:your_strong_password \
    --key-pass pass:your_strong_password \
    --v1-signing-enabled true \
    --v2-signing-enabled true \
    --v3-signing-enabled true \
    rebuilt_aligned.apk

# Verify
apksigner verify --verbose --print-certs rebuilt_aligned.apk
```

### What User Must Do Before Installing

1. **Enable "Install unknown apps"** for their file manager/browser
2. **Disable Play Protect** (optional, may block custom-signed APKs)
3. **Uninstall original app** if signature differs (will lose data)

### Distribution Methods

**Direct APK**:
- Simplest for single APK
- User downloads, taps to install

**Split APK Bundle (.apks)**:
- Use bundletool to create
- User needs SAI (Split APKs Installer) or similar

**APKMirror format (.apkm)**:
- Same as .apks, just different name
- Compatible with APKMirror Installer

**ADB install** (for advanced users):
```bash
adb install -r patched.apk
# For splits:
adb install-multiple base.apk split_config.*.apk
```

### Preventing Play Store Overwrites

1. **Change package name** (creates new app identity)
2. **Use different signing key** (user must uninstall original first)
3. **Inform user to disable auto-updates** for the app

---

## End-to-End Workflow: Zero to Delivery

### Phase 1: Setup (One-time)

- [ ] Install Java 17
- [ ] Install Apktool 2.11.0
- [ ] Install jadx 1.5.1
- [ ] Install Android SDK Build Tools 35.0.x
- [ ] Install Frida (pip install frida-tools)
- [ ] Create release keystore (BACKUP SECURELY)
- [ ] Set up emulator or container (redroid/Waydroid/AVD)

### Phase 2: Analysis

- [ ] Decompile with jadx to understand structure
- [ ] Identify target functionality
- [ ] Map out relevant classes/methods
- [ ] Check for obfuscation (R8/ProGuard)
- [ ] Check for anti-tamper/anti-debug

### Phase 3: Decompile

- [ ] Run `apktool d target.apk -o dec/ -f`
- [ ] If resource errors, try `--api 35` or `--ignore-missing-resources`
- [ ] For OEM apps, install framework JARs first

### Phase 4: Modify

- [ ] Edit smali files for logic changes
- [ ] Edit resources for UI changes
- [ ] Edit AndroidManifest.xml for permissions/components
- [ ] Test recompilation frequently (small iterations)

### Phase 5: Recompile & Fix

- [ ] `apktool b dec/ -o rebuilt.apk`
- [ ] If AAPT2 errors, consult error catalog
- [ ] If duplicate resources, search and remove
- [ ] If missing resources, add manually or use ignore flag

### Phase 6: Sign & Test (Local)

- [ ] `zipalign -v -p 4 rebuilt.apk rebuilt_aligned.apk`
- [ ] `apksigner sign --ks release.keystore ... rebuilt_aligned.apk`
- [ ] `apksigner verify --verbose rebuilt_aligned.apk`
- [ ] Install on emulator/container
- [ ] Test core functionality
- [ ] Check logs for crashes: `adb logcat | grep -i FATAL`

### Phase 7: Prepare for Delivery

- [ ] Verify all features work
- [ ] Test on multiple Android versions (29, 33, 35)
- [ ] Create user documentation (what changed, how to install)
- [ ] Backup original APK and keystore

### Phase 8: Deliver

- [ ] Package APK + instructions
- [ ] Distribute via chosen method
- [ ] Collect feedback on issues

### Phase 9: Maintenance

- [ ] Track upstream updates
- [ ] Re-apply patches when needed
- [ ] Update documentation for new versions

---

## Quick Reference Cheat Sheet

### Common Commands

```bash
# Decompile
apktool d target.apk -o dec/ -f

# Recompile
apktool b dec/ -o rebuilt.apk

# Align
zipalign -v -p 4 rebuilt.apk rebuilt_aligned.apk

# Sign (debug)
apksigner sign --ks ~/.android/debug.keystore --ks-pass pass:android rebuilt_aligned.apk

# Sign (release)
apksigner sign --ks release.keystore --ks-key-alias myapp --ks-pass pass:pwd rebuilt_aligned.apk

# Verify
apksigner verify --verbose rebuilt_aligned.apk

# Install
adb install -r rebuilt_aligned.apk

# Uninstall
adb uninstall com.example.app
```

### Smali Quick Reference

```smali
# Return constant
const/4 v0, 0x0    # 0
const/4 v0, 0x1    # 1
const/high16 v0, 0x3e800000  # 0.25f

# Return boolean
const/4 v0, 0x0    # false
const/4 v0, 0x1    # true

# Return string
const-string v0, "value"

# Invoke virtual (object method)
invoke-virtual {v0}, Ljava/lang/String;->length()I

# Invoke static (class method)
invoke-static {v0}, Ljava/lang/System;->out(Ljava/lang/Object;)V

# New instance
new-instance v0, Ljava/lang/StringBuilder;
invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

# Field access
iget-object v0, p0, Lcom/example/App;->context:Landroid/content/Context;
iput-object v0, p0, Lcom/example/App;->context:Landroid/content/Context;

# Conditional jumps
if-eqz v0, :label    # if v0 == 0, goto label
if-nez v0, :label    # if v0 != 0, goto label
if-eq v0, v1, :label # if v0 == v1, goto label

# Labels
:label
    # code here

# Return
return-void
return v0
return-object v0
```

### Key File Paths

```
~/.android/debug.keystore        # Debug keystore
~/.local/share/apktool/framework/ # Installed frameworks
~/release.keystore               # Release keystore (BACKUP!)
/data/local/tmp/                 # Temporary files on device
/system/framework/               # Device frameworks
```

### Common Patterns

**NOP a method call**:
```smali
# Before:
invoke-virtual {v0}, Lcom/example/Target;->doSomething()V

# After:
nop
```

**Force method to return true**:
```smali
.method public checkPermission()Z
    .registers 2
    const/4 v0, 0x1
    return v0
.end method
```

**Force method to return false**:
```smali
.method public checkPermission()Z
    .registers 2
    const/4 v0, 0x0
    return v0
.end method
```

**Remove a conditional branch**:
```smali
# Before:
if-eqz v0, :skip
# ... code ...
:skip

# After:
nop
# ... code ...
:skip
```