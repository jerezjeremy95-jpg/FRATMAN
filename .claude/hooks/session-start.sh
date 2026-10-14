#!/bin/bash
# SessionStart hook: install Agent Reach so it survives ephemeral cloud sessions.
# Idempotent and non-interactive. Installs the `rss` and `youtube` channels
# (the only channels published in agent-reach 0.1.0 — neither needs credentials).
set -euo pipefail

VENV="$HOME/.agent-reach/venv"
BIN="$HOME/.local/bin/agent-reach"

# Create the isolated venv and install agent-reach if missing.
if [ ! -x "$VENV/bin/agent-reach" ]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q --upgrade pip >/dev/null 2>&1 || true
  "$VENV/bin/pip" install -q agent-reach >/dev/null 2>&1
fi

# Expose it on PATH via ~/.local/bin.
mkdir -p "$HOME/.local/bin"
ln -sf "$VENV/bin/agent-reach" "$BIN"

# Install the credential-free channels (install is a no-op if already present).
"$BIN" install rss >/dev/null 2>&1 || true
"$BIN" install youtube >/dev/null 2>&1 || true

echo "agent-reach ready: $("$BIN" doctor 2>/dev/null | grep -c '^ok') channel(s) ok" >&2
