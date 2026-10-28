> Loaded on demand from SKILL.md when the agent needs plasmoid structure, metadata.json schema, version requirements, or dependency listings.

# Plasmoid Structure & Dependencies Reference

## Version Requirements

| Component | Version |
|-----------|---------|
| Plasma | 6.x |
| Qt | 6.x |
| Python | 3.8+ |
| PySide6/PyQt6 | 6.x |

## Dependencies

### System Packages

```bash
# Arch/Manjaro
sudo pacman -S python-pyqt6 pyside6 kirigami plasma-framework plasma-sdk

# Fedora
sudo dnf install python3-pyqt6 python3-pyside6 kf6-kirigami-devel plasma-framework plasma-sdk

# Debian/Ubuntu
sudo apt install python3-pyqt6 python3-pyside6 kirigami-devel plasma-framework plasma-sdk

# openSUSE
sudo zypper install python3-qt6 python3-pyside6 kf6-kirigami-devel plasma-framework
```

### Python Packages

```bash
pip install psutil requests pydbus
```

## Plasmoid Structure

```
my-plasmoid/
├── package/
│   ├── contents/
│   │   ├── config/
│   │   │   ├── config.qml
│   │   │   └── main.xml
│   │   ├── ui/
│   │   │   ├── main.qml
│   │   │   └── configGeneral.qml
│   │   └── main.xml
│   └── metadata.json
├── src/
│   ├── __init__.py
│   └── backend.py
├── README.md
└── LICENSE
```
