#!/bin/bash
# One-time setup that runs after the dev container is created.
# It installs the project's npm dependencies.
#
# Claude Code comes from the Claude Code feature in devcontainer.json, so it
# is not installed here. The .env file is not loaded into the shell either:
# the Figma token is read only by scripts/start-figma-console-mcp.sh (for
# the figma-console MCP server) and by the npm "script:*" commands, which
# pass .env to node with --env-file.
set -e

echo "==> Installing npm dependencies"
npm install

echo "==> Done"
