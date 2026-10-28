> Loaded on demand from SKILL.md when the agent needs complete main.qml template or representation patterns.

# QML UI Reference

## Complete main.qml Template

```qml
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components 3.0 as PlasmaComponents3
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.0 as Kirigami
import com.example.widget 1.0

PlasmoidItem {
    id: root
    
    // Backend instance
    WidgetBackend {
        id: backend
    }
    
    // Full representation (expanded widget)
    Plasmoid.fullRepresentation: Kirigami.Card {
        implicitWidth: Kirigami.Units.gridUnit * 20
        implicitHeight: Kirigami.Units.gridUnit * 15
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Kirigami.Units.smallSpacing
            spacing: Kirigami.Units.smallSpacing
            
            PlasmaComponents3.Label {
                text: Plasmoid.configuration.customLabel || "My Widget"
                font.bold: true
                Layout.fillWidth: true
            }
            
            PlasmaComponents3.Label {
                text: backend.data
                Layout.fillWidth: true
            }
            
            PlasmaComponents3.Button {
                text: "Refresh"
                onClicked: backend.refresh()
            }
        }
    }
    
    // Compact representation (panel icon)
    Plasmoid.compactRepresentation: PlasmaCore.IconItem {
        source: Plasmoid.icon
        anchors.centerIn: parent
        
        implicitWidth: Kirigami.Units.iconSizes.medium
        implicitHeight: implicitWidth
        
        MouseArea {
            anchors.fill: parent
            onClicked: Plasmoid.expanded = !Plasmoid.expanded
        }
    }
    
    Plasmoid.toolTipMainText: "My Widget"
    Plasmoid.toolTipSubText: backend.data
    Plasmoid.icon: "utilities-system-monitor"
}
```
