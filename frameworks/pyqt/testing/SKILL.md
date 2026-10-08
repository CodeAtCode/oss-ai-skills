---
name: pyqt-testing
description: Use when testing PyQt/PySide6 applications with pytest-qt - qtbot fixture, signal/wait patterns, mouse/keyboard simulation, dialog testing, model/view testing, threaded code testing, or manual debugging techniques
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - python
    - qt
    - pyqt
    - pyside
    - testing
    - pytest
    - tdd
---

# PyQt Testing - pytest-qt

Comprehensive guide to testing Qt applications with pytest-qt.

## Installation

```bash
pip install pytest-qt
```

## qtbot Fixture

The `qtbot` fixture provides methods for interacting with Qt widgets:

```python
import pytest
from PySide6.QtWidgets import QApplication, QPushButton, QLabel
from PySide6.QtCore import Qt

def test_button_click(qtbot):
    """Test button click updates label."""
    button = QPushButton("Click Me")
    label = QLabel("Before")
    
    # Register widgets for cleanup
    qtbot.addWidget(button)
    qtbot.addWidget(label)
    
    def on_click():
        label.setText("After")
    
    button.clicked.connect(on_click)
    
    # Simulate click
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    
    assert label.text() == "After"

def test_key_press(qtbot):
    """Test keyboard input."""
    from PySide6.QtWidgets import QLineEdit
    
    line_edit = QLineEdit()
    qtbot.addWidget(line_edit)
    
    # Type text
    qtbot.keyClicks(line_edit, "Hello World")
    
    assert line_edit.text() == "Hello World"
```

## Mouse and Keyboard Simulation

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QLineEdit, QCheckBox

def test_mouse_buttons(qtbot):
    """Test different mouse buttons."""
    button = QPushButton("Test")
    qtbot.addWidget(button)
    
    clicks = []
    button.clicked.connect(lambda: clicks.append("left"))
    
    # Left click
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    
    # Right click
    qtbot.mouseClick(button, Qt.MouseButton.RightButton)
    
    # Double click
    qtbot.mouseDClick(button, Qt.MouseButton.LeftButton)
    
    assert clicks == ["left"]

def test_keyboard_modifiers(qtbot):
    """Test keyboard with modifiers."""
    line_edit = QLineEdit()
    qtbot.addWidget(line_edit)
    
    line_edit.setFocus()
    
    # Type with Ctrl held
    qtbot.keyClicks(line_edit, "a", Qt.KeyboardModifier.ControlModifier)
    
    # Press specific key
    qtbot.keyPress(line_edit, Qt.Key.Key_Return)
    qtbot.keyRelease(line_edit, Qt.Key.Key_Enter)

def test_checkbox_toggle(qtbot):
    """Test checkbox interaction."""
    checkbox = QCheckBox("Test")
    qtbot.addWidget(checkbox)
    
    # Click to check
    qtbot.mouseClick(checkbox, Qt.MouseButton.LeftButton)
    assert checkbox.isChecked()
    
    # Click to uncheck
    qtbot.mouseClick(checkbox, Qt.MouseButton.LeftButton)
    assert not checkbox.isChecked()
```

## waitSignal

Wait for signals to be emitted:

```python
from PySide6.QtCore import QThread, Signal, QTimer

def test_wait_signal(qtbot):
    """Test waiting for signal."""
    
    class Worker(QThread):
        finished = Signal(str)
        
        def run(self):
            import time
            time.sleep(0.1)
            self.finished.emit("Done")
    
    worker = Worker()
    
    # Wait for signal with timeout
    with qtbot.waitSignal(worker.finished, timeout=1000) as blocker:
        worker.start()
    
    # Check signal argument
    assert blocker.args == ["Done"]

def test_wait_signal_raising(qtbot):
    """raising is a bool: raise AssertionError on timeout instead of returning silently."""
    timer = QTimer()
    timer.setInterval(100)

    with qtbot.waitSignal(timer.timeout, timeout=500, raising=True):
        timer.start()

    timer.stop()

