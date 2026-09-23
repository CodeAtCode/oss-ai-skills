<!-- Loaded on demand from ../SKILL.md — Tree-sitter Language Support deep dive -->

## Language Support (Tree-sitter)

### Language config.toml

Place in `languages/my-language/`:

```toml
name = "My Language"
grammar = "my-language"               # Must match grammar name in extension.toml
path_suffixes = ["myl", "mylang"]     # File extensions
line_comments = ["// ", "# "]          # Line comment prefixes
block_comments = [{ start = "/*", end = "*/" }]
tab_size = 4
hard_tabs = false
first_line_pattern = "^#!.*myl"       # Shebang detection
word_characters = ["#", "$", "-"]     # Non-alpha chars that are part of words

# Bracket auto-closing configuration
brackets = [
    { start = "{", end = "}", close = true, newline = true },
    { start = "(", end = ")", close = true, newline = true },
    { start = "[", end = "]", close = true, newline = true },
    { start = "\"", end = "\"", close = true, newline = false, not_in = ["string"] },
]

# Scope-specific overrides
[overrides.string]
completion_query_characters = ["-", "."]
```

### Tree-sitter Query Files

All `.scm` files go in `languages/my-language/`.

#### highlights.scm — Syntax Highlighting

```scheme
(string) @string
(comment) @comment
(number) @number
(keyword) @keyword
(function name: (identifier) @function)
(type_identifier) @type
(identifier) @variable
(property_identifier) @property
(operator) @operator
(constant) @constant
(boolean) @boolean
```

**Supported captures:**
| Capture | Description |
|---------|-------------|
| `@string` | String literals |
| `@string.escape` | Escaped characters |
| `@string.regex` | Regular expressions |
| `@string.special` | Special strings |
| `@comment` | Comments |
| `@comment.doc` | Doc comments |
| `@keyword` | Keywords |
| `@number` | Numeric values |
| `@boolean` | Boolean values |
| `@function` | Functions |
| `@type` | Types |
| `@type.builtin` | Built-in types |
| `@variable` | Variables |
| `@variable.special` | Special variables |
| `@variable.parameter` | Parameters |
| `@property` | Properties |
| `@operator` | Operators |
| `@constant` | Constants |
| `@constant.builtin` | Built-in constants |
| `@constructor` | Constructors |
| `@attribute` | Attributes |
| `@tag` | Tags |
| `@label` | Labels |
| `@punctuation` | Punctuation |
| `@punctuation.bracket` | Brackets |
| `@punctuation.delimiter` | Delimiters |
| `@preproc` | Preprocessor directives |
| `@embedded` | Embedded content |
| `@enum` | Enumerations |
| `@variant` | Variants |

**Fallback captures:** Multiple captures on same node define fallback highlights:
```scheme
(type_identifier) @type @variable
```
Zed resolves right-to-left: tries `@variable` first, falls back to `@type`.

#### brackets.scm — Bracket Matching

```scheme
("{" @open "}" @close)
("[" @open "]" @close)
("(" @open ")" @close)
("\"" @open "\"" @close) (#set! rainbow.exclude)  ; Exclude from rainbow brackets
```

#### outline.scm — Code Outline

```scheme
(function_definition name: (identifier) @name) @item
(class_definition name: (identifier) @name) @item
(method_definition name: (identifier) @name) @item
```

Captures: `@name` (item name), `@item` (entire item), `@context` (context info), `@annotation` (decorators, doc comments).

#### indents.scm — Auto-Indentation

```scheme
(array "]" @end) @indent
(object "}" @end) @indent
(function_definition body: (block "{" @indent))
```

#### injections.scm — Language Injections

```scheme
(fenced_code_block
    (info_string (language) @injection.language)
    (code_fence_content) @injection.content)

((string_content) @injection.content
    (#set! injection.language "sql"))
```

#### textobjects.scm — Vim Text Objects

```scheme
(method_definition
    body: (_
        "{"
        (_)* @function.inside
        "}")) @function.around

(class_definition
    body: (_
        "{"
        (_)* @class.inside
        "}")) @class.around

(comment)+ @comment.around
```

Captures: `@function.around`, `@function.inside`, `@class.around`, `@class.inside`, `@comment.around`, `@comment.inside`.

#### redactions.scm — Screen Share Privacy

```scheme
(pair value: (string) @redact)
(pair value: (number) @redact)
(password_field) @redact
```

#### runnables.scm — Runnable Code Detection

```scheme
(
    (document
        (object
            (pair
                key: (string (string_content) @_name
                    (#eq? @_name "scripts"))
                value: (object
                    (pair
                        key: (string (string_content) @run))
                    )
                )
            )
        )
    )
)
```

Extra captures (except `_` prefixed) become `ZED_CUSTOM_<capture_name>` env vars.