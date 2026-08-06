---
name: opencode
description: "Develop plugins, tools, and extensions for OpenCode AI coding agent. Covers the real Plugin/Hooks API (v1.18+), tool factory, event system, configuration, build, testing, and the crash-prevention rules learned the hard way."
metadata:
  author: mte90
  version: "2.0.0"
  tags:
    - opencode
    - plugin
    - ai-agent
    - mcp
    - tool-development
---

# OpenCode Plugin Development

Complete, field-tested guide for developing plugins for OpenCode (v1.18+) AI coding agent.

> **Every rule, signature, and pattern below was verified against a real plugin
> (`opencode-auto-resume`) that went through 5 versions and 3 distinct crash
> classes in production.** The "Hard-won rules" sections are non-negotiable —
> violating them silently breaks the host.

---

## Extension Types — When to Use What

| Extension Type | Best For | Example |
|----------------|----------|---------|
| **Plugin (Hooks)** | Event-driven automation, custom tools, recovery logic | Auto-resume stalled sessions, enforce agent selection |
| **Tools** | AI-triggered actions inside a plugin | `task_complete`, `commit`, custom search |
| **MCP Servers** | External service integrations | Databases, GitHub, filesystem, remote APIs |
| **Skills** | Knowledge/prompt templates (this file is one) | Framework patterns, project conventions |
| **Commands** | Interactive slash shortcuts | `/hello`, `/deploy` |
| **Providers** | Custom LLM backends | Alternative API gateways, self-hosted models |

---

## The Plugin Contract (v1.18+) — Read This First

A plugin is an **async function** `(input, options) => Promise<Hooks>`. It is NOT an object with `name`/`version`/`tools` fields — that shape is outdated and the host ignores it.

### Type definition (from `@opencode-ai/plugin/dist/index.d.ts`)

```typescript
export type Plugin = (input: PluginInput, options?: PluginOptions) => Promise<Hooks>

export interface Hooks {
  dispose?: () => Promise<void>
  event?: (input: { event: Event }) => Promise<void>
  config?: (input: Config) => Promise<void>
  tool?: { [key: string]: ToolDefinition }
  auth?: AuthHook
  provider?: ProviderHook
  "chat.message"?: (input: ChatMessageInput) => Promise<void>
  "tool.execute.before"?: (input: ToolExecInput) => Promise<void>
  "tool.execute.after"?: (input: ToolExecInput) => Promise<void>
  "command.execute.before"?: (input: CommandExecInput) => Promise<void>
  "command.execute.after"?: (input: CommandExecInput) => Promise<void>
}
```

### Correct minimal plugin

```typescript
import type { Plugin } from "@opencode-ai/plugin"
import { tool } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async (ctx, options) => {
  return {
    event: async ({ event }) => {
      // handle events
    },
    config: async () => {
      // one-time init
    },
    tool: {
      my_tool: tool({
        description: "Does something useful",
        args: {},
        execute: async (_args, ctx) => "ok",
      }),
    },
  }
}

export default MyPlugin
```

> ⚠️ **`config` hook signature**: `(input: Config) => Promise<void>`. It receives a Config object — you may ignore it but the parameter exists.

---

## 🚨 Hard-Won Rules (violate these and the host crashes)

These rules were discovered through real production crashes. Each one has a regression test in the reference plugin.

### Rule 1 — Only export Plugin-shaped values from the entry module

OpenCode's plugin loader iterates **every** module export via `Object.values(module)` and treats each as a Plugin entrypoint:

```js
// Inside opencode's plugin loader (deobfuscated):
for (let N of Object.values(pluginModule)) {
  if (typeof N !== "function") throw TypeError("Plugin export is not a function")
  const hooks = await N(ctx, options)   // called as a Plugin!
  pluginArray.push(hooks)
}
// later:
for (let N of pluginArray) {
  await N.config?.(config)   // crashes if N is null
}
```

