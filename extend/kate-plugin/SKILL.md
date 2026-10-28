---
name: kate-plugin
description: Use when developing C++ plugins for Kate - KTextEditor Framework, CMake/ECM, Qt threading, KDE plugin architecture
metadata:
  author: mte90
  version: 2.0.1
  tags:
    - kate
    - kde
    - text-editor
    - plugin
    - c++
    - qt
    - kde-frameworks
---

> **Objective:** Use this skill to reduce plugin-load failures, CMake-link errors, and thread-assertion violations by enforcing ECM-target discipline, Qt-thread rules, and KPlugin registration patterns below.

# Kate Plugin Development

C++ plugins for Kate using KTextEditor Framework, KDE Frameworks, and Qt.

## Overview

Kate plugins extend functionality through C++ using KTextEditor framework.

```
/usr/share/kate/plugins/    # System
~/.local/share/kate/plugins/ # User
```

## Plugin Architecture

```cpp
#include <KPluginFactory>
#include <KTextEditor/Plugin>

class MyPlugin : public KTextEditor::Plugin {
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "org.kde.KTextEditor.Plugin" FILE "metadata.json")
public:
    explicit MyPlugin(QObject *parent, const QVariantList &)
        : KTextEditor::Plugin(parent) {}
    ~MyPlugin() override = default;

    QWidget *createConfigWidget(QWidget *p) override { return new ConfigWidget(p); }
    void readConfig(KConfigGroup &g) override { m_enabled = g.readEntry("Enabled", true); }
    void writeConfig(KConfigGroup &g) override { g.writeEntry("Enabled", m_enabled); }
    void init() override {}
    void addView(KTextEditor::MainWindow *mw) override {
        auto *v = mw->activeView();
        if (v) connect(v->document(), &KTextEditor::Document::textChanged, this, &MyPlugin::onTextChanged);
    }
    void removeView(KTextEditor::MainWindow *) override {}
private slots:
    void onTextChanged(KTextEditor::Document *doc) { qDebug() << doc->url(); }
private:
    bool m_enabled = true;
};

K_PLUGIN_FACTORY_WITH_JSON(MyPluginFactory, "metadata.json", registerPlugin<MyPlugin>();)
```

```json
{
    "KPlugin": {
        "Name": "My Plugin",
        "Description": "A C++ plugin for Kate",
        "Icon": "kate",
        "Authors": [{"Name": "Dev", "Email": "dev@example.com"}],
        "Version": "1.0.0",
        "License": "GPL-2.0-or-later",
        "ServiceTypes": ["KTextEditor/Plugin"],
        "Category": "Language"
    },
    "X-KTextEditor": {"APIVersion": "5"}
}
```

```cmake
cmake_minimum_required(VERSION 3.16)
project(myplugin VERSION 1.0.0)
set(CMAKE_CXX_STANDARD 17)
find_package(ECM 5.90 REQUIRED NO_MODULE)
find_package(KF5 REQUIRED COMPONENTS CoreAddons Config KTextEditor WidgetsAddons)
include(KDEInstallDirs)
include(KDECMakeSettings)

kcoreaddons_add_plugin(myplugin INSTALL_NAMESPACE "kate"
    SOURCES myplugin.cpp configwidget.cpp
    LIBRARIES KF5::CoreAddons KF5::ConfigGui KF5::KTextEditor)
install(FILES metadata.json DESTINATION ${KDE_INSTALL_KTPLUGINDIR}/myplugin)
```

See references/ktexteditor-api.md for KTextEditor class catalogs and API usage patterns.

## CMake Build System

```cmake
cmake_minimum_required(VERSION 3.16)
project(myplugin VERSION 1.0.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
find_package(ECM 5.90 REQUIRED NO_MODULE)
find_package(KF5 REQUIRED COMPONENTS CoreAddons Config KTextEditor WidgetsAddons)
include(KDEInstallDirs)
include(KDECMakeSettings)
include(KDECompilerSettings)

kcoreaddons_add_plugin(myplugin INSTALL_NAMESPACE "kate"
    SOURCES main.cpp myplugin.cpp configwidget.cpp
    LIBRARIES KF5::CoreAddons KF5::ConfigGui KF5::KTextEditor)

enable_testing()
find_package(Qt5 REQUIRED COMPONENTS Test)
qt5_add_tests(test_myplugin SOURCES test_myplugin.cpp LIBRARIES Qt5::Test KF5::KTextEditor)

install(TARGETS myplugin LIBRARY DESTINATION ${KDE_INSTALL_KTPLUGINDIR}/myplugin)
install(FILES metadata.json DESTINATION ${KDE_INSTALL_KTPLUGINDIR}/myplugin)
```

See references/json-config-utils.md for JSON configuration utility patterns.

## Threaded Agent Architecture

