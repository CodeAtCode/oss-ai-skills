<!-- Loaded on demand from ../SKILL.md -->

# Subagent Lifecycle Management & Tool System

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
    await ctx.client.session.abort({ path: { id: subagent.id } })
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

Use `ctx.client.session.abort({ path: { id } })` to terminate a subagent:

```typescript
try {
  await ctx.client.session.abort({ path: { id: subagent.id } })
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

## Context Saturation & Compaction (v1.18+)

*From production plugin experience: field-tested patterns for handling context window pressure.*

### Token tracking from streaming events

Track token totals from `message.updated` events to detect when a session is approaching its model's context limit:

```typescript
// Per-session watch state
interface SessionWatch {
  lastTokenTotal: number
  // ... other fields
}

// In message.updated handler
if (event.type === "message.updated") {
  const props = event.properties as any
  const delta = props?.delta as string | undefined
  if (delta) {
    // Accumulate tokens from streaming deltas
    // (use your token counter of choice)
    w.lastTokenTotal += countTokens(delta)
  }
}
```

### Saturation detection

Configure a threshold (default 0.85) and compute ratio vs model window:

```typescript
const contextSaturationThreshold: number =
  (options?.contextSaturationThreshold as number) ?? 0.85

// In session.idle handler, before taking action
const usable = getUsableContextWindow(modelID) // e.g. 128000 for claude-3.5
if (w.lastTokenTotal / usable >= contextSaturationThreshold) {
  await log("warn", `${short(sid)} - context saturated (${Math.round(w.lastTokenTotal / usable * 100)}%), triggering compaction`)
  // Trigger native compaction or custom recovery
}
```

### Native compaction fallback

OpenCode v1.18+ provides `session.summarize()` for built-in context compaction:

```typescript
// Opt-in behind config
const useNativeCompaction: boolean =
  (options?.useNativeCompaction as boolean) ?? false

if (useNativeCompaction && saturationDetected) {
  await ctx.client.session.summarize({ path: { id: sid } })
  await log("info", `${short(sid)} - native compaction triggered`)
}
```

**Note:** Magic-context sessions (`ctx.config.get().plugin` returns truthy) run in reduced mode without historian/compaction — handle them differently or skip compaction logic.

---

## ESC/Abort Race & PluginAbortInFlight Pattern

*Critical pattern discovered through production crashes: the ESC interrupt and plugin abort can race, causing false-positive "user cancelled" detection.*

### The problem

When the user presses ESC, the `session.status` event with `"interrupted"` can arrive **BEFORE** the `session.error` event with `MessageAbortedError`. If the plugin aborts during this window, it may misinterpret the abort as user-initiated cancellation.

### The solution

Track abort state explicitly in the per-session watch (`ensureWatch`):

```typescript
interface SessionWatch {
  pluginAbortInFlight: boolean
  pluginAbortAt: number
  // ... other fields
}

// Initialize in ensureWatch
w.pluginAbortInFlight = false
w.pluginAbortAt = 0
```

**Before aborting:**

```typescript
w.pluginAbortInFlight = true
w.pluginAbortAt = Date.now()

try {
  await ctx.client.session.abort({ path: { id: sid } })
  // ... success handling
} finally {
  w.pluginAbortInFlight = false
  w.pluginAbortAt = 0
}
```

**In session.error handler:**

```typescript
case "session.error": {
  const error = props?.error as any
  if (error?.name === "MessageAbortedError") {
    // Check if this was a plugin-initiated abort
    if (w.pluginAbortInFlight && Date.now() - w.pluginAbortAt < 1000) {
      await log("debug", `${short(sid)} - abort race detected, treating as plugin abort not user-cancel`)
      // Do NOT set userCancelled = true
    } else {
      w.userCancelled = true
      await log("info", `${short(sid)} - user pressed ESC`)
    }
  }
  break
}
```

---

## Idempotency Guards in Event Handlers

*Production pattern: prevent duplicate work and state corruption from re-entrant event handlers.*

### hasOpenTodos gating

Never send a "done without work" prompt unless there are actually open todos:

```typescript
function isOpenTodo(todo: any): boolean {
  const status = todo?.status as string | undefined
  return status === "pending" || status === "in_progress"
}

