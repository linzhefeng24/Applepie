# Source from a project script after ROOT is set. No shell execution of .env contents.
eval "$(python3 "$ROOT/scripts/settings.py" --shell)"