def test_wait_signals_any(qtbot):
    """Wait for any of multiple signals."""
    timer1 = QTimer()
    timer2 = QTimer()
    
    timer1.setInterval(200)
    timer2.setInterval(100)
    
    # Returns when either signal fires
    with qtbot.waitSignals([timer1.timeout, timer2.timeout], timeout=1000):
        timer2.start()  # This one will fire first
        timer1.start()
    
    timer1.stop()
    timer2.stop()
```

## waitActive and waitExposed

```python
def test_window_activation(qtbot, qapp):
    """Test window becomes active."""
    from PySide6.QtWidgets import QWidget
    
    widget = QWidget()
    qtbot.addWidget(widget)
    
    widget.show()
    
    # Wait for window to be active
    with qtbot.waitActive(widget, timeout=1000):
        qapp.setActiveWindow(widget)

def test_window_exposed(qtbot):
    """Test window is exposed (visible on screen)."""
    from PySide6.QtWidgets import QWidget
    
    widget = QWidget()
    qtbot.addWidget(widget)
    
    # Show and wait for exposure
    with qtbot.waitExposed(widget, timeout=1000):
        widget.show()
```

## Testing Dialogs

```python
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtCore import QTimer

def test_dialog_accept(qtbot):
    """Test dialog accepted."""
    
    class TestDialog(QDialog):
        def __init__(self):
            super().__init__()
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok |
                QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            
            layout = QVBoxLayout(self)
            layout.addWidget(buttons)
    
    dialog = TestDialog()
    
    # Find OK button
    button_box = dialog.findChild(QDialogButtonBox)
    ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
    
    # Click OK after dialog opens
    QTimer.singleShot(100, lambda: qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton))
    
    result = dialog.exec()
    
    assert result == QDialog.DialogCode.Accepted

def test_custom_dialog_values(qtbot):
    """Test custom dialog returns values."""
    
    class InputDialog(QDialog):
        def __init__(self):
            super().__init__()
            
            from PySide6.QtWidgets import QLineEdit
            
            self.line_edit = QLineEdit()
            self.line_edit.setPlaceholderText("Enter name")
            
            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok |
                QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            
            layout = QVBoxLayout(self)
            layout.addWidget(self.line_edit)
            layout.addWidget(buttons)
        
        def get_value(self):
            return self.line_edit.text()
    
    dialog = InputDialog()
    qtbot.addWidget(dialog)
    
    # Enter text
    qtbot.keyClicks(dialog.line_edit, "Test Name")
    
    # Accept dialog
    button_box = dialog.findChild(QDialogButtonBox)
    ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
    QTimer.singleShot(100, lambda: qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton))
    
    result = dialog.exec()
    
    assert result == QDialog.DialogCode.Accepted
    assert dialog.get_value() == "Test Name"
```

## Testing Model/View

```python
from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex

def test_list_model(qtbot):
    """Test QAbstractListModel."""
    
    class SimpleModel(QAbstractListModel):
        def __init__(self, data):
            super().__init__()
            self._data = data
        
        def rowCount(self, parent=QModelIndex()):
            return len(self._data)
        
        def data(self, index, role=Qt.ItemDataRole.DisplayRole):
            if 0 <= index.row() < len(self._data):
                return self._data[index.row()]
            return None
    
    model = SimpleModel(["Item 1", "Item 2", "Item 3"])
    
    assert model.rowCount() == 3
    index = model.index(1, 0)
    assert model.data(index, Qt.ItemDataRole.DisplayRole) == "Item 2"

def test_model_updates(qtbot):
    """Test model signals data changes."""
    
    class MutableModel(QAbstractListModel):
        def __init__(self):
            super().__init__()
            self._items = []
        
        def rowCount(self, parent=QModelIndex()):
            return len(self._items)
        
        def data(self, index, role=Qt.ItemDataRole.DisplayRole):
            if 0 <= index.row() < len(self._items):
                return self._items[index.row()]
            return None
        
        def add_item(self, item):
            self.beginInsertRows(QModelIndex(), len(self._items), len(self._items))
            self._items.append(item)
            self.endInsertRows()
    
    model = MutableModel()
    
    # Wait for rowsInserted signal
    with qtbot.waitSignal(model.rowsInserted, timeout=1000):
        model.add_item("New Item")
    
    assert model.rowCount() == 1
```

## Testing Threaded Code

```python
from PySide6.QtCore import QThread, Signal