**If any export returns `null` → the host crashes with `null is not an object (evaluating 'N.config')`, surfaced in the TUI as `Unexpected server error. Check server logs for details.`**

#### ✅ Correct

```typescript
// src/index.ts — ONLY Plugin exports
export const MyPlugin: Plugin = async (ctx, options) => { ... }
export default MyPlugin
```

#### 🚫 Wrong — crashes the host

```typescript
// src/index.ts
export function getLastAssistantError(messages) { ... return null }  // called as Plugin, returns null, host crashes
export function backoffMs(attempt) { return 42 }                       // called as Plugin, returns number, host crashes
export const MyPlugin: Plugin = async (ctx, options) => { ... }
export default MyPlugin
```

#### Solution — split utilities into a separate file

```typescript
// src/index.ts — bundle entry, only Plugin exports
export const MyPlugin: Plugin = async (ctx, options) => { ... }
export default MyPlugin

// src/test-utils.ts — NOT the bundle entry; tests import from here
export function getLastAssistantError(messages) { ... }
export function backoffMs(attempt, base, max) { ... }
```

Tests import utilities from `./test-utils`; the bundled `dist/index.js` only exposes the Plugin. Verify with:

```bash
bun -e 'const m = await import("./dist/index.js"); console.log(Object.keys(m))'
# MUST print only: [ "MyPlugin", "default" ]
```

### Rule 2 — Never let an async handler throw unhandled

The `event` hook is called **fire-and-forget** by the host. If `handleEvent()` rejects, it becomes an unhandled promise rejection → bun process exits → OpenCode disappears from the TUI.

#### ✅ Correct

```typescript
return {
  event: async ({ event }) => {
    handleEvent(event).catch((e) => {
      console.error("[my-plugin] handleEvent error:", e)
    })
  },
}
```

Same rule applies to `setInterval(async () => { ... })` bodies — wrap in a `safe()` boundary:

```typescript
async function safe<T>(fn: () => Promise<T>, label: string): Promise<T | undefined> {
  try { return await fn() }
  catch (e) {
    const msg = e instanceof Error ? e.message : String(e)
    console.error(`[my-plugin] ${label}: ${msg}`)
    return undefined
  }
}

setInterval(() => {
  safe(doPeriodicWork, "periodic timer").catch(() => {})
}, 5000)
```

### Rule 3 — Validate event payloads defensively

OpenCode event payloads are **not guaranteed** to match the documented shape. Real-world crashes found:

- `todo.updated` events arrive with `properties.todos` as `{}` (object) or `undefined`, not an array
- `session.status` `properties.status` is always `{ type: "idle" | "busy" | "retry" }` — never a bare string
- Session IDs (`sessionID`) may be missing on some events

#### ✅ Correct — `Array.isArray` before `.map()`/`.filter()`

```typescript
case "todo.updated": {
  const rawTodos = (event.properties as any)?.todos
  const todos: Array<Record<string, unknown>> = Array.isArray(rawTodos) ? rawTodos : []
  w.todos = todos.map((t) => ({ ... }))   // safe
  break
}
```

### Rule 4 — `log()` must never rethrow

If the OpenCode log API itself throws (network/server error), your `log()` helper's `catch` block must not propagate. Otherwise an error inside an error handler escapes:

```typescript
async function log(level: "info" | "warn" | "error", msg: string) {
  try {
    await ctx.client.app.log({ body: { service: "my-plugin", level, message: msg } })
  } catch (e) {
    console.error("[my-plugin] log() failed:", e instanceof Error ? e.message : e)
    // do NOT rethrow
  }
}
```

### Rule 5 — Validate `sid` before every SDK call

Session IDs from events may be empty, `undefined`, or malformed. The SDK throws `Expected 'id' to be a string` if you pass garbage:

```typescript
if (typeof sid !== "string" || !sid.startsWith("ses_")) return
await ctx.client.session.prompt({ path: { id: sid }, body: { ... } })
```

