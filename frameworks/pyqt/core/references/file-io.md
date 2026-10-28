> Loaded on demand from `SKILL.md` when the agent needs complete file I/O API reference.

# File I/O Reference

## QFile

```python
from PySide6.QtCore import QFile, QIODevice

# Read file
file = QFile("data.txt")
if file.open(QIODevice.ReadOnly | QIODevice.Text):
    data = file.readAll()
    file.close()
    print(data)

# Write file
file = QFile("output.txt")
if file.open(QIODevice.WriteOnly | QIODevice.Text):
    file.write(b"Hello, World!")
    file.close()

# Append
file = QFile("log.txt")
if file.open(QIODevice.Append | QIODevice.Text):
    file.write(b"New log entry\n")
    file.close()

# Check exists
if QFile.exists("data.txt"):
    print("File exists")

# Remove file
QFile.remove("temp.txt")

# Copy file
QFile.copy("source.txt", "dest.txt")

# Rename file
QFile.rename("old.txt", "new.txt")
```

## QTextStream

```python
from PySide6.QtCore import QFile, QTextStream, QIODevice

# Read text
file = QFile("data.txt")
if file.open(QIODevice.ReadOnly | QIODevice.Text):
    stream = QTextStream(file)
    stream.setEncoding(QTextStream.Utf8)
    
    # Read all
    content = stream.readAll()
    
    # Read line by line
    while not stream.atEnd():
        line = stream.readLine()
        print(line)
    
    file.close()

# Write text
file = QFile("output.txt")
if file.open(QIODevice.WriteOnly | QIODevice.Text):
    stream = QTextStream(file)
    stream.setEncoding(QTextStream.Utf8)
    stream << "Line 1\n"
    stream << "Line 2\n"
    stream.writeString("Unicode: 你好")
    file.close()
```

## QDir

```python
from PySide6.QtCore import QDir

# Current directory
current = QDir.currentPath()
home = QDir.homePath()
temp = QDir.tempPath()

# Create directory
dir = QDir()
dir.mkpath("/path/to/new/directory")  # Creates all parent dirs

# Check if exists
if QDir("/path/to/dir").exists():
    print("Directory exists")

# List directory contents
dir = QDir("/path/to/dir")
entries = dir.entryList()  # Files and dirs
files = dir.entryList(QDir.Files)  # Only files
dirs = dir.entryList(QDir.Dirs | QDir.NoDotAndDotDot)  # Only subdirs

# With filters
entries = dir.entryList(["*.txt"], QDir.Files | QDir.Readable)

# Remove directory
QDir("/path/to/dir").rmdir(".")  # Must be empty
```
