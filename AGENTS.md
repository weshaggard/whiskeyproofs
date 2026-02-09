# Agent Instructions

## Task Framework

All tasks in this repository must follow this structured workflow: **Task → Requirements → Retry → Report**.

### 1. Task

Before starting work, restate the task in one sentence. This anchors what you are doing and prevents scope drift.

### 2. Requirements

Before making any changes, list the concrete acceptance criteria that must be met for the task to be considered complete. Requirements must be:

- **Specific** — no vague goals; each requirement is pass/fail
- **Verifiable** — each one can be checked by running a script, inspecting output, or viewing a file
- **Scoped** — only what was asked for; do not add unrequested work

If the request is ambiguous, ask the user to clarify before proceeding.

### 3. Retry

When a step fails, follow this retry strategy:

| Failure Type | Strategy | Max Retries |
|---|---|---|
| **Network / transient errors** (timeouts, HTTP 5xx, connection refused) | Retry the same operation unchanged | 3 |
| **Logic / data errors** (wrong result, no match found, validation failure) | Retry with a small tweak (e.g., broaden search terms, adjust date range, try alternate approach) | 3 |
| **Permanent errors** (file not found, permission denied, invalid input) | Do not retry; stop and report the failure immediately | 0 |

After exhausting retries, **stop and report** — do not keep attempting indefinitely.

### 4. Report

When the task is finished (whether fully successful, partially successful, or failed), produce **two outputs**:

**Inline summary** (in the chat response):
- One sentence stating the outcome
- Count of items processed / succeeded / failed

**Report file** (written to the session folder):
- Path: `{session_folder}/files/task-report.md`
- The report must contain enough context that a **future agent session** can pick up where this one left off without re-reading the original request or re-discovering state.
- Structure:

```markdown
# Task Report

## Task
{one-sentence restatement of the original request}

## Result
{✅ Success | ⚠️ Partial | ❌ Failed}

## Summary
- Items processed: N
- Succeeded: N
- Failed: N
- Skipped: N

## Completed
{list of items/steps that succeeded, with enough detail to avoid re-doing them}

## Errors
{for each failure: what was attempted, the exact error message or output, and which retry attempts were made with what changes — include file paths, line numbers, IDs, or any identifiers needed to reproduce or investigate}

## Remaining Work
{explicit list of items/steps that were NOT completed — each entry should be actionable by the next agent without additional context, including any relevant IDs, file paths, search terms, or parameters that were being used}

## State
{any intermediate data, caches, or working state the next session should know about — e.g., "results saved to found_ttb_ids.json", "CSV was partially updated through row 250", "TTB session cookie expired after ID 24050001000660"}
```

If a section has no content (e.g., no errors, no remaining work), write "None."