// In message.updated handler when detecting done claims
if (containsDoneClaimPattern(text, DONE_CLAIM_PATTERNS)) {
  const todos = w.todos || []
  const hasOpenTodos = todos.some(isOpenTodo)
  
  if (hasOpenTodos) {
    // Model claims done but work remains → send recovery prompt
    bestCandidate = { prompt: doneWithoutWorkPrompt, priority: 1 }
  } else {
    // No open todos → check if work was actually done
    if (!containsWorkDescription(allAssistantText)) {
      bestCandidate = { prompt: doneWithoutDetailsPrompt, priority: 1 }
    }
  }
}
```

### Latch flags on watch state

Prevent multiple concurrent recovery attempts:

```typescript
interface SessionWatch {
  pendingRecovery: boolean
  pendingRecoveryReason: string | null
  pendingRecoveryAt: number | null
  resumeAttempts: number
  // ... other fields
}

// Guard at start of recovery logic
if (w.pendingRecovery) {
  await log("debug", `${short(sid)} - recovery already in progress, skipping`)
  return
}

// Set latch before async work
w.pendingRecovery = true
w.pendingRecoveryReason = "silent-unknown"
w.pendingRecoveryAt = Date.now()

try {
  // ... recovery work
} finally {
  // Always clear latch
  w.pendingRecovery = false
  w.pendingRecoveryReason = null
  w.pendingRecoveryAt = null
}
```

---

## Subagent Empty-Result Validation

*Pattern for detecting when a subagent finishes but produces no useful output.*

After a subagent completes, validate its output before considering the work done:

```typescript
const status = await ctx.client.session.get({ path: { id: subagentID } })
if (status.type === "idle") {
  const messages = await ctx.client.session.messages({ path: { id: subagentID } })
  
  // Check for empty or reasoning-only responses
  const lastAssistant = getLastAssistantMessage(messages)
  if (!lastAssistant || hasNoTextParts(lastAssistant)) {
    await log("warn", `${short(sid)} - subagent ${subagentID} produced no output, retrying`)
    w.resumeAttempts++
    // Retry logic or escalate to parent
  }
}
```

---

## Orphan Parent Detection

*Pattern for detecting when a parent session is stuck waiting for a finished subagent.*

### The problem

A parent session can remain "busy" after its child subagent finishes, causing the parent to hang indefinitely.

### Detection

Track `busyCount()` (sessions with `status === "busy"`) and watch for the pattern where a parent transitions from busyCount >1→1:

```typescript
function busyCount(): number {
  let count = 0
  for (const [, w] of sessions) {
    if (w.status === "busy") count++
  }
  return count
}

// In periodic watch loop
const numBusy = busyCount()
for (const [sid, w] of sessions) {
  if (w.status !== "busy") continue
  if (w.orphanWatchStartAt !== null) {
    const orphanIdle = now - w.orphanWatchStartAt
    if (orphanIdle >= subagentWaitMs + gracePeriodMs) {
      // Parent is orphaned — subagent finished but parent didn't notice
      if (w.resumeAttempts < maxRetries) {
        // Guard: don't abort while parent is running a tool
        if (!hasInflightTools(w)) {
          await handleOrphanParent(sid, w)
        }
      }
    }
  }
}
```

### Resolution

After waiting `subagentWaitMs + gracePeriodMs` (~18s default), probe the child session. If the child is done but the parent is still busy, abort+resume the parent:

```typescript
async function handleOrphanParent(sid: string, w: SessionWatch) {
  w.pluginAbortInFlight = true
  w.pluginAbortAt = Date.now()
  
  try {
    await ctx.client.session.abort({ path: { id: sid } })
    await log("info", `${short(sid)} - orphan parent aborted, resuming`)
    
    // Wait a moment, then send continue prompt
    await new Promise(r => setTimeout(r, ABORT_CONTINUE_DELAY_MS))
    await sendContinuePrompt(sid, continuePrompt, w)
    w.orphanWatchStartAt = null
    w.resumeAttempts++
  } finally {
    w.pluginAbortInFlight = false
    w.pluginAbortAt = 0
  }
}
```

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