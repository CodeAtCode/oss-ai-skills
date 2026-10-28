> Loaded on demand from `SKILL.md` when the agent needs common headers and CMake component lookup.

# Quick Reference

## Common Headers

```cpp
#include <QApplication>      // GUI application
#include <QMainWindow>      // Main window
#include <QWidget>          // Basic widget
#include <QPushButton>      // Button
#include <QLabel>           // Text label
#include <QLineEdit>        // Text input
#include <QVBoxLayout>      // Layout
#include <QTimer>           // Timer
#include <QThread>          // Threading
#include <QNetworkAccessManager>  // Network
#include <QSqlDatabase>     // Database
```

## Common CMake Components

```cmake
find_package(Qt6 REQUIRED COMPONENTS
    Core        # Core non-GUI functionality
    Gui         # Window system, events
    Widgets     # UI widgets
    Network     # Network programming
    Sql         # SQL database
    Xml         # XML/SAX/DOM parsers
    Concurrent  # Threading utilities
)
```

## Common Qt6 Modules

- **Qt6::Core** - Core functionality
- **Qt6::Gui** - Windowing, events, 2D graphics
- **Qt6::Widgets** - UI widgets
- **Qt6::Quick** - QML framework
- **Qt6::Network** - Network APIs
- **Qt6::Sql** - SQL database
- **Qt6::Xml** - XML processing
- **Qt6::Test** - Unit testing framework
- **Qt6::Concurrent** - Threading utilities