```cpp
#include <QThread>
#include <QQueue>
#include <QMutex>
#include <QWaitCondition>

class AgentThread : public QThread {
    Q_OBJECT
public:
    explicit AgentThread(QObject *parent = nullptr) : QThread(parent), m_running(true) {}
    ~AgentThread() override { m_running = false; m_condition.wakeOne(); wait(); }
    void enqueueTask(const QString &task) { QMutexLocker locker(&m_mutex); m_tasks.enqueue(task); m_condition.wakeOne(); }
protected:
    void run() override {
        while (m_running) {
            QMutexLocker locker(&m_mutex);
            while (m_tasks.isEmpty() && m_running) m_condition.wait(&m_mutex);
            if (!m_running) break;
            QString task = m_tasks.dequeue();
            locker.unlock();
            processTask(task);
        }
    }
private:
    void processTask(const QString &task) { emit taskCompleted(task, "Result: " + task); }
signals:
    void taskCompleted(const QString &task, const QString &result);
private:
    QQueue<QString> m_tasks; QMutex m_mutex; QWaitCondition m_condition; bool m_running;
};

class AgentManager : public QObject {
    Q_OBJECT
public:
    explicit AgentManager(QObject *parent = nullptr) : QObject(parent), m_agentThread(new AgentThread(this)) {
        connect(m_agentThread.data(), &AgentThread::taskCompleted, this, &AgentManager::onTaskCompleted, Qt::QueuedConnection);
        m_agentThread->start();
    }
    void enqueueAgentTask(const QString &task) { m_agentThread->enqueueTask(task); }
private slots:
    void onTaskCompleted(const QString &task, const QString &result) { qDebug() << "Task:" << task; emit resultReady(task, result); }
signals:
    void resultReady(const QString &task, const QString &result);
private:
    QScopedPointer<AgentThread> m_agentThread;
};

struct AgentTask { QString id; QString data; };
struct AgentResult { QString id; QString output; };

class AgentLoop : public QObject {
    Q_OBJECT
public:
    explicit AgentLoop(QObject *parent = nullptr) : QObject(parent), m_thread(new QThread(this)) {
        m_processor = new AgentProcessor();
        m_processor->moveToThread(m_thread);
        connect(this, &AgentLoop::taskEnqueued, m_processor, &AgentProcessor::processTask, Qt::QueuedConnection);
        connect(m_processor, &AgentProcessor::taskFinished, this, &AgentLoop::onTaskFinished, Qt::QueuedConnection);
        m_thread->start();
    }
    ~AgentLoop() override { m_thread->quit(); m_thread->wait(); }
    void enqueue(const AgentTask &task) { QMutexLocker locker(&m_mutex); m_queue.enqueue(task); emit taskEnqueued(task); }
private slots:
    void onTaskFinished(const AgentResult &result) {
        emit taskCompleted(result);
        QMutexLocker locker(&m_mutex);
        if (!m_queue.isEmpty()) emit taskEnqueued(m_queue.dequeue());
    }
signals:
    void taskEnqueued(const AgentTask &task);
    void taskCompleted(const AgentResult &result);
private:
    QThread *m_thread; AgentProcessor *m_processor; QQueue<AgentTask> m_queue; QMutex m_mutex;
};
```

See references/interface-patterns.md for C++ interface-based design and thread-safe storage patterns.

## Configuration with KConfig/QSettings

```cpp
#include <KSharedConfig>
#include <KConfigGroup>

class PluginConfig {
public:
    explicit PluginConfig() : m_config(KSharedConfig::openConfig()), m_group(m_config->group("Plugin")) {}
    void load() { m_enabled = m_group.readEntry("Enabled", true); m_maxThreads = m_group.readEntry("MaxThreads", 4); }
    void save() { m_group.writeEntry("Enabled", m_enabled); m_group.writeEntry("MaxThreads", m_maxThreads); m_config->sync(); }
    bool isEnabled() const { return m_enabled; }
    void setEnabled(bool v) { m_enabled = v; }
private:
    KSharedConfigPtr m_config; KConfigGroup m_group;
    bool m_enabled = true; int m_maxThreads = 4;
};

class StructuredConfig {
public:
    QJsonObject toJsonObject() const { QJsonObject obj; obj["enabled"] = m_enabled; QJsonObject t; t["max"] = m_maxThreads; obj["threads"] = t; return obj; }
    void fromJsonObject(const QJsonObject &obj) { m_enabled = obj["enabled"].toBool(true); if (obj.contains("threads")) m_maxThreads = obj["threads"].toObject()["max"].toInt(4); }
private:
    bool m_enabled = true; int m_maxThreads = 4;
};

class ConfigMigrator {
public:
    static void migrate(KConfigGroup &group) {
        int version = group.readEntry("ConfigVersion", 0);
        if (version < 2) { group.writeEntry("Plugin.Enabled", group.readEntry("Enabled", true)); group.writeEntry("ConfigVersion", 2); }
    }
};
```

See references/configuration-reference.md for KConfig configuration patterns.

## Permission System

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