---

## The Context API (`ctx`)

The `ctx` parameter is undocumented but stable across v1.18.x:

```typescript
// ctx.client — API calls
await ctx.client.app.log({
  body: { service: "my-plugin", level: "info", message: "..." }
})

const { data: sessions } = await ctx.client.session.list()
const { data: statusMap } = await ctx.client.session.status()  // Record<sid, {type: "busy"|"idle"|"retry"}>
const messages = await ctx.client.session.messages({ path: { id: sid } })
await ctx.client.session.abort({ path: { id: sid } })
await ctx.client.session.prompt({
  path: { id: sid },
  body: {
    parts: [{ type: "text", text: "continue" }],
    agent,   // optional: preserve selected agent
    model,   // optional: { providerID, modelID }
  },
})

// ctx.ui — toast notifications (TUI)
await ctx.ui.toast({ title: "Done", message: "...", variant: "success" })
```

### `session.status()` return shape

```typescript
// status() returns { data: Record<sid, status> } where status is:
type SessionStatus = { type: "idle" | "busy" | "retry" }
// NEVER a bare string — always access via .type
```

### `session.list()` does NOT include status

The `Session` type from `session.list()` has **no** `status` field. To check if a session is busy, call `session.status()` separately and build a `Record<sid, string>` map.

---

## Event System

Plugins receive Server-Sent Events via the `event` hook. Real event types (v1.18+):

```typescript
return {
  event: async ({ event }) => {
    const type = event.type as string
    const sid = event.sessionID as string | undefined
    const props = event.properties as Record<string, unknown> | undefined

    switch (type) {
      case "session.created":
      case "session.updated":
      case "session.idle":          // legacy alias of session.status=idle
      case "session.interrupted":   // user pressed ESC
        break

      case "session.status": {
        const status = props?.status as { type: string } | undefined
        // status.type in "idle" | "busy" | "retry" | "interrupted"
        break
      }

      case "session.error": {
        const error = props?.error as { name: string; data?: { message: string } } | undefined
        // error.name === "MessageAbortedError" → user pressed ESC
        break
      }

      case "message.updated":
      case "message.part.updated":
        // props?.delta — streaming text delta
        break

      case "todo.updated": {
        // ⚠️ props?.todos may be {} or undefined — validate with Array.isArray
        break
      }

      case "tool.call":
      case "tool.result":
      case "command.executed":
        break
    }
  },
}
```

---

## Subagent Lifecycle Management

Managing subagents spawned from plugins requires careful attention to timeouts, abort handling, and cleanup to prevent runaway processes.

### Spawning Subagents

Use `ctx.client.session.create` with subagent configuration:

```typescript
const subagent = await ctx.client.session.create({
  parentID: ctx.session.id,
  agent: "fixer",
  message: "Fix the failing tests in auth.ts",
})
```

### Timer-Based Abort

The critical pattern for preventing runaway subagents:

```typescript
const TIMEOUT_MS = 60000 // 60 seconds

const subagent = await ctx.client.session.create({ 
  parentID: ctx.session.id,
  agent: "fixer",
  message: "Fix failing tests",
})

const timer = setTimeout(async () => {
  try {
    await ctx.client.session.abort({ id: subagent.id })
    ctx.logger.warn(`Subagent ${subagent.id} aborted after timeout`)
  } catch (error) {
    ctx.logger.error(`Failed to abort subagent: ${error}`)
  }
}, TIMEOUT_MS)

// Clear timer when subagent completes
ctx.client.session.subscribe(subagent.id, (event) => {
  if (event.type === "session.end" || event.type === "session.error") {
    clearTimeout(timer)
  }
})
```

### Abort API

Use `ctx.client.session.abort({ id })` to terminate a subagent:

