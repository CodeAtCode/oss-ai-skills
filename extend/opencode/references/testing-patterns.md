<!-- Loaded on demand from ../SKILL.md -->

# Testing, SDK Types & Real-World Patterns

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

---

## Silent Dead-Stream Detection

*Pattern for detecting assistant messages that produced no visible output.*

Some sessions end with `finish: "unknown"` but zero text parts — the model only produced reasoning. Detect and handle these:

```typescript
const silentDeadStreamMinTokens: number =
  (options?.silentDeadStreamMinTokens as number) ?? DEFAULT_SILENT_DEAD_STREAM_MIN_TOKENS // e.g., 200

function getLastSilentDeadStream(messages: Message[]): { finish: string; outputTokens: number } | null {
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i]
    if (msg.role === "assistant" && msg.finish && msg.finish !== "stop") {
      const hasText = msg.parts?.some(p => p.type === "text" && p.text?.trim())
      if (!hasText) {
        // Dead stream: non-terminal finish with no text
        const outputTokens = countTokensFromParts(msg.parts || [])
        return { finish: msg.finish, outputTokens }
      }
    }
  }
  return null
}

// In session.idle handler
const dead = getLastSilentDeadStream(await getSessionMessages(sid))
if (dead && dead.outputTokens >= silentDeadStreamMinTokens) {
  // Silent dead stream detected — trigger recovery
  w.pendingRecovery = true
  w.pendingRecoveryReason = `silent-${dead.finish}`
  w.pendingRecoveryAt = Date.now()
  await log("info", `${short(sid)} - silent dead stream (${dead.finish}, ${dead.outputTokens} tokens)`)
}
```

---

## Test Timing Patterns

*Optimize test suite runtime by replacing long fixed waits with injectable delays.*

### Replace long warmup waits

In most tests, replace `wait(3500)` → `wait(500)` and use injectable config:

```typescript
const toolTextCheckDelayMs: number =
  (options?.toolTextCheckDelayMs as number) ?? DEFAULT_TOOL_TEXT_CHECK_DELAY_MS
const minActivityGapMs: number =
  (options?.minActivityGapMs as number) ?? DEFAULT_MIN_ACTIVITY_GAP_MS
const warmupMs: number =
  (options?.warmupMs as number) ?? DEFAULT_WARMUP_MS
```

Test config:
```typescript
const testOptions = {
  toolTextCheckDelayMs: 10,
  minActivityGapMs: 0,
  warmupMs: 0,  // Disable warmup unless testing warmup behavior
}

const hooks = await MyPlugin(ctx, testOptions)
```

**Real result:** Suite runtime 104s → 23s

**Exception:** Keep real `warmupMs: 60000` ONLY in tests that verify warmup behavior itself.

---

## TypeScript vs SDK Types in Tests

*Pattern for handling stricter SDK types vs test mocks.*

The SDK `Event` union is stricter than test mocks. Use non-null assertions and `as any` on event literals:

```typescript
// Test mocks
hooks.event!()({ event: { type: "session.status", sessionID: "s1", properties: { status: { type: "idle" } } } })
hooks.config!()({ /* config shape */ })

// Event helpers
const statusEvent = makeStatusEvent("idle", "s1") as any
const errorEvent = makeErrorEvent("MessageAbortedError", "aborted") as any
```

**Verify with:** `bun x tsc --noEmit -p tsconfig.json`

**Rule:** Never duplicate interface definitions between `src` and test files — import from SDK or shared test-utils.

---

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