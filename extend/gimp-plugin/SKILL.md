---
name: gimp-plugin
description: Use when developing GIMP 3.0+ plugins in Python 3 - procedure registration, image and layer operations, GEGL operations, PDB calls, dialogs and progress bars, file export, or batch processing plugins
metadata:
  author: mte90
  version: 2.0.0
  tags:
    - python
    - gimp
    - image-processing
    - graphics
    - plugin
---

> **Objective:** Use this skill to reduce PDB-call-typed errors, image-ref-leak crashes, GEGL-op-misuse bugs, and batch-mode failures by enforcing procedure-registration discipline, image-lifecycle rules, GEGL-pipeline patterns, and batch-run-mode checks.

# GIMP Plugin Development

Complete guide for developing GIMP 3.0+ plugins with Python 3.

## Overview

GIMP (GNU Image Manipulation Program) supports plugins written in Python 3. GIMP 3.0 introduced significant API changes, GEGL-based image processing, and modern Python integration.

**Key Features:**
- Python 3 scripting (no longer Python 2)
- GEGL (Generic Graphics Library) for image operations
- New procedure registration system
- GTK 3 dialog support
- Access to all GIMP internal procedures

### GIMP 3.0+ Requirements

```bash
# Check GIMP version
gimp --version  # GIMP 3.0.0 or higher

# Python 3 is bundled with GIMP
# Plugins use the Python interpreter included with GIMP
```

### Plugin Locations

```
# User plugins (preferred)
 ~/.config/GIMP/3.0/plug-ins/

# System plugins
/usr/lib/gimp/3.0/plug-ins/

# Windows
%APPDATA%\GIMP\3.0\plug-ins\

# macOS
~/Library/Application Support/GIMP/3.0/plug-ins/
```

### Plugin File Structure

```
my_plugin/
├── my_plugin.py           # Main plugin file (must be executable on Linux)
└── __pycache__/           # Python cache (auto-generated)
```

```bash
# Make plugin executable (Linux/macOS)
chmod +x ~/.config/GIMP/3.0/plug-ins/my_plugin.py
```

## Basic Plugin Structure

### Minimal Plugin

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
from gi.repository import GObject
from gi.repository import GLib

def my_plugin(procedure, run_mode, image, n_drawables, drawables, args, data):
    """Main plugin function."""
    Gimp.message("Hello from my plugin!")
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

class MyPlugin(Gimp.PlugIn):
    ## Gimp.PlugIn virtual methods ##
    
    def do_query_procedures(self):
        """Return list of procedure names."""
        return ["plug-in-my-plugin"]
    
    def do_create_procedure(self, name):
        """Create procedure definition."""
        procedure = Gimp.ImageProcedure.new(
            self, name,
            Gimp.PDBProcType.PLUGIN,
            my_plugin, None
        )
        procedure.set_image_types("RGB*")
        procedure.set_documentation(
            "My Plugin Description",
            "Detailed help text",
            name
        )
        procedure.set_menu_label("My Plugin")
        procedure.add_menu_path("<Image>/Filters/Custom/")
        procedure.set_attribution("Author", "Author", "2024")
        
        return procedure

Gimp.main(MyPlugin.__gtype__, sys.argv)
```

### Plugin with Parameters

```python
#!/usr/bin/env python3

import gi
gi.require_version('Gimp', '3.0')
gi.require_version('Gegl', '0.4')
from gi.repository import Gimp, Gegl, GObject, GLib

def my_filter(procedure, run_mode, image, n_drawables, drawables, args, data):
    """Apply filter with user parameters."""
    # Get parameters
    blur_amount = args.index(0)
    opacity = args.index(1)
    
    # Get active drawable (layer)
    drawable = drawables[0]
    
    # Apply GEGL operation
    Gimp.drawable_filter_new(drawable, "gegl:gaussian-blur")
    
    # Update image
    Gimp.displays_flush()
    
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

