#!/bin/bash
# One-time setup that runs after the dev container is created.
# It does two things:
#   1. installs the project's npm dependencies
#   2. makes the shell load the project's .env file (Figma token) on startup
# Claude Code itself comes from the Claude Code feature in devcontainer.json,
# so it is not installed here.
set -e

PROJECT_DIR="$PWD"

# The image provides both bash and zsh. Write shell setup to both so it
# works no matter which one VS Code opens in the terminal.
SHELL_RC_FILES="$HOME/.bashrc $HOME/.zshrc"

echo "==> Installing npm dependencies"
npm install

echo "==> Wiring .env auto-load into shell startup files"
ENV_MARKER="# ai-design-system-demo-app: auto-load project .env"

for shell_rc_file in $SHELL_RC_FILES; do
  touch "$shell_rc_file"

  # .mcp.json refers to ${FIGMA_ACCESS_TOKEN}, which Claude Code expands from
  # the shell environment. Loading .env here means the token is available
  # whenever the claude CLI is launched from a terminal in this container.
  if ! grep -qF "$ENV_MARKER" "$shell_rc_file"; then
    cat >> "$shell_rc_file" <<EOF

$ENV_MARKER
if [ -f "$PROJECT_DIR/.env" ]; then
  set -a
  . "$PROJECT_DIR/.env"
  set +a
fi
EOF
  fi
done

echo "==> Done"
