#!/bin/bash
# Starts the figma-console MCP server with the Figma token from .env.
#
# Claude Code runs this script (see the "figma-console" entry in .mcp.json)
# instead of starting the server directly. The token lives only in the
# project's ignored .env file, so this script reads it there and hands it to
# the one program that needs it. Nothing else in the container, and no
# terminal, has the token in its environment.
set -e

# The project folder is one level up from this script's folder. Working it
# out from the script's own location means it does not matter which folder
# Claude Code was started from.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env"

# Stop with a clear message if there is no .env yet. Messages go to stderr
# (>&2) because an MCP server's stdout is reserved for talking to Claude Code.
if [ ! -f "$ENV_FILE" ]; then
  echo "start-figma-console-mcp: no .env file at $ENV_FILE." >&2
  echo "Copy .env-rename to .env and add FIGMA_ACCESS_TOKEN (see the README)." >&2
  exit 1
fi

# Load .env. "set -a" tells bash to export every variable assigned from here
# on, so the KEY=value lines in .env become environment variables that the
# server below can see. "set +a" turns that back off right after, so later
# variables in this script stay private to it.
set -a
source "$ENV_FILE"
set +a

# Stop with a clear message if .env does not have the token. This checks
# only that the value is not empty; it never prints it.
if [ -z "$FIGMA_ACCESS_TOKEN" ]; then
  echo "start-figma-console-mcp: FIGMA_ACCESS_TOKEN is missing or empty in .env." >&2
  echo "Add a Figma personal access token there (see the README)." >&2
  exit 1
fi

# Replace this script with the server ("exec"), so Claude Code talks to the
# server directly and stopping the server needs no extra step.
# The version is pinned on purpose: "@latest" would fetch whatever is newest
# each time Figma is used, and the three-day release cooldown in .npmrc does
# not apply to an npx fetch, so a poisoned release could run with the Figma
# token. Bump the version at a two-week review (the tool-figma skill card
# records it). 1.40.9 was published October 2, 2026.
exec npx -y figma-console-mcp@1.40.9