See references/permission-system.md for permission management patterns.

## Testing C++ Plugins

```cpp
#include <QTest>
#include <QObject>

class DocumentHandlerTest : public QObject {
    Q_OBJECT
private slots:
    void testInsertText() {
        KTextEditor::Document *doc = new KTextEditor::Document(nullptr);
        DocumentHandler handler(doc);
        handler.insertText(KTextEditor::Cursor(0, 0), "Hello");
        QCOMPARE(doc->text(), QString("Hello"));
        delete doc;
    }
    void testReplaceText() {
        KTextEditor::Document *doc = new KTextEditor::Document(nullptr);
        doc->setText("Hello World");
        DocumentHandler handler(doc);
        handler.replaceText(KTextEditor::Range(0, 0, 0, 5), "Hi");
        QCOMPARE(doc->text(), QString("Hi World"));
        delete doc;
    }
};
QTEST_APPLESS_MAIN(DocumentHandlerTest)
#include "test_document_handler.moc"

class MockDocument : public QObject {
    Q_OBJECT
public:
    QString text() const { return m_text; }
    void setText(const QString &t) { m_text = t; }
    void insertText(const KTextEditor::Cursor &, const QString &text) { m_text += text; emit textChanged(this); }
signals:
    void textChanged(KTextEditor::Document *doc);
private:
    QString m_text;
};

class AgentThreadTest : public QObject {
    Q_OBJECT
private slots:
    void testTaskProcessing() {
        AgentThread thread; thread.start();
        bool completed = false;
        connect(&thread, &AgentThread::taskCompleted, [&completed](const QString &, const QString &) { completed = true; });
        thread.enqueueTask("test-task");
        QTest::qWait(1000);
        QVERIFY(completed);
        thread.quit(); thread.wait();
    }
};
QTEST_MAIN(AgentThreadTest)
#include "test_agent_thread.moc"

enable_testing()
find_package(Qt5 REQUIRED COMPONENTS Test)
add_executable(test_myplugin test_main.cpp test_document_handler.cpp test_agent_thread.cpp)
target_link_libraries(test_myplugin PRIVATE Qt5::Test KF5::KTextEditor myplugin)
add_test(NAME myplugin_tests COMMAND test_myplugin)
```

See references/testing-patterns.md for QTest patterns and mock interfaces.

## Common Issues

| Issue | Solution |
|-------|----------|
| Plugin not loading | Verify metadata.json and KPluginFactory |
| KTextEditor symbols undefined | Link KF5::KTextEditor |
| Signal/slot not connecting | Ensure Q_OBJECT and moc |
| Crash on addView | Check null view/document |
| Config not persisting | Call KConfigGroup::sync() |
| Thread safety issues | Use Qt::QueuedConnection |
| AgentLoop tasks stuck | Verify task queue and signals |
| Permission requests hanging | Implement async callback |

## Best Practices

- **Do use Q_PLUGIN_METADATA with JSON file** because KPluginLoader skips undeclared factories and the plugin won't load
- **Do check for null pointers on view/document** because KTextEditor APIs assert on invalid pointers
- **Do use Qt::QueuedConnection for cross-thread signals** because GUI updates on non-main threads cause assertion violations
- **Do implement cleanup in removeView() matching addView()** because orphaned connections leak memory and cause double-signal firing
- **Do store config in KConfig with namespaced groups** because unnamespaced keys collide with other plugins
- **Do use smart pointers for interface-based DI** because manual memory management in plugin lifecycles causes use-after-free
- **Do process long tasks in worker threads** because blocking the main thread freezes the Kate UI
- **Do emit results via queued signals for UI updates** because direct signal delivery to GUI objects from worker threads crashes
- **Do use QTest with mock KTextEditor interfaces** because real KTextEditor objects require full Kate initialization
- **Do follow KDE coding style** because inconsistent formatting breaks code review and merge processes

## Deep Dives

See the following references for detailed API catalogs and patterns (loaded on demand):

- **references/ktexteditor-api.md** - KTextEditor class catalogs (Document, View, Range, Cursor)
- **references/json-config-utils.md** - JSON configuration loading/saving utilities
- **references/configuration-reference.md** - KConfig/KSharedConfig patterns and migration
- **references/interface-patterns.md** - C++ interface-based design and thread-safe storage
- **references/permission-system.md** - Permission management and access control patterns
- **references/testing-patterns.md** - QTest patterns and mock interface implementations

## References

- **KTextEditor API**: https://docs.kde.org/stable5/kservice/ktexteditor/
- **KPluginFactory**: https://doc.qt.io/qt-5/qpluginfactory.html
- **KDE Frameworks**: https://kde.org/products/frameworks/
- **Kate Developer**: https://kate-editor.org/development/
- **ECM**: https://community.kde.org/Frameworks/ECM
- **Qt Docs**: https://doc.qt.io/qt-5/
- **KConfig**: https://api.kde.org/frameworks/kconfig/html/
