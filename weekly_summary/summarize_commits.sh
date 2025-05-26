#!/bin/bash

# Script to summarize git commits between two dates

# Store the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to repository root directory
cd "$REPO_ROOT"

# Check if start and end dates are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <start_date> <end_date>"
    exit 1
fi

START_DATE=$1
END_DATE=$2

echo "# Git Activity Summary ($START_DATE to $END_DATE)"
echo
echo "## Commit Log"
echo
echo "\`\`\`"
git log --pretty=format:"%h %ad %s" --date=short --after="$START_DATE" --before="$END_DATE"
echo "\`\`\`"
echo
echo "## Detailed Changes"
echo
echo "\`\`\`"
git log --after="$START_DATE" --before="$END_DATE" --stat --pretty=format:"--- %h ---%n%h %s%n"
echo "\`\`\`"
echo
echo "## Manual Summary"
echo
echo "Based on the above logs, summarize the changes into categories:"
echo
echo "- **Feature Additions:**"
echo "  - (List new features added)"
echo
echo "- **Bug Fixes:**"
echo "  - (List bugs that were fixed)"
echo
echo "- **Refactors:**"
echo "  - (List code restructuring or cleaning)"
echo
echo "- **Infrastructure Changes:**"
echo "  - (List changes to build, CI/CD, etc)"
echo
echo "- **Documentation:**"
echo "  - (List documentation updates)" 