```typescript
try {
  await ctx.client.session.abort({ id: subagent.id })
  ctx.logger.info(`Subagent ${subagent.id} aborted successfully`)
} catch (error) {
  // Abort may throw if session already ended
  ctx.logger.warn(`Subagent ${subagent.id} already ended: ${error}`)
}
```

### State Polling

Check subagent status:

```typescript
const status = await ctx.client.session.get({ id: subagent.id })
if (status.status === "completed") {
  // Process results
  const messages = await ctx.client.session.messages({ id: subagent.id })
  // ... process messages
} else if (status.status === "running") {
  // Still working
} else if (status.status === "aborted") {
  // Was terminated
}
```

### Cleanup on Abort

When a subagent is aborted mid-execution, clean up resources:

```typescript
async function spawnWithCleanup(ctx: any, config: SubagentConfig) {
  const subagent = await ctx.client.session.create(config)
  const tempFiles: string[] = []
  
  // Register cleanup handler
  const cleanup = async () => {
    for (const file of tempFiles) {
      await ctx.client.fs.remove({ path: file }).catch(() => {})
    }
  }
  
  ctx.client.session.subscribe(subagent.id, async (event) => {
    if (event.type === "session.end" || event.type === "session.error" || event.type === "session.aborted") {
      await cleanup()
    }
  })
  
  return { subagent, cleanup }
}
```

### Common Pitfalls

| Issue | Cause | Solution |
|-------|-------|----------|
| Subagent hangs forever | No timeout set | Always set a timer with abort |
| Timer fires after completion | Not cleared on success | Clear timer in completion handler |
| Abort throws | Session already ended | Wrap abort in try/catch |
| Parent waits forever | No abort on parent exit | Register cleanup handler on parent end |

---

## Tool System

Use the `tool()` factory from `@opencode-ai/plugin`. Do NOT hand-roll a `Tool` object.

```typescript
import { tool } from "@opencode-ai/plugin"
import { z } from "zod"  // or omit args for no-arg tools

const myTool = tool({
  description: "Search the codebase for a pattern",
  args: z.object({
    query: z.string().describe("Search query"),
    maxResults: z.number().optional().default(10),
  }),
  execute: async (args, ctx) => {
    // args is typed from the schema
    // ctx.sessionID — the session that called the tool
    return `Found ${args.maxResults} results for "${args.query}"`
  },
})
```

For no-arg tools:

```typescript
const taskCompleteTool = tool({
  description: "Signal that all work is complete",
  args: {},
  execute: async (_args, ctx) => "Task completion acknowledged",
})
```

Register tools in the `tool` hook:

```typescript
return {
  tool: {
    task_complete: taskCompleteTool,
    my_search: myTool,
  },
}
```

---

## MCP Integration

### What is MCP?

Model Context Protocol (MCP) is a standard protocol for connecting AI models to external tools and data sources.

### MCP Server Configuration

```json
// opencode.json
{
  "mcpServers": {
    "filesystem": {
      "command": "mcp-filesystem",
      "args": ["--root", "/home/user/projects"],
      "env": {}
    },
    "github": {
      "command": "mcp-github",
      "args": [],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "database": {
      "command": "mcp-postgres",
      "args": ["postgresql://localhost/mydb"]
    }
  }
}
```

### Creating MCP Server

```typescript
// Custom MCP server
import { Server } from '@modelcontextprotocol/sdk/server'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio'

const server = new Server({
  name: 'my-mcp-server',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {}
  }
})

// Register tools
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'my_tool',
        description: 'My custom tool',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string' }
          },
          required: ['query']
        }
      }
    ]
  }
})

server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params
  
  if (name === 'my_tool') {
    const result = await processQuery(args.query)
    return {
      content: [{ type: 'text', text: result }]
    }
  }
  
  throw new Error(`Unknown tool: ${name}`)
})

// Start server
const transport = new StdioServerTransport()
await server.connect(transport)
```

### MCP Tool Usage

