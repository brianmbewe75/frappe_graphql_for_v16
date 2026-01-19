#!/bin/bash
# Script to push frappe_graphql_for_v16 to GitHub
# Usage: ./push_to_github.sh

cd /home/frappe/frappe-bench/apps/frappe_graphql

echo "=== Pushing to GitHub ==="
echo "Repository: https://github.com/brianmbewe75/frappe_graphql_for_v16"

# Set remote to HTTPS (you'll need to enter credentials)
git remote set-url origin https://github.com/brianmbewe75/frappe_graphql_for_v16.git

# Push to repository
echo "Pushing to origin/master..."
git push -u origin master

echo "Done!"
