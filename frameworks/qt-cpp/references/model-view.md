> Loaded on demand from `SKILL.md` when the agent needs model/view programming patterns.

# Model/View Programming Reference

## QAbstractListModel

```cpp
#include <QAbstractListModel>
#include <QVector>

class TodoModel : public QAbstractListModel {
    Q_OBJECT
public:
    enum Roles {
        TextRole = Qt::UserRole + 1,
        DoneRole
    };

    explicit TodoModel(QObject *parent = nullptr)
        : QAbstractListModel(parent) {}

    int rowCount(const QModelIndex &parent = QModelIndex()) const override {
        Q_UNUSED(parent);
        return m_todos.size();
    }

    QVariant data(const QModelIndex &index, int role) const override {
        if (!index.isValid() || index.row() >= m_todos.size())
            return QVariant();

        const Todo &todo = m_todos[index.row()];

        switch (role) {
        case TextRole:
            return todo.text;
        case DoneRole:
            return todo.done;
        default:
            return QVariant();
        }
    }

    QHash<int, QByteArray> roleNames() const override {
        QHash<int, QByteArray> roles;
        roles[TextRole] = "text";
        roles[DoneRole] = "done";
        return roles;
    }

    Q_INVOKABLE void add(const QString &text) {
        beginInsertRows(QModelIndex(), m_todos.size(), m_todos.size());
        m_todos.append({text, false});
        endInsertRows();
    }

    Q_INVOKABLE void remove(int index) {
        if (index < 0 || index >= m_todos.size())
            return;

        beginRemoveRows(QModelIndex(), index, index);
        m_todos.removeAt(index);
        endRemoveRows();
    }

    Q_INVOKABLE void toggle(int index) {
        if (index < 0 || index >= m_todos.size())
            return;

        m_todos[index].done = !m_todos[index].done;
        emit dataChanged(createIndex(index, 0),
                        createIndex(index, 0),
                        {DoneRole});
    }

private:
    struct Todo {
        QString text;
        bool done;
    };

    QVector<Todo> m_todos;
};
```

## QML ListView with Model

```qml
import QtQuick 2.15
import QtQuick.Controls 2.15

ListView {
    width: 400
    height: 500
    model: todoModel
    delegate: ItemDelegate {
        width: ListView.view.width
        height: 50

        CheckBox {
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            checked: model.done
            onClicked: todoModel.toggle(index)
        }

        Text {
            anchors.left: checkbox.right
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            text: model.text
            elide: Text.ElideRight
        }
    }

    Button {
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        text: "Add"
        onClicked: todoModel.add("New todo")
    }
}
```
