> Loaded on demand from SKILL.md when the agent needs KConfig configuration patterns.

# KConfig Configuration Reference

KSharedConfig and KConfigGroup usage patterns for Kate plugins.

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
