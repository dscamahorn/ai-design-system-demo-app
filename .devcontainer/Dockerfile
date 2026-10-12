# The dev container image. VS Code builds it for "Reopen in Container", and
# the devcontainer command builds the same file on the Air.
#
# Starts from Microsoft's Node image (Node 22, git, a proper shell, sudo, and
# a non-root "node" user). This project pins the bookworm (Debian 12)
# variant of it. Add the system tools the project needs below.
FROM mcr.microsoft.com/devcontainers/javascript-node:22-bookworm

# The two security scanners the Security rules run before a milestone branch
# is pushed: Semgrep reads the code for known bad shapes, pip-audit checks
# Python packages against the database of known holes. (npm audit comes with
# npm.) They live in the image so every project has them on day one and the
# versions are the same everywhere. uv, the house Python tool, installs each
# one as an isolated tool under /opt/uv and links the commands into
# /usr/local/bin; the three variables on the RUN line tell it where, and are
# set for that one line only so a project's own `uv sync` is unaffected.
# The versions are pinned on purpose: bump them at a two-week review.
#
# The last uv line installs Python 3.14 into /opt/uv/python on purpose.
# Bookworm's own Python is 3.11, which is new enough for the scanners, so
# uv would otherwise never put a Python there. The timelapse skill
# (installed by postCreateCommand) needs 3.12 or newer and expects to find
# one in /opt/uv/python; without this line it tries to download one into
# that root-owned folder and fails with "Permission denied".
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /uvx /bin/
RUN UV_TOOL_DIR=/opt/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
    UV_PYTHON_INSTALL_DIR=/opt/uv/python \
    uv tool install semgrep==1.180.0 \
    && UV_TOOL_DIR=/opt/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
    UV_PYTHON_INSTALL_DIR=/opt/uv/python \
    uv tool install pip-audit==2.10.1 \
    && UV_PYTHON_INSTALL_DIR=/opt/uv/python uv python install 3.14 \
    && chmod -R a+rX /opt/uv

# npm 12, pinned. The base image ships npm 10. From npm 12, a package's
# install scripts do not run unless the project lists the package in an
# "allowScripts" allowlist in package.json (built with "npm approve-scripts"),
# git and remote-URL dependencies are off, and the "min-release-age" cooldown
# in the project's .npmrc is honored. Those three closed the install-time
# path every 2026 npm supply-chain wave used. Bump the version at a two-week
# review.
RUN npm install -g npm@12.2.0

# System packages. ffmpeg is here for every project because the timelapse
# skill (installed into the container by postCreateCommand, see
# devcontainer.json) builds its video with it. Add the project's own system
# tools to the same line, one per row.
# --no-install-recommends keeps the image smaller by skipping optional
# extras; removing the apt lists afterward does the same.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Web projects only: the browser for the project's verification skill (the
# stack-verify skill explains the skill; Playwright is the library that drives
# the browser) and for the timelapse skill, which looks for it under this
# same path. Chromium is installed here, at build time, into a shared path
# every user can read, so no download happens inside a running session (the
# Bash sandbox allows only a short list of domains). Pin the same Playwright
# version in the project's package.json. --with-deps adds the system
# libraries Chromium needs. This project does not use Playwright yet, so the
# block stays off; uncomment it when it does, and bump the version at a
# two-week review.
# ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright
# RUN npx --yes playwright@1.64.0 install --with-deps chromium \
#     && chmod -R a+rX /opt/playwright

# Docker creates the folders a bind mount needs as root. Claude Code must be
# able to write in ~/.claude and in ~/.claude/projects (its session files;
# the project's own transcript folder is mounted inside projects/, and a
# session started in a subfolder of the repo writes a sibling folder there),
# so both are created here, owned by the normal user, before the mounts
# land inside them.
# The global rules and app preferences arrive as the shared/ folder mount
# (see devcontainer.json). Claude Code looks for them at ~/.claude/CLAUDE.md
# and ~/.claude/settings.json, so those two are a one-line import and a
# symlink pointing into shared/.
RUN mkdir -p /home/node/.claude/projects \
    && printf '@~/.claude/shared/CLAUDE.md\n' > /home/node/.claude/CLAUDE.md \
    && ln -s shared/settings.json /home/node/.claude/settings.json \
    && chown -R node:node /home/node/.claude

# Claude Code, installed with Anthropic's own installer as the normal user,
# so it lives in that user's home folder (~/.local/bin/claude) and can
# update itself. The Claude Code devcontainer feature, used until October
# 12, 2026, ran "npm install -g" as root, which left a package the normal
# user could not replace: every update inside a container failed with
# EACCES until the next rebuild. Installing it here also means npm 12 runs
# with no exceptions to its "install scripts off" rule. It comes last
# because ~/.claude must already exist and belong to the user. USER
# switches who runs the next lines; it goes back to root afterward so
# anything added below this block runs as before.
USER node
RUN curl -fsSL https://claude.ai/install.sh | bash
USER root
