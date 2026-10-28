> Loaded on demand from `SKILL.md` when the agent needs complete QTimer API reference.

# QTimer Reference

## Single-Shot Timer

```python
from PySide6.QtCore import QTimer

# Call function after 1000ms
QTimer.singleShot(1000, self.onTimer)

# With lambda
QTimer.singleShot(500, lambda: print("Delayed!"))

# Cancel single-shot (store reference)
self.timer_id = QTimer.singleShot(1000, self.delayedAction)
# Note: Can't cancel singleShot, use regular timer instead
```

## Periodic Timer

```python
from PySide6.QtCore import QTimer

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.onTimeout)
        
        # Start with 100ms interval
        self.timer.start(100)
        
        # Or: self.timer.setInterval(100); self.timer.start()
    
    def onTimeout(self):
        print("Timer fired!")
    
    def stopTimer(self):
        self.timer.stop()
    
    def isRunning(self):
        return self.timer.isActive()
    
    def remainingTime(self):
        return self.timer.remainingTime()  # ms until next timeout
```

## Timer Properties

```python
timer = QTimer()

# Interval (milliseconds)
timer.setInterval(1000)  # 1 second
interval = timer.interval()

# Single-shot mode
timer.setSingleShot(True)  # Fires once then stops

# Timer type
timer.setTimerType(Qt.PreciseTimer)    # ~1ms accuracy
timer.setTimerType(Qt.CoarseTimer)     # ~5% accuracy (default)
timer.setTimerType(Qt.VeryCoarseTimer) # ~500ms accuracy
```