```typescript
// Access MCP tools from OpenCode
import { useMcpTools } from '@opencode-ai/plugin'

const githubTools = await useMcpTools('github')

// List available tools
const tools = await githubTools.list()
// [{ name: 'create_issue', description: '...', inputSchema: {...} }, ...]

// Call a tool
const result = await githubTools.call('create_issue', {
  owner: 'myorg',
  repo: 'myrepo',
  title: 'New Issue',
  body: 'Issue description'
})
```

---

## Configuration

### Install a plugin

In `~/.config/opencode/opencode.json`:

```jsonc
{
  "plugin": [
    "my-plugin@1.0.0",                    // from npm
    "file:///abs/path/to/dist/index.js",  // local development
    ["file:///abs/path/to/dist/index.js", { "enabled": true, "debug": true }]  // with options
  ],
  "autoupdate": true
}
```

Options are passed as the second argument to the Plugin function. With `autoupdate: true`, the highest semver version in the npm registry wins.

### Plugin options pattern

```typescript
export const MyPlugin: Plugin = async (ctx, options = {}) => {
  const enabled = options.enabled !== false   // default true
  const timeout = options.timeoutMs ?? 30_000

  if (!enabled) {
    return { event: async () => {}, config: async () => {} }
  }
  // ...
}
```

### Two install locations — know the difference

OpenCode resolves plugins from **two** places. Updates must touch both or you get stale loads:

| Location | Purpose |
|----------|---------|
| `~/.cache/opencode/packages/<name>@<ver>/` | Download cache. Contains `node_modules/`, `dist/`, `package-lock.json`. |
| `~/.config/opencode/node_modules/<name>/` | Runtime resolution via `bun.lock` + `package.json` in `~/.config/opencode/`. |

The `~/.config/opencode/package.json` caret-pins versions (e.g. `"opencode-auto-resume": "^1.0.15"`), and `bun.lock` locks resolution. To force a specific version: edit `package.json`, delete `bun.lock`, run `bun install` in `~/.config/opencode/`.

To clear all cached versions and force a fresh download:

```bash
rm -rf ~/.cache/opencode/packages/opencode-auto-resume@*
rm -rf ~/.local/share/reflex/bun/install/cache/opencode-auto-resume@*
cd ~/.config/opencode && bun install
```

---

## SDK Usage

### @opencode-ai/sdk

```typescript
import { OpenCodeClient } from '@opencode-ai/sdk'

// Create client
const client = new OpenCodeClient({
  baseUrl: 'http://localhost:3000',
  apiKey: 'your-api-key'
})

// Send message
const response = await client.chat({
  message: 'Explain this code',
  files: ['./src/index.ts']
})

// Stream response
for await (const chunk of client.chatStream({
  message: 'Write a function'
})) {
  process.stdout.write(chunk.content)
}

// Execute tool
const result = await client.executeTool({
  name: 'read_file',
  args: { path: './src/main.ts' }
})

// Create session
const session = await client.createSession({
  model: 'claude-3-opus',
  systemPrompt: 'You are a helpful coding assistant'
})

// Continue conversation
const reply = await session.sendMessage('Add error handling')
```

### SDK Client Options

```typescript
interface ClientOptions {
  // API endpoint
  baseUrl?: string
  
  // Authentication
  apiKey?: string
  
  // Model configuration
  model?: string
  
  // Timeout in milliseconds
  timeout?: number
  
  // Retry configuration
  retries?: number
  
  // Custom headers
  headers?: Record<string, string>
}
```

---

## HTTP Server & REST API

### Server Configuration

```typescript
// Server setup
import { createServer } from '@opencode-ai/server'

const server = createServer({
  port: 3000,
  host: '0.0.0.0',
  
  // Authentication
  auth: {
    type: 'api-key',
    keys: ['secret-key-1', 'secret-key-2']
  },
  
  // CORS
  cors: {
    origins: ['http://localhost:5173'],
    methods: ['GET', 'POST', 'PUT', 'DELETE']
  },
  
  // Rate limiting
  rateLimit: {
    windowMs: 60000,
    max: 100
  }
})

await server.start()
```

