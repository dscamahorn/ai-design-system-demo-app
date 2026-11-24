"""Format and lint checks that Claude Code runs on its own, as hooks.

Copied from the stack-new-project skill's template into a project as
scripts/agent_checks.py. The project's .claude/settings.local.json runs it at
two moments (a hook is a command Claude Code runs every time an event
happens, so the check never depends on the agent remembering it):

  --format-edited-file   after every Edit or Write: formats that one file
  --lint-before-stop     when the agent is about to finish a turn that edited
                         files: runs the linter, and on errors sends them back
                         so the agent fixes them, at most MAX_FIX_ROUNDS times

Why: instructions guide, hooks enforce. A file the agent writes is never
saved in the editor, so format-on-save never touches it, and a style rule in
AGENTS.md is followed most of the time while a hook runs all of the time.
From CS146S week 4 (November 15, 2026).

Set the two commands below for this project. The defaults are the house
JavaScript tools (Prettier and ESLint); a project without them leaves a
command empty and that check is skipped.
"""

import json
import os
import subprocess
import sys

# The formatter, run on one file at a time; the file path is added at the end.
FORMAT_COMMAND = ["node_modules/.bin/prettier", "--write", "--ignore-unknown"]

# Only these kinds of files are formatted. Markdown is left out on purpose so
# PRD.md, DECISIONS.md, and notes are never rewritten behind Doug's back.
FORMATTED_EXTENSIONS = [".js", ".mjs", ".cjs", ".ts", ".jsx", ".tsx", ".css", ".html", ".json"]

# The linter, run on the whole project when the agent stops.
# The same files and flags as `npm run app:lint`: only the files this project
# owns, because the rest is the upstream design system's code.
LINT_COMMAND = [
    "node_modules/.bin/eslint",
    "src/examples/SampleUI.tsx",
    "src/sample-ui-main.tsx",
    "src/figma/primitives/button/ButtonSuccess.figma.ts",
    "--report-unused-disable-directives",
    "--max-warnings",
    "0",
]

# How many times a failing lint is handed back before the agent may stop
# anyway. Two, after Stripe's rule: each further round costs time and context
# for less and less return.
MAX_FIX_ROUNDS = 2

# Exit code 2 tells Claude Code to show this script's error output to the
# agent; at the Stop event it also keeps the agent working.
EXIT_SEND_BACK_TO_AGENT = 2

# Where each session's edit marker and round count are kept between hook
# runs; .claude/ is git-ignored.
STATE_FOLDER = os.path.join(".claude", "agent-checks")

HELP_TEXT = """Runs a project's formatter and linter as Claude Code hooks.

  --format-edited-file  read the hook's JSON from stdin and format the file
                        that was just edited (used by the PostToolUse hook)
  --lint-before-stop    after a turn that edited files, run the linter; on
                        errors, print them and exit 2 so the agent fixes
                        them, at most 2 rounds (Stop hook)
  --dry-run             print the command that would run, and run nothing
  --help                show this text

Run from the project root. Set FORMAT_COMMAND and LINT_COMMAND at the top of
the script for the project's own tools."""


def read_hook_input() -> dict:
    """Read the JSON that Claude Code sends to a hook on stdin; empty if there is none."""
    # Run by hand in a terminal, stdin is the keyboard and reading it would
    # wait forever, so there is no hook input to read.
    if sys.stdin.isatty():
        return {}
    raw_text = sys.stdin.read()
    if raw_text.strip() == "":
        return {}
    return json.loads(raw_text)


def tool_is_installed(command: list) -> bool:
    """Say whether the command's program exists, so a missing tool is skipped rather than failing."""
    if len(command) == 0:
        return False
    return os.path.exists(command[0])


def session_file_path(session_id: str, kind: str) -> str:
    """Return this session's bookkeeping file of one kind ("rounds" or "edited")."""
    return os.path.join(STATE_FOLDER, session_id + "." + kind)


def mark_edit_happened(session_id: str) -> None:
    """Leave a marker saying the agent edited a file, so the Stop hook knows to lint."""
    os.makedirs(STATE_FOLDER, exist_ok=True)
    with open(session_file_path(session_id, "edited"), "w") as marker_file:
        marker_file.write("edited")