class MyFilterPlugin(Gimp.PlugIn):
    def do_query_procedures(self):
        return ["plug-in-my-filter"]
    
    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(
            self, name,
            Gimp.PDBProcType.PLUGIN,
            my_filter, None
        )
        procedure.set_image_types("RGB*, GRAY*")
        procedure.set_documentation(
            "Apply custom blur filter",
            "Applies a configurable blur to the image",
            name
        )
        procedure.set_menu_label("My Blur Filter")
        procedure.add_menu_path("<Image>/Filters/Blur/")
        
        # Add parameters
        procedure.add_argument_from_property(
            GObject.Value(GObject.TYPE_DOUBLE),
            "blur-amount",
            "Blur Amount",
            "Radius of the blur",
            0.0, 100.0, 5.0
        )
        procedure.add_argument_from_property(
            GObject.Value(GObject.TYPE_DOUBLE),
            "opacity",
            "Opacity",
            "Filter opacity (0-100)",
            0.0, 100.0, 100.0
        )
        
        return procedure

Gimp.main(MyFilterPlugin.__gtype__, sys.argv)
```

## Procedure Registration (Critical Patterns)

**Do validate procedure names at registration** because typos fail silently at runtime and the plugin appears unregistered.

**Do set `set_image_types()` correctly** because mismatched types cause GIMP to hide the plugin from unsupported images.

**Do use `add_argument_from_property()` for parameter binding** because it auto-generates UI widgets and validates types.

See `references/image-operations.md` for complete procedure types, menu paths, image type specifiers, and parameter API.

## Deep Dives

- **Image Operations, GEGL, and PDB** — `references/image-operations.md`: Drawable access, layer operations, selections, pixel access, GEGL operation graphs, and PDB procedure calls
- **User Interface and Files** — `references/ui-and-files.md`: GTK dialogs, color pickers, file dialogs, progress bars, file load/save operations
- **Complete Examples** — `references/complete-examples.md`: Full plugin implementations (batch resize, artistic filter)

## Critical Rules (Do X Because Y)

**Do check run_mode before showing dialogs** because batch scripts fail when interactive dialogs block non-interactive execution.

```python
if run_mode == Gimp.RunMode.NONINTERACTIVE:
    # Skip dialogs, use defaults
    blur_radius = 5
else:
    # Show dialog
    blur_radius = show_settings_dialog()
```

**Do call `Gimp.displays_flush()` after drawable changes** because GIMP won't refresh the canvas otherwise, leaving users seeing stale data.

**Do wrap operations in undo groups** because single-step undo prevents users from reverting multi-operation plugins.

```python
Gimp.image_undo_group_start(image)
try:
    # Multiple layer operations
    pass
finally:
    Gimp.image_undo_group_end(image)
```

**Do return proper error values with `procedure.new_return_values()`** because returning bare values breaks GIMP's procedure result parsing.

**Do catch exceptions and return `EXECUTION_ERROR`** because uncaught exceptions crash the Python interpreter without reporting the error to GIMP.

**Do run GIMP from terminal** because stderr output (print statements, tracebacks) only appears there, not in the GUI console.

```bash
gimp                    # See print() output
G_MESSAGES_DEBUG=all gimp  # See GLib/GObject debug messages
```

**Do use `Gimp.message()` for user-facing errors** because it displays in GIMP's interface while `print()` only goes to terminal.

**Do check run_mode before showing dialogs** because batch scripts fail when interactive dialogs block non-interactive execution.

```python
if run_mode == Gimp.RunMode.NONINTERACTIVE:
    # Skip dialogs, use defaults
    blur_radius = 5
else:
    # Show dialog
    blur_radius = show_settings_dialog()
```

**Do call `Gimp.displays_flush()` after drawable changes** because GIMP won't refresh the canvas otherwise, leaving users seeing stale data.

**Do wrap operations in undo groups** because single-step undo prevents users from reverting multi-operation plugins.

```python
Gimp.image_undo_group_start(image)
try:
    # Multiple layer operations
    pass
finally:
    Gimp.image_undo_group_end(image)
```

**Do return proper error values with `procedure.new_return_values()`** because returning bare values breaks GIMP's procedure result parsing.

**Do catch exceptions and return `EXECUTION_ERROR`** because uncaught exceptions crash the Python interpreter without reporting the error to GIMP.

## Debugging

**Do run GIMP from terminal** because stderr output (print statements, tracebacks) only appears there, not in the GUI console.

```bash
gimp                    # See print() output
G_MESSAGES_DEBUG=all gimp  # See GLib/GObject debug messages
```