### REST API Endpoints

```typescript
// Chat endpoint
POST /api/chat
{
  "message": "string",
  "session_id": "string?",
  "files": ["string"]?,
  "model": "string?"
}

// Response
{
  "content": "string",
  "session_id": "string",
  "tool_calls": [...]
}

// Streaming
POST /api/chat/stream
// Returns SSE stream

// Tool execution
POST /api/tools/execute
{
  "name": "string",
  "args": { ... }
}

// Session management
GET  /api/sessions
POST /api/sessions
GET  /api/sessions/:id
DELETE /api/sessions/:id

// Models
GET /api/models

// Configuration
GET /api/config
PUT /api/config
```

### API Client Example

```typescript
// Using fetch
const response = await fetch('http://localhost:3000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'
  },
  body: JSON.stringify({
    message: 'Hello, OpenCode!',
    model: 'claude-3-opus'
  })
})

const data = await response.json()
console.log(data.content)
```

---

## Build Configuration

```json
{
  "name": "my-opencode-plugin",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "scripts": {
    "build": "bun build src/index.ts --outdir dist --target bun",
    "dev": "bun build src/index.ts --outdir dist --target bun --watch",
    "test": "bun test",
    "prepublishOnly": "bun run build"
  },
  "files": ["dist/index.js", "README.md", "LICENSE"],
  "dependencies": {
    "@opencode-ai/plugin": "latest"
  },
  "devDependencies": {
    "@opencode-ai/sdk": "latest",
    "@types/bun": "latest",
    "typescript": "latest"
  }
}
```

> `--target bun` is required — OpenCode runs on bun. The output is a single bundled `dist/index.js` (a virtual filesystem `/$bunfs/root/...`).

---

## Testing

### Unit tests for pure functions

Keep utility functions in `src/test-utils.ts` so they can be tested without importing the plugin entry (which would require mocking `ctx`):

```typescript
// src/index.backoff.test.ts
import { backoffMs } from "./test-utils"
import { describe, test, expect } from "bun:test"

describe("backoffMs()", () => {
  test("attempt 1 returns base", () => {
    expect(backoffMs(1, 1000, 8000)).toBe(1000)
  })
  test("caps at max", () => {
    expect(backoffMs(10, 1000, 8000)).toBe(8000)
  })
})
```

### Integration tests with mock ctx

```typescript
import { mock } from "bun:test"
import { MyPlugin } from "./index"

function createMockContext(opts: { sessions?: any[], messages?: Record<string, any[]> }) {
  const promptCalls: any[] = []
  const ctx = {
    client: {
      app: { log: mock(async () => {}) },
      session: {
        list: mock(async () => ({ data: opts.sessions ?? [] })),
        status: mock(async () => ({ data: {} })),
        messages: mock(async (cfg: any) => opts.messages?.[cfg.path.id] ?? []),
        prompt: mock(async (cfg: any) => { promptCalls.push(cfg); return {} }),
        abort: mock(async () => ({})),
      },
    },
    ui: { toast: mock(async () => {}) },
  } as any
  return { ctx, promptCalls }
}

test("plugin preserves agent on resume", async () => {
  const { ctx, promptCalls } = createMockContext({
    messages: { s1: [{ role: "user", agent: "prometheus", parts: [] }] },
  })
  const hooks = await MyPlugin(ctx, {})

  await hooks.event({ event: { type: "session.status", sessionID: "s1", properties: { status: { type: "idle" } } } })

  expect(promptCalls[0]?.agent).toBe("prometheus")
})
```

### Regression tests for crash-prevention rules