def edit_happened(session_id: str) -> bool:
    """Say whether the agent edited a file since the last lint that passed or gave up."""
    return os.path.exists(session_file_path(session_id, "edited"))


def read_rounds_used(session_id: str) -> int:
    """Return how many times lint errors were already sent back in this session."""
    path = session_file_path(session_id, "rounds")
    if not os.path.exists(path):
        return 0
    with open(path) as rounds_file:
        text = rounds_file.read().strip()
    if text.isdigit():
        return int(text)
    return 0


def save_rounds_used(session_id: str, rounds_used: int) -> None:
    """Record the round count for this session."""
    os.makedirs(STATE_FOLDER, exist_ok=True)
    with open(session_file_path(session_id, "rounds"), "w") as rounds_file:
        rounds_file.write(str(rounds_used))


def clear_session_state(session_id: str) -> None:
    """Forget the edit marker and the round count, after lint passes or the cap is reached."""
    for kind in ["edited", "rounds"]:
        path = session_file_path(session_id, kind)
        if os.path.exists(path):
            os.remove(path)


def format_edited_file(dry_run: bool) -> int:
    """Mark that an edit happened, then format the edited file when it is a kind the formatter handles."""
    hook_input = read_hook_input()
    session_id = hook_input.get("session_id", "no-session")
    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if file_path == "":
        return 0
    if not dry_run:
        mark_edit_happened(session_id)
    extension = os.path.splitext(file_path)[1].lower()
    if extension not in FORMATTED_EXTENSIONS:
        return 0
    if not tool_is_installed(FORMAT_COMMAND):
        return 0
    command = FORMAT_COMMAND + [file_path]
    if dry_run:
        print("would run: " + " ".join(command))
        return 0
    # A formatting failure (usually a syntax error) is not reported here;
    # the linter at the Stop hook reports it with a clearer message.
    subprocess.run(command, capture_output=True, text=True)
    return 0


def lint_before_stop(dry_run: bool) -> int:
    """Run the linter after a turn that edited files; hand errors back until MAX_FIX_ROUNDS is reached."""
    hook_input = read_hook_input()
    session_id = hook_input.get("session_id", "no-session")
    if not tool_is_installed(LINT_COMMAND):
        return 0
    if dry_run:
        print("would run: " + " ".join(LINT_COMMAND))
        return 0
    # A turn that only answered a question edited nothing, so there is
    # nothing new to lint; old errors in the repo do not hold it up.
    if not edit_happened(session_id):
        return 0
    result = subprocess.run(LINT_COMMAND, capture_output=True, text=True)
    if result.returncode == 0:
        clear_session_state(session_id)
        return 0
    rounds_used = read_rounds_used(session_id)
    if rounds_used >= MAX_FIX_ROUNDS:
        # Stop handing it back: forget this edit, let the agent finish, and
        # tell Doug. A hook's "systemMessage" is shown to the person. The
        # next lint happens only after the next edit.
        clear_session_state(session_id)
        message = "Lint still fails after " + str(MAX_FIX_ROUNDS) + " fix rounds; the agent stopped retrying. Run the Lint command from AGENTS.md to see what is left."
        print(json.dumps({"systemMessage": message}))
        return 0
    save_rounds_used(session_id, rounds_used + 1)
    lint_output = result.stdout + result.stderr
    round_number = rounds_used + 1
    header = "Lint failed (fix round " + str(round_number) + " of " + str(MAX_FIX_ROUNDS) + "). Fix these before finishing:"
    print(header, file=sys.stderr)
    print(lint_output, file=sys.stderr)
    return EXIT_SEND_BACK_TO_AGENT


def main() -> int:
    """Read the flags and run the chosen check."""
    arguments = sys.argv[1:]
    if "--help" in arguments or len(arguments) == 0:
        print(HELP_TEXT)
        return 0
    dry_run = "--dry-run" in arguments
    # Claude Code sets CLAUDE_PROJECT_DIR for hooks; the commands above are
    # relative to the project root, so work from there.
    project_folder = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_folder != "":
        os.chdir(project_folder)
    if "--format-edited-file" in arguments:
        return format_edited_file(dry_run)
    if "--lint-before-stop" in arguments:
        return lint_before_stop(dry_run)
    print("Unknown flag. Try --help. (Retrying the same command will not help.)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
