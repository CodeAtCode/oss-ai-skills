> Loaded on demand from SKILL.md when the agent needs JSON configuration utility patterns.

# JSON Configuration Utilities

Generic JSON loading/saving patterns for Kate plugins.

```cpp
#include <QJsonObject>
#include <QJsonDocument>
#include <QFile>

QJsonObject loadConfig(const QString &path) {
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) return {};
    QJsonParseError error;
    QJsonDocument doc = QJsonDocument::fromJson(file.readAll(), &error);
    return doc.object();
}

void saveConfig(const QString &path, const QJsonObject &config) {
    QFile file(path);
    if (file.open(QIODevice::WriteOnly)) file.write(QJsonDocument(config).toJson(QJsonDocument::Indented));
}
```
