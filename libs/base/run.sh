python3 -m venv .venv

# Make the sandbox active in the current shell session
source .venv/bin/activate

# Install pinned pip first
pip install -r $(git rev-parse --show-toplevel)/pip-requirements.txt

# Install shared development dependencies and project/library-specific dependencies
pip install -r $(git rev-parse --show-toplevel)/dev-requirements.txt -r requirements.txt
