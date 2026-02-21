#!/bin/bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOK_DIR="$REPO_ROOT/.git/hooks"
cp "$REPO_ROOT/hooks/pre-commit" "$HOOK_DIR/pre-commit"
chmod +x "$HOOK_DIR/pre-commit"
echo "GreenLinter pre-commit hook installed successfully."
