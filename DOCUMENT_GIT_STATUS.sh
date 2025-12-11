#!/bin/bash
# Git Status Documentation Script

cd /home/user/webapp

# Git status
cat > GIT_STATUS.md << EOF
# Git Status ($(date))

## Current Branch
\`\`\`
$(git branch --show-current)
\`\`\`

## Recent Commits (Last 10)
\`\`\`
$(git log --oneline -10)
\`\`\`

## Changed Files (vs origin/main)
\`\`\`
$(git diff --stat origin/main 2>/dev/null || echo "Already up to date with origin")
\`\`\`

## Uncommitted Changes
\`\`\`
$(git status --short)
\`\`\`

## Remote URL
\`\`\`
$(git remote -v)
\`\`\`

## Latest Commit Details
\`\`\`
$(git log -1 --stat)
\`\`\`

## File Count by Type
\`\`\`
Python files: $(find . -name "*.py" -type f | wc -l)
Markdown docs: $(find . -name "*.md" -type f | wc -l)
HTML templates: $(find . -name "*.html" -type f | wc -l)
CSS files: $(find . -name "*.css" -type f | wc -l)
\`\`\`
EOF

echo "✅ Git status saved to GIT_STATUS.md"
cat GIT_STATUS.md