def test_worker_thread(qtbot):
    """Test worker thread emits signals."""
    
    class TestWorker(QThread):
        progress = Signal(int)
        
        def run(self):
            for i in range(5):
                self.progress.emit(i * 20)
    
    worker = TestWorker()
    
    # Collect signals
    signals = []
    worker.progress.connect(signals.append)
    
    # Wait for thread to finish
    with qtbot.waitSignal(worker.finished, timeout=2000):
        worker.start()
    
    assert signals == [0, 20, 40, 60, 80]

def test_thread_cancellation(qtbot):
    """Test thread can be cancelled."""
    
    class CancellableWorker(QThread):
        finished = Signal()
        
        def __init__(self):
            super().__init__()
            self._cancelled = False
        
        def run(self):
            for i in range(100):
                if self._cancelled:
                    return
                import time
                time.sleep(0.01)
            self.finished.emit()
        
        def cancel(self):
            self._cancelled = True
    
    worker = CancellableWorker()
    worker.start()
    worker.cancel()
    worker.wait(100)  # Wait with timeout
    
    # Should have finished quickly due to cancellation
    assert not worker.isRunning()
```

## Fixtures

```python
# conftest.py - Shared fixtures
import pytest
from PySide6.QtWidgets import QApplication, QMainWindow

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication once per session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

@pytest.fixture
def main_window(qtbot):
    """Create main window for each test."""
    window = QMainWindow()
    qtbot.addWidget(window)
    window.show()
    return window

@pytest.fixture
def temp_settings(tmp_path):
    """Create temporary QSettings."""
    from PySide6.QtCore import QSettings
    import pathlib
    
    config_file = pathlib.Path(tmp_path) / "test.ini"
    settings = QSettings(str(config_file), QSettings.Format.IniFormat)
    yield settings
    settings.clear()
```

## Best Practices

1. **Always use qtbot.addWidget()** - Ensures proper cleanup
2. **Use waitSignal for async operations** - With appropriate timeouts
3. **Avoid real delays** - Use QTimer.singleShot for timing
4. **Test signals, not implementation** - Verify behavior
5. **Use fixtures for common setup** - DRY principle
6. **Keep tests isolated** - Each test should be independent

## Manual Testing

Debugging techniques for interactive testing and troubleshooting:

```python
# Add debug output
import logging
logging.basicConfig(level=logging.DEBUG)

# Check memory
from PySide6.QtCore import QObject
print(f"QObject children: {len(self.children())}")

# Dump widget tree
def dump_widgets(widget, indent=0):
    print(" " * indent + (widget.objectName() or widget.__class__.__name__))
    for child in widget.findChildren(QObject):
        dump_widgets(child, indent + 2)
```

## Testing Logic Without QApplication: the Presenter Pattern

Business logic inside QWidget slots needs a QApplication, an event loop, and widget plumbing to test. Extract decisions into a plain presenter class and keep slots as one-line delegations that only render presenter state. Models follow the same rule (see Testing Model/View above): keep QAbstractItemModel subclasses thin over plain data.

pytest instantiates fixtures only when a test requests them, so a presenter unit test that imports no Qt module and never requests qtbot or qapp runs with no QApplication at all. Source: https://pytest-qt.readthedocs.io/en/latest/reference.html#pytestqt.plugin.qapp

```python
# presenters.py - plain Python, no Qt imports
class CartPresenter:
    """Decisions live here; the widget only renders presenter state."""

    def __init__(self, max_items=5):
        self.items = []
        self.max_items = max_items

    def add(self, name, price):
        if len(self.items) >= self.max_items:
            raise ValueError(f"cart full: max {self.max_items} items")
        self.items.append((name, price))
        return len(self.items)

    @property
    def total(self):
        return sum(price for _, price in self.items)
```

```python
# test_presenters.py - unit test with no QApplication, event loop, or qtbot
import pytest

from presenters import CartPresenter


def test_add_rejects_full_cart():
    presenter = CartPresenter(max_items=2)
    presenter.add("apple", 1.0)
    presenter.add("pear", 2.0)
    with pytest.raises(ValueError, match="cart full: max 2 items"):
        presenter.add("fig", 3.0)
    assert presenter.total == 3.0