Test the **contract**, not just behavior — bun's test runner does not fatal on unhandled rejections, so behavioral tests alone miss crash bugs. Read the source file and assert structural rules:

```typescript
import { readFileSync } from "node:fs"
const SOURCE = readFileSync(join(import.meta.dir, "index.ts"), "utf8")

test("REGRESSION: no non-Plugin exports", () => {
  expect(SOURCE).not.toMatch(/^export\s+function\s+getLastAssistantError/m)
  expect(SOURCE).not.toMatch(/^export\s+function\s+backoffMs/m)
})

test("REGRESSION: event hook wraps handleEvent in .catch()", () => {
  expect(SOURCE).toMatch(/handleEvent\(event[^)]*\)\.catch\(/)
})

test("REGRESSION: todo.updated validates Array.isArray", () => {
  expect(SOURCE).toMatch(/Array\.isArray\(rawTodos\)/)
})

test("REGRESSION: bundled dist only exports Plugin-shaped values", async () => {
  const mod = await import("./index")
  for (const [name, fn] of Object.entries(mod)) {
    if (typeof fn !== "function") throw new Error(`${name} is not a function`)
    const result = await (fn as Function)(fakeCtx, {})
    if (result === null || typeof result !== "object") {
      throw new Error(`${name} returned ${result} — would crash the host`)
    }
  }
})
```

---

## SDK Types (from `@opencode-ai/sdk`)

### Message types

```typescript
interface UserMessage {
  id: string
  sessionID: string
  role: "user"
  time: { created: number }
  agent: string        // the selected agent; critical for resume
  model: { providerID: string; modelID: string }
  tools?: { [key: string]: boolean }
}

interface AssistantMessage {
  id: string
  sessionID: string
  role: "assistant"
  time: { created: number; completed?: number }
  error?: any          // present if the message failed
  parentID: string
  modelID: string
  providerID: string
  finish?: string      // "stop" | "length" | "error" | "unknown"
}

interface Message {
  role: string
  info?: { role?: string; error?: any }  // some messages nest role/error in .info
  parts?: Part[]
  error?: { name: string; data?: { message: string }; message?: string }
}
```

### Part types

```typescript
type Part =
  | { type: "text"; text: string; synthetic?: boolean }
  | { type: "tool"; callID: string; tool: string; state: ToolState }
  | { type: "reasoning"; text: string }
  | { type: "file"; mime: string; url: string }
  | { type: "agent"; name: string }
  | { type: "step-start" }
  | { type: "step-finish"; reason: string; cost: number; tokens: any }
  | { type: "retry"; attempt: number; error: any }
  | { type: "compaction"; auto: boolean }
```

### Extracting the selected agent

The agent is on `UserMessage.agent`, **not** on `AssistantMessage`. To preserve the agent across resume:

```typescript
async function getSessionAgent(sid: string): Promise<string | undefined> {
  const messages = await getSessionMessages(sid)
  for (let i = messages.length - 1; i >= 0; i--) {
    const role = messages[i].role ?? messages[i].info?.role
    if (role === "user") {
      const agent = (messages[i] as any).agent
      if (typeof agent === "string" && agent.length > 0) return agent
    }
  }
  return undefined
}
```

---

## Real-World Patterns

### Detecting streaming failures

Providers fail mid-stream with errors like `APIError`, `ProviderError`, `StreamError`. Classify by error **name** (exact match) and **message** (regex):

```typescript
function isStreamingFailure(errorName: string, errorMessage: string): boolean {
  const NAMES = ["ProviderError", "APIError", "StreamError", "ConnectionError", "TimeoutError"]
  const PATTERNS = ["streaming response failed", "stream.*fail", "connection.*reset"]
  if (NAMES.includes(errorName)) return true
  const lower = errorMessage.toLowerCase()
  return PATTERNS.some(p => { try { return new RegExp(p, "i").test(lower) } catch { return lower.includes(p) } })
}
```

### Active-tool safety guard

