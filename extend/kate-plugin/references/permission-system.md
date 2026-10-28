> Loaded on demand from SKILL.md when the agent needs permission system patterns.

# Permission System Reference

Generic permission management patterns for Kate plugins.

```cpp
#include <QSet>

enum class Permission { ReadDocument, WriteDocument, AccessNetwork };

class PermissionManager {
public:
    enum class Decision { Granted, Denied, Pending };
    Decision requestPermission(Permission perm, const QString &reason) {
        if (m_granted.contains(perm)) return Decision::Granted;
        emit permissionRequested(perm, reason);
        return Decision::Pending;
    }
    void grantPermission(Permission perm) { m_granted.insert(perm); emit permissionGranted(perm); }
    void denyPermission(Permission perm) { m_denied.insert(perm); emit permissionDenied(perm); }
    bool hasPermission(Permission perm) const { return m_granted.contains(perm); }
signals:
    void permissionRequested(Permission perm, const QString &reason);
    void permissionGranted(Permission perm);
    void permissionDenied(Permission perm);
private:
    QSet<Permission> m_granted, m_denied;
};

class DocumentAccessController {
public:
    explicit DocumentAccessController(PermissionManager *pm) : m_permManager(pm) {}
    void requestWriteAccess(const QString &reason) {
        auto decision = m_permManager->requestPermission(Permission::WriteDocument, reason);
        if (decision == PermissionManager::Decision::Granted) performWrite();
    }
private:
    void performWrite() {}
    PermissionManager *m_permManager;
};

class PluginActions : public QObject {
    Q_OBJECT
public:
    explicit PluginActions(KTextEditor::MainWindow *mainWindow, PermissionManager *pm)
        : QObject(mainWindow), m_mainWindow(mainWindow), m_permManager(pm) {
        auto *action = m_mainWindow->actionCollection()->addAction("write");
        connect(action, &KAction::triggered, this, &PluginActions::onWriteRequested);
    }
private slots:
    void onWriteRequested() {
        if (!m_permManager->hasPermission(Permission::WriteDocument)) {
            m_permManager->requestPermission(Permission::WriteDocument, "Needs write access"); return;
        }
        performWrite();
    }
    void performWrite() {}
private:
    KTextEditor::MainWindow *m_mainWindow; PermissionManager *m_permManager;
};
```
