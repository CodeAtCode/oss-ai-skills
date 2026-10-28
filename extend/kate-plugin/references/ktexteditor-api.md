> Loaded on demand from SKILL.md when the agent needs KTextEditor API class reference.

# KTextEditor API Reference

This file catalogs KTextEditor classes and methods for reference. See SKILL.md for procedural rules about when and how to use them.

## Document API

```cpp
#include <KTextEditor/Document>
#include <KTextEditor/View>
#include <KTextEditor/Range>
#include <KTextEditor/Cursor>

class DocumentHandler {
public:
    explicit DocumentHandler(KTextEditor::Document *doc) : m_doc(doc) {}
    void insertText(const KTextEditor::Cursor &cur, const QString &text) { m_doc->insertText(cur, text); }
    void replaceText(const KTextEditor::Range &range, const QString &text) { m_doc->replaceText(range, text); }
    QString getText() const { return m_doc->text(); }
    QString getLine(int n) const { return m_doc->line(n); }
    int lineCount() const { return m_doc->lines(); }
    KTextEditor::Range search(const QString &pat, const KTextEditor::Cursor &start) { return m_doc->searchText(pat, start); }
private:
    KTextEditor::Document *m_doc;
};
```

## View API

```cpp
class ViewHandler {
public:
    explicit ViewHandler(KTextEditor::View *view) : m_view(view) {}
    KTextEditor::Cursor getCursorPosition() const { return m_view->cursorPosition(); }
    void setCursorPosition(int line, int col) { m_view->setCursorPosition(line, col); }
    QString getSelection() const { return m_view->selectionText(); }
    void setSelection(const KTextEditor::Range &range) { m_view->setSelection(range); }
    void clearSelection() { m_view->clearSelection(); }
    void toggleFolding(const KTextEditor::Range &range) { m_view->toggleFolding(range); }
private:
    KTextEditor::View *m_view;
};
```

## Position Utilities

```cpp
void positions(KTextEditor::Document *doc) {
    KTextEditor::Cursor cursor(10, 5);
    KTextEditor::Range range(10, 0, 10, 20);
    if (range.isValid()) { QString text = range.text(doc); bool contains = range.contains(cursor); }
}
```