Never abort a session that has a tool running. Check both the in-flight counter (from hooks) and the SDK status:

```typescript
async function checkSessionHasActiveTool(sid: string): Promise<boolean> {
  const statusMap = await getSessionStatusMap()
  if (statusMap[sid] === "busy") return true
  const messages = await getSessionMessages(sid)
  const lastMsg = messages[messages.length - 1]
  if (!lastMsg || roleOf(lastMsg) !== "assistant") return false
  const parts = lastMsg.parts as any[] | undefined
  return parts?.some(p => p.type === "tool-call" || p.type === "tool_use") ?? false
}
```

### Hallucination loop detection

Track `continue` timestamps per session. If 3+ continues within 10 minutes, abort and restart:

```typescript
function isHallucinationLoop(sid: string): boolean {
  const w = sessions.get(sid)
  if (!w) return false
  const now = Date.now()
  w.continueTimestamps.push(now)
  const cutoff = now - 600_000  // 10 min
  w.continueTimestamps = w.continueTimestamps.filter(t => t >= cutoff)
  return w.continueTimestamps.length >= 3
}
```

---

## Debugging

### "Unexpected server error. Check server logs for details."

This is the generic TUI mask. The real error is in the log:

```bash
grep "level=ERROR" ~/.local/share/opencode/log/opencode.log | tail -20
```

Common causes (in order of likelihood):

1. **Non-Plugin export returns null** → `null is not an object (evaluating 'N.config')` — see Rule 1
2. **Unhandled promise rejection** in `event` hook or `setInterval` — see Rule 2
3. **Event payload not validated** → `todos.filter is not a function` — see Rule 3
4. **Invalid session ID** passed to SDK → `Expected 'id' to be a string` — see Rule 5

### Plugin not loading

```bash
grep "failed to load plugin" ~/.local/share/opencode/log/opencode.log
```

Check:
- `dist/index.js` exists and has `"main": "dist/index.js"` in `package.json`
- The cache directory has the real package, not just a wrapper: `ls ~/.cache/opencode/packages/<name>@<ver>/node_modules/<name>/dist/index.js`
- `bun.lock` in `~/.config/opencode/` resolves to the version you expect

### Verify which version loaded at runtime

```bash
grep "opencode-auto-resume\|my-plugin" ~/.local/share/opencode/log/opencode.log | tail -5
# Look for: path=my-plugin@X.Y.Z
```

---

## Publishing & Distribution

### Package Structure

```
my-opencode-plugin/
├── package.json
├── tsconfig.json
├── src/
│   └── index.ts
├── dist/
│   └── index.js
└── README.md
```

### package.json

```json
{
  "name": "opencode-plugin-mytool",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "peerDependencies": {
    "@opencode-ai/plugin": "^1.0.0"
  },
  "keywords": [
    "opencode",
    "plugin",
    "ai",
    "coding-assistant"
  ]
}
```

### Publishing to npm

```bash
# Build
npm run build

# Test
npm test

# Publish
npm publish --access public
```

### Local Development

```bash
# Link for local testing
npm link

# In opencode config
{
  "plugins": ["opencode-plugin-mytool"]
}
```

---

## Summary Checklist

Before publishing a plugin:

- [ ] `dist/index.js` exports ONLY `default` (and optionally a named alias of the same function)
- [ ] `event` hook wraps async work in `.catch()`
- [ ] All `setInterval` async bodies wrapped in try/catch or `safe()`
- [ ] `log()` helper never rethrows
- [ ] All event payload fields validated (`Array.isArray`, `typeof`, `?.`)
- [ ] All SDK calls validate `sid` first
- [ ] `session.status()` accessed via `.type`, never compared as bare string
- [ ] Tests include source-contract assertions (not just behavioral)
- [ ] `bun test` passes with 0 failures
- [ ] `bun build` produces `dist/index.js` with only Plugin exports