```

```python
# cart_widget.py - the slot only delegates and renders
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from presenters import CartPresenter


class CartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.presenter = CartPresenter()
        self.status = QLabel("empty")
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._on_add_clicked)
        layout = QVBoxLayout(self)
        layout.addWidget(self.status)
        layout.addWidget(add_button)

    def _on_add_clicked(self):
        try:
            count = self.presenter.add("item", 1.0)
        except ValueError as err:
            self.status.setText(str(err))
            return
        self.status.setText(f"{count} items, total {self.presenter.total:.2f}")
```

With this split, a qtbot integration test only asserts the rendering glue (`widget.status.text()`), never the rules: the presenter unit test already covers those.

## Mutation Testing for Qt Apps

Mutation testing mutates source lines and re-runs the suite; a surviving mutant means no assertion noticed the change. For Qt apps, mutate only non-UI logic (the presenters and models above) and exclude widget and slot code.

- Scope runs to presenter/model modules: `[tool.mutmut]` with `only_mutate = ["myapp/presenters.py"]`, `do_not_mutate` for widget modules, or `# pragma: no mutate` on a widget class.
- Slot bodies are hostile to mutation runs: mutmut re-runs the covered tests per mutant in forked workers, so a mutant inside a slot pays the full UI lifecycle cost every time. QApplication startup, window mapping/exposure (asynchronous on X11), every `qtbot.wait*` call spending its timeout budget, widget teardown; hundreds of UI tests multiply that cost across thousands of mutants.
- Slot mutations are also noisy: label text, tooltips, and margins are cosmetic, nothing should assert them, so they survive as equivalent mutants and bury real gaps.
- Qt-specific fork hazard: the `qapp` fixture leaves a live QApplication in the pytest process and every forked mutant worker inherits it. If mutant runs hang or segfault, switch mutmut to `process_isolation = "forkserver"`.

Tool mechanics, configuration reference, and equivalent-mutant triage: see [frameworks/pytest/references/mutation-testing.md](../../pytest/references/mutation-testing.md).

## Exact-State Assertions vs Screenshot Oracles

Assert the exact widget/model state that encodes the behavior. A screenshot is a visual oracle, never a logic oracle.

- Read state through accessors and assert exact values: `line_edit.text()`, `checkbox.isChecked()`, `spin.value()`, `combo.currentText()`, `model.data(model.index(0, 0), Qt.ItemDataRole.DisplayRole)`. Exact equality beats `is not None` and truthiness checks.
- Reach state through widget setters when input handling is not the subject: the pytest-qt docs note that `QComboBox.setCurrentText`, `QLineEdit.setText`, and similar widget methods have the same effect as user interaction but are more reliable than the raw QTest-style calls; keep `qtbot.mouseClick`/`qtbot.keyClicks` for tests about the input handling itself. Source: https://pytest-qt.readthedocs.io/en/latest/reference.html
- For state updated asynchronously (worker thread, queued signal), poll with `qtbot.waitUntil(callback, timeout=5000)` (v2.0+): in assert form the callback raises AssertionError until the state holds; in lambda form it returns True/False (any other return raises ValueError). Source: https://pytest-qt.readthedocs.io/en/latest/reference.html#pytestqt.qtbot.QtBot.waitUntil

```python
def test_async_status(qtbot):
    widget = StatusWidget()
    qtbot.addWidget(widget)

    widget.start_job()  # worker thread updates the label when done

    qtbot.waitUntil(lambda: widget.status.text() == "done", timeout=2000)
    assert widget.status.text() == "done"
    assert widget.presenter.ok_count == 1
```

`qtbot.screenshot(widget)` (v4.1+) saves a PNG under pytest's tmp_path and returns its `pathlib.Path`: a visual oracle for review or regression comparison. It cannot assert presenter state or model rows; passing pixels can coexist with broken logic. Source: https://pytest-qt.readthedocs.io/en/latest/reference.html#pytestqt.qtbot.QtBot.screenshot

## References

- **pytest-qt**: https://pytest-qt.readthedocs.io/
- **Qt for Python Testing**: https://doc.qt.io/qtforpython-6/
- **pytest**: https://docs.pytest.org/
