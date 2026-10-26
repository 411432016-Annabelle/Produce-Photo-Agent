# Produce Freshness Agent

A Discord agent that identifies fruits and vegetables from photos and estimates their freshness and whether they're ready to eat, using `claude -p`.

## Before any work

Read `docs/architecture.md` first. It is the source of truth for behaviour, the `claude -p` contract, Excel columns, reply format and security.

## Guards

Wrap each of the four guards (architecture section 12) in its own marker comments, with every guard enabled:

```python
# ===== GUARD 1 START: claude -p sees only a temp folder with one photo =====
...
# ===== GUARD 1 END =====
```

- Guard 1: `claude -p` runs in a temp folder holding only the one photo, never `DATA_DIR`.
- Guard 2: the uploader's text is stored only in Excel's Note column, never passed to `claude -p`.
- Guard 3: the item name is cleaned (`/`, `\`, `..`, `:`, etc.) before use as a filename.
- Guard 4: Excel text starting with `=`, `+`, `-`, `@` is stored as plain text.

Keep each guard contained in one marked block so it can be switched off on its own for teaching.

## Git

Commit code and docs only. `.env` (holds `DISCORD_TOKEN`) and everything in `DATA_DIR` (`data/`: photos, `produce_log.xlsx`, `pending_rows.jsonl`) stay out of Git; both are in `.gitignore`.
