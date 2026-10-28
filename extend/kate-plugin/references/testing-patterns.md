> Loaded on demand from SKILL.md when the agent needs QTest patterns for Kate plugins.

# Testing Patterns for Kate Plugins

QTest patterns and mock interfaces for testing Kate plugins.

## Document Handler Tests

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
```

## Mock Interfaces

```cpp
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
```

## Thread Tests

```cpp
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
```

## CMake Test Configuration

```cmake
enable_testing()
find_package(Qt5 REQUIRED COMPONENTS Test)
add_executable(test_myplugin test_main.cpp test_document_handler.cpp test_agent_thread.cpp)
target_link_libraries(test_myplugin PRIVATE Qt5::Test KF5::KTextEditor myplugin)
add_test(NAME myplugin_tests COMMAND test_myplugin)
```
