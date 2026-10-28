> Loaded on demand from `SKILL.md` when the agent needs Qt 6 specific API features.

# Qt 6 Specific Features Reference

## QString UTF-8 by Default

```cpp
// Qt5: UTF-16
QString text = "Hello";  // Internally UTF-16
QByteArray bytes = text.toUtf8();  // Need explicit conversion

// Qt6: UTF-8 by default
QString text = "Hello";  // Internally UTF-8
QByteArray bytes = text.toLatin1();  // Need explicit conversion for Latin-1
```

## New Graphics Stack

```cpp
// Qt6 uses RHI (Rendering Hardware Interface)
// Supports Vulkan, Metal, Direct3D 11/12, OpenGL

// For Qt Quick 3D
import QtQuick3D 6.0

Model {
    id: cube
    source: "#Cube"
    scale: Qt.vector3d(2, 2, 2)
}

Node {
    Model {
        id: sceneModel
        source: "#Rectangle"
        scale: Qt.vector3d(10, 10, 1)
        materials: PrincipledMaterial {
            baseColor: "green"
        }
    }
}
```

## Properties

```cpp
// Qt6 properties (similar to Q_PROPERTY but simpler)
class Counter : public QObject {
    Q_OBJECT
    Q_PROPERTY(int value READ value WRITE setValue NOTIFY valueChanged FINAL)

    QML_ELEMENT  // Register for QML

public:
    int value() const { return m_value; }
    void setValue(int value) {
        if (m_value != value) {
            m_value = value;
            emit valueChanged();
        }
    }

    // Property binding (Qt6 feature)
    Q_PROPERTY(int doubled READ doubled NOTIFY valueChanged FINAL)
    int doubled() const { return m_value * 2; }

signals:
    void valueChanged();

private:
    int m_value = 0;
};
```
