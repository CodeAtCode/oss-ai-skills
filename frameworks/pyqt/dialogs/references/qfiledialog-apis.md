> Loaded on demand from `SKILL.md` when the agent needs QFileDialog static method syntax and options.

# QFileDialog API Reference

## Static Methods

### getOpenFileName
```python
filename, _ = QFileDialog.getOpenFileName(
    parent,
    "Title",
    "/home/user",  # Starting directory
    "Images (*.png *.jpg);;Text Files (*.txt);;All Files (*)"
)
```

### getSaveFileName
```python
filename, _ = QFileDialog.getSaveFileName(
    parent,
    "Save File",
    "/home/user/untitled.txt",
    "Text Files (*.txt);;All Files (*)"
)
```

### getExistingDirectory
```python
directory = QFileDialog.getExistingDirectory(
    parent,
    "Select Directory",
    "/home/user",
    QFileDialog.Option.ShowDirsOnly
)
```

### getOpenFileNames (multiple files)
```python
files, _ = QFileDialog.getOpenFileNames(
    parent,
    "Open Files",
    "/home/user",
    "Images (*.png *.jpg)"
)
```

## Common Options
```python
options = QFileDialog.Option.DontUseNativeDialog  # Use Qt dialog instead of OS dialog
filename, _ = QFileDialog.getOpenFileName(parent, "Open", "", "", options=options)
```

---
*See official docs: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QFileDialog.html*
