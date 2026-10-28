> Loaded on demand from `SKILL.md` when the agent needs signal/slot connection syntax and patterns.

# Signals and Slots Reference

## Basic Signal-Slot Connection

```cpp
// sender.h
#include <QObject>
#include <QTimer>

class Sender : public QObject {
    Q_OBJECT
public:
    explicit Sender(QObject *parent = nullptr) : QObject(parent) {
        m_timer = new QTimer(this);
        connect(m_timer, &QTimer::timeout, this, &Sender::timeout);
        m_timer->start(1000);
    }

signals:
    void timeout();
    void progress(int value);

private:
    QTimer *m_timer;
};

// receiver.h
#include <QObject>

class Receiver : public QObject {
    Q_OBJECT
public slots:
    void handleTimeout() {
        qDebug() << "Timeout received!";
    }

    void handleProgress(int value) {
        qDebug() << "Progress:" << value;
    }
};

// main.cpp
int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);

    Sender sender;
    Receiver receiver;

    // Qt5 connection syntax
    QObject::connect(&sender, SIGNAL(timeout()),
                     &receiver, SLOT(handleTimeout()));

    // Qt6 modern connection syntax (recommended)
    QObject::connect(&sender, &Sender::timeout,
                     &receiver, &Receiver::handleTimeout);

    return app.exec();
}
```

## Lambda Connections

```cpp
class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    MainWindow(QWidget *parent = nullptr) : QMainWindow(parent) {
        QPushButton *button = new QPushButton("Click me", this);

        // Lambda with capture
        connect(button, &QPushButton::clicked, this, [this]() {
            handleButtonClick();
        });

        // Lambda with parameters
        connect(button, &QPushButton::clicked, this, [=](bool checked) {
            qDebug() << "Button clicked:" << checked;
        });

        // Lambda with context object
        connect(button, &QPushButton::clicked,
                this, [this]() {
                    this->handleButtonClick();
                },
                Qt::QueuedConnection);
    }

private:
    void handleButtonClick() {
        qDebug() << "Button clicked!";
    }
};
```

## Connection Types

```cpp
// Auto Connection (default)
connect(sender, &Sender::signal, receiver, &Receiver::slot);
// Uses DirectConnection if receiver and sender are in same thread
// Uses QueuedConnection otherwise

// Direct Connection (same thread only)
connect(sender, &Sender::signal, receiver, &Receiver::slot,
        Qt::DirectConnection);
// Slot executes immediately in sender's thread

// Queued Connection (different threads)
connect(sender, &Sender::signal, receiver, &Receiver::slot,
        Qt::QueuedConnection);
// Slot executes in receiver's thread event loop

// Unique Connection (prevents duplicates)
connect(sender, &Sender::signal, receiver, &Receiver::slot,
        Qt::UniqueConnection);

// Blocking Queued Connection (blocks sender until slot finishes)
connect(sender, &Sender::signal, receiver, &Receiver::slot,
        Qt::BlockingQueuedConnection);
```

## Signal Forwarding

```cpp
class Relay : public QObject {
    Q_OBJECT
public:
    explicit Relay(QObject *parent = nullptr) : QObject(parent) {}

    // Relay signals
    void relaySignal(int value) {
        emit forwarded(value);
    }

signals:
    void forwarded(int value);
};

// Usage
Source source;
Relay relay;
Destination dest;

connect(&source, &Source::data, &relay, &Relay::relaySignal);
connect(&relay, &Relay::forwarded, &dest, &Destination::handleData);
```
