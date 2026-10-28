> Loaded on demand from `SKILL.md` when the agent needs complete signal/slot syntax reference.

# Signals and Slots Reference

## Signal Declaration (PySide6)

```python
from PySide6.QtCore import QObject, Signal

class MyObject(QObject):
    # Define signals at class level
    valueChanged = Signal(int)
    nameChanged = Signal(str)
    dataReady = Signal(dict)
    errorOccurred = Signal(str)
    
    # Signal with multiple arguments
    positionChanged = Signal(int, int)
    
    # Signal with optional arguments
    progressChanged = Signal(int, arguments=['percent'])
```

## Signal Declaration (PyQt6)

```python
from PyQt6.QtCore import QObject, pyqtSignal

class MyObject(QObject):
    valueChanged = pyqtSignal(int)
    nameChanged = pyqtSignal(str)
    positionChanged = pyqtSignal(int, int)
```

## Slot Declaration (PySide6)

```python
from PySide6.QtCore import Slot

class MyObject(QObject):
    @Slot()
    def doSomething(self):
        print("Action performed")
    
    @Slot(int)
    def setValue(self, value):
        self._value = value
    
    @Slot(str, int)
    def processData(self, name, count):
        pass
    
    @Slot(result=str)  # Return type annotation
    def getName(self) -> str:
        return self._name
```

## Slot Declaration (PyQt6)

```python
from PyQt6.QtCore import pyqtSlot

class MyObject(QObject):
    @pyqtSlot()
    def doSomething(self):
        pass
    
    @pyqtSlot(int)
    def setValue(self, value):
        pass
```

## Connecting Signals to Slots

```python
# Connect signal to slot
button.clicked.connect(self.onButtonClick)
valueChanged.connect(self.updateValue)

# Connect with lambda
button.clicked.connect(lambda: print("Clicked!"))

# Connect with partial
from functools import partial
button.clicked.connect(partial(self.processItem, item_id))

# Disconnect
button.clicked.disconnect(self.onButtonClick)

# Check connection
is_connected = button.clicked.isConnected(self.onButtonClick)

# Emit signal
self.valueChanged.emit(42)
self.positionChanged.emit(x, y)

# Block signals temporarily
button.blockSignals(True)
button.setChecked(True)
button.blockSignals(False)

# Get signal emission count
count = button.receivers(button.clicked)
```

## Connection Types

```python
from PySide6.QtCore import Qt

# Auto (default) - Direct if same thread, Queued if different
button.clicked.connect(self.handleClick, Qt.AutoConnection)

# Direct - Slot called immediately in signal's thread
button.clicked.connect(self.handleClick, Qt.DirectConnection)

# Queued - Slot called when control returns to receiver's thread
worker.finished.connect(self.onFinished, Qt.QueuedConnection)

# BlockingQueued - Blocks until slot completes (use carefully!)
worker.result.connect(self.handleResult, Qt.BlockingQueuedConnection)
```

## Properties

```python
from PySide6.QtCore import Property, Signal

class Person(QObject):
    nameChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._name = ""
    
    @Property(str, notify=nameChanged)
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if self._name != value:
            self._name = value
            self.nameChanged.emit()
```

### Using Properties

```python
person = Person()
person.name = "Alice"  # Setter called
print(person.name)     # Getter called

# Connect to property change
person.nameChanged.connect(lambda: print("Name changed!"))
```
