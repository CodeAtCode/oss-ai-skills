---
name: pyqt-multimedia
description: "Use when adding multimedia to PyQt/PySide6 apps - audio and video playback with QMediaPlayer, camera capture with QCamera and QMediaCaptureSession, audio/video recording with QMediaRecorder, GStreamer backend setup, or codec and platform compatibility issues"
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - python
    - qt
    - pyqt
    - multimedia
    - audio
    - video
    - camera
    - media
---

> **Objective:** Use this skill to reduce playback-deadlock incidents, GStreamer-backend startup failures, codec-missing black-screen bugs, and recording-corruption incidents by enforcing backend-setup discipline, codec-availability checks, and platform-compatibility decision patterns below.

# PyQt Multimedia

## Core Rules (do X because Y)

### Check GStreamer plugins before playback because missing codecs produce silent black video

On Linux, Qt Multimedia uses GStreamer as the backend. Missing plugins cause video to render as black screens without errors.

```bash
# Ubuntu/Debian - install ALL plugin groups before testing playback
sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav

# Verify plugins are loaded
gst-inspect-1.0 | grep -E "h264|mp3|aac"
```

**Failure mode:** Video loads, QMediaPlayer reports "no error", but screen stays black. Solution: install missing plugin packages, not just Qt bindings.

### Use QMediaCaptureSession not QMediaRecorder directly because the session owns the pipeline

QMediaCaptureSession coordinates camera, video output, image capture, and recorder. Bypassing it causes resource conflicts and recording corruption.

```python
# ✅ Correct: session coordinates all components
self.capture_session = QMediaCaptureSession()
self.capture_session.setCamera(self.camera)
self.capture_session.setVideoOutput(self.video_widget)
self.capture_session.setRecorder(self.recorder)  # Session manages pipeline

# ❌ Wrong: recorder without session causes conflicts
self.recorder = QMediaRecorder()
# Missing session = pipeline ownership unclear, recording fails silently
```

### Set output location before calling record() because unconfigured recorder corrupts files

QMediaRecorder requires output location to be set before recording starts. Skipping this produces 0-byte or corrupted files.

```python
# ✅ Set location first, then record
self.recorder.setOutputLocation(QUrl.fromLocalFile(path))
self.recorder.record()

# ❌ Wrong order: recording starts with no destination
self.recorder.record()
self.recorder.setOutputLocation(QUrl.fromLocalFile(path))  # Too late
```

### Check device availability before instantiating because unavailable devices crash on start

QCamera and QAudioInput fail when instantiated with invalid device references. Always enumerate devices first.

```python
from PyQt6.QtMultimedia import QMediaDevices

# ✅ Check before use
cameras = QMediaDevices.videoInputs()
if not cameras:
    raise RuntimeError("No camera available - cannot start video")
self.camera = QCamera(cameras[0])

# ❌ Wrong: no check, crashes on camera.start()
self.camera = QCamera()  # Invalid device
self.camera.start()  # Silent failure or crash
```

### Handle QMediaPlayer error signals because playback failures are silent without them

QMediaPlayer does not raise exceptions on playback errors. Without error signal handlers, users see nothing happen.

```python
self.player.errorChanged.connect(self.handle_playback_error)

def handle_playback_error(self, error: QMediaPlayer.ErrorState):
    if error != QMediaPlayer.ErrorState.NoError:
        # Log or display the error - otherwise user sees nothing
        print(f"Playback failed: {self.player.errorString()}")
```

---

## Audio Playback

Basic audio player with volume control:

```python
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

player = QMediaPlayer()
audio_output = QAudioOutput()
player.setAudioOutput(audio_output)
player.setSource(QUrl.fromLocalFile("audio.mp3"))
audio_output.setVolume(0.5)
player.play()
```

See `references/media-pipeline.md` for complete audio/video player with controls.

---

## Video Playback

Video playback requires QVideoWidget for display. Black screen usually means missing GStreamer plugins (see Core Rules).

```python
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

player = QMediaPlayer()
video_widget = QVideoWidget()
player.setVideoOutput(video_widget)
player.setSource(QUrl.fromLocalFile("video.mp4"))
player.play()
```

See `references/media-pipeline.md` for complete player with position slider and time labels.

---

## Camera Capture

### Photo Capture

Use QMediaCaptureSession with QImageCapture for photo capture:

```python
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QImageCapture
from PyQt6.QtMultimedia import QMediaDevices

cameras = QMediaDevices.videoInputs()
if not cameras:
    raise RuntimeError("No camera found")

camera = QCamera(cameras[0])
capture_session = QMediaCaptureSession()
capture_session.setCamera(camera)

image_capture = QImageCapture()
capture_session.setImageCapture(image_capture)

camera.start()
image_capture.captureToFile()
```

See `references/media-pipeline.md` for camera with device selection and photo preview.

---

## Audio/Video Recording

### Video Recording

Use QMediaRecorder attached to QMediaCaptureSession:

```python
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaRecorder

camera = QCamera()
capture_session = QMediaCaptureSession()
capture_session.setCamera(camera)

recorder = QMediaRecorder()
capture_session.setRecorder(recorder)

recorder.setOutputLocation(QUrl.fromLocalFile("output.mp4"))
recorder.record()
```

See `references/media-pipeline.md` for complete recorder with status handling and timestamps.

### Audio Recording

For audio-only recording, attach QAudioInput to the session:

```python
from PyQt6.QtMultimedia import QMediaRecorder, QMediaCaptureSession, QAudioInput

capture_session = QMediaCaptureSession()
audio_input = QAudioInput()
capture_session.setAudioInput(audio_input)

recorder = QMediaRecorder()
capture_session.setRecorder(recorder)
recorder.record()
```

---

## GStreamer Backend (Linux)

Linux uses GStreamer. Install plugin packages before testing multimedia:

```bash
# Core + bad + ugly plugins + libav for broad codec support
sudo apt-get install gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav

# Verify GStreamer can find codecs
gst-inspect-1.0 h264parse
gst-inspect-1.0 mp3
```

**Failure mode:** `QMediaPlayer` loads video file but playback fails with no error. Cause: GStreamer missing codec plugins. Fix: install plugin packages above.

---

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Black video screen | Missing GStreamer codec plugins | Install `gstreamer1.0-plugins-bad` and `gstreamer1.0-libav` |
| Recording produces 0-byte file | Output location not set before `record()` | Call `setOutputLocation()` before `record()` |
| Camera.start() crashes | Camera device unavailable | Check `QMediaDevices.videoInputs()` before instantiating QCamera |
| No audio output | Wrong audio output device selected | Check `QMediaDevices.audioOutputs()` and set explicitly |
| Playback fails silently | Error signal not connected | Connect to `errorChanged` signal and handle errors |

---

## Deep Dives

See reference files loaded on demand:

- **`references/media-pipeline.md`** - Complete video player with controls, camera capture with session management, media recorder setup, error handling patterns
- **`references/codecs-platforms.md`** - Platform-specific codec support tables, installation commands for Linux/Windows/macOS, format compatibility guides

---

## References

- **Qt Multimedia**: https://doc.qt.io/qt-6/qtmultimedia-index.html
- **PySide6 Multimedia**: https://doc.qt.io/qt-6/multimedia.html
- **GStreamer**: https://gstreamer.freedesktop.org/
