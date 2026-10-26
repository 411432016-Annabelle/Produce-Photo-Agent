# Produce-Photo-Agent

A Discord agent that identifies fruits and vegetables from photos and estimates their freshness and whether they're ready to eat, using `claude -p`. Every result is replied in the channel and appended to an Excel log.

Full design: [docs/architecture.md](docs/architecture.md). Discord set-up: [docs/discord-server-setup.md](docs/discord-server-setup.md) and [docs/discord-bot-setup.md](docs/discord-bot-setup.md).

## Requirements

- macOS (or Linux) with [uv](https://docs.astral.sh/uv/) installed
- Python 3.12 (uv picks it up from `.python-version`)
- Claude Code (`claude` command) installed and logged in
- A Discord bot with **Message Content Intent** on, invited to your server

## Set-up

1. Copy `.env.example` to `.env` and fill in the four settings: `DISCORD_TOKEN`, `CHANNEL_ID`, `CLAUDE_MODEL`, `DATA_DIR`. Never commit `.env`.
2. Install the dependencies:
   ```
   uv sync
   ```

## Run

```
uv run python -m agent
```

The terminal shows `✅ Logged in as … Watching #produce-check`. Stop it with **Ctrl+C**.

Photos are saved to `DATA_DIR/photos/` and the log to `DATA_DIR/produce_log.xlsx`. If Excel is busy, rows wait in `DATA_DIR/pending_rows.jsonl` and are added automatically later. Look at the log, but close it **without saving** while the agent runs.

## Tests

```
uv run pytest
```

These run offline with a fake `claude` command and use no Claude quota.

## Security guards

Each guard is one block between `# ==== GUARD n: … START ====` and `# ==== GUARD n END ====`. All four are enabled. Commenting out a block (every line of it) switches that guard off and leaves the unsafe behaviour, so the agent still runs. `tests/test_guards.py` checks both states.

| Guard | What it does | File | Lines (approx.) |
|---|---|---|---|
| 1 | `claude -p` runs in a temp folder holding only the one photo, with reads of `DATA_DIR` denied. Off: `claude -p` runs inside `DATA_DIR` with the Read tool | `agent/analyzer.py` | 46–60 |
| 2 | The uploader's text never reaches `claude -p`; it only goes to the Note column. Off: the text is added to the prompt | `agent/analyzer.py` | 62–65 |
| 3 | The item name is cleaned (`/ \ .. :` and other path-breaking characters) before it becomes a filename | `agent/photos.py` | 69–75 |
| 4 | Text starting with `= + - @`, tab or line break is stored in Excel as plain text, never a formula | `agent/excel_log.py` | 139–145 |

Use a test channel and test data when demonstrating with guards off, and turn them back on afterwards.
