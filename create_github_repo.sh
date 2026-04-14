#!/bin/bash
# Create the SphereForge GitHub repo and push.
# Usage: ./create_github_repo.sh <YOUR_GITHUB_PAT>
#
# To generate a new PAT:
#   1. Go to https://github.com/settings/tokens
#   2. Click "Generate new token (classic)"
#   3. Select scopes: repo (full control)
#   4. Copy the token and pass it to this script

set -euo pipefail

PAT="${1:?Usage: $0 <GITHUB_PAT>}"
REPO_NAME="SphereForge"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Creating GitHub repo: $REPO_NAME ==="

# Create repo via API
RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $PAT" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{
    \"name\":\"$REPO_NAME\",
    \"description\":\"Transform 360° camera footage into high-quality 3D Gaussian Splat scenes\",
    \"private\":false,
    \"has_issues\":true,
    \"has_projects\":true,
    \"has_wiki\":true,
    \"auto_init\":false
  }")

# Extract clone URL
CLONE_URL=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('clone_url',''))")
HTML_URL=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('html_url',''))")

if [ -z "$CLONE_URL" ]; then
  echo "ERROR: Failed to create repo."
  echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','unknown error'))"
  exit 1
fi

echo "Repo created: $HTML_URL"

# Init git and push
cd "$PROJECT_DIR"

if [ ! -d ".git" ]; then
  git init
  echo "Git repo initialized"
fi

# Configure remote
if git remote get-url origin &>/dev/null; then
  git remote set-url origin "$CLONE_URL"
else
  git remote add origin "$CLONE_URL"
fi
echo "Remote set to: $CLONE_URL"

# Stage all files
git add -A
git status

# Commit
git commit -m "Initial commit: SphereForge 8-stage 360° Gaussian Splat pipeline

- 20,000+ lines of Python across 90 source + 11 test files
- All 8 pipeline stages implemented
- DAP (Depth Any Panoramas) for ERP-native depth estimation
- gsplat integration for differentiable rasterization
- Stable Diffusion + EscherNet inpainting for occlusion recovery
- ErpGS distortion-aware loss + 360-GeoGS depth/normal regularization
- ImprovedGS+ densification (EAS + LAS + RAP)
- Multiple export formats: PLY, SOG, SPZ, HTML viewer
- GPLv3+ license"

# Push
git branch -M main
git push -u origin main

echo ""
echo "=== Done! ==="
echo "Repo URL: $HTML_URL"
