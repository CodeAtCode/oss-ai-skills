> Loaded on demand from SKILL.md when the agent needs C++ interface-based design patterns.

# Interface-Based Design Patterns

Generic C++ interface patterns for thread-safe storage and dependency injection in Kate plugins.

## Thread Storage Interface

```cpp
#include <memory>
#include <QString>
#include <QVariant>

class IThreadStorage {
public:
    virtual ~IThreadStorage() = default;
    virtual void store(const QString &key, const QVariant &value) = 0;
    virtual QVariant retrieve(const QString &key) = 0;
    virtual bool has(const QString &key) = 0;
    virtual void remove(const QString &key) = 0;
    virtual void clear() = 0;
};

class JsonThreadStorage : public IThreadStorage {
public:
    explicit JsonThreadStorage(const QString &filePath) : m_filePath(filePath) { load(); }
    void store(const QString &key, const QVariant &value) override { m_data[key] = QJsonValue::fromVariant(value); save(); }
    QVariant retrieve(const QString &key) override { return m_data.contains(key) ? m_data[key].toVariant() : QVariant(); }
    bool has(const QString &key) override { return m_data.contains(key); }
    void remove(const QString &key) override { m_data.remove(key); save(); }
    void clear() override { m_data = QJsonObject(); save(); }
private:
    void load() { QFile f(m_filePath); if (f.open(QIODevice::ReadOnly)) m_data = QJsonDocument::fromJson(f.readAll()).object(); }
    void save() { QFile f(m_filePath); if (f.open(QIODevice::WriteOnly)) f.write(QJsonDocument(m_data).toJson()); }
    QString m_filePath; QJsonObject m_data;
};

class MemoryThreadStorage : public IThreadStorage {
public:
    void store(const QString &key, const QVariant &value) override { m_data[key] = value; }
    QVariant retrieve(const QString &key) override { return m_data.value(key); }
    bool has(const QString &key) override { return m_data.contains(key); }
    void remove(const QString &key) override { m_data.remove(key); }
    void clear() override { m_data.clear(); }
private:
    QMap<QString, QVariant> m_data;
};
```

## Service Pattern

```cpp
class AgentService {
public:
    explicit AgentService(std::unique_ptr<IThreadStorage> storage) : m_storage(std::move(storage)) {}
    void runAgent(const QString &taskId) { m_storage->store("lastTask", taskId); m_storage->store("lastResult", processTask(taskId)); }
private:
    QString processTask(const QString &id) { return "Processed: " + id; }
    std::unique_ptr<IThreadStorage> m_storage;
};
```
