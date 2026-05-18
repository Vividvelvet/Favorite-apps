#!/usr/bin/env python3
"""
Script to update README.md with the last updated date for each GitHub repository.
This script is run by GitHub Actions on a schedule.
"""

import re
import os
from datetime import datetime
import requests

# GitHub API token from environment
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Pattern to match GitHub links in markdown
# Matches: [**App Name**](https://github.com/owner/repo)
GITHUB_LINK_PATTERN = r'\[(\*\*[^*]+\*\*)\]\((https://github\.com/([^/]+)/([^/)]+))\)'

def get_last_updated(owner: str, repo: str) -> str:
    """
    Fetch the last updated date for a GitHub repository.
    Returns a formatted date string like "2026-05-18"
    """
    try:
        url = f'https://api.github.com/repos/{owner}/{repo}'
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Use pushed_at as the last update date
        pushed_at = data.get('pushed_at')
        if pushed_at:
            # Parse and format the date (YYYY-MM-DD)
            date_obj = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
            return date_obj.strftime('%Y-%m-%d')
        return 'Unknown'
    except Exception as e:
        print(f"Error fetching {owner}/{repo}: {e}")
        return 'Unknown'

def update_readme():
    """
    Update README.md with last updated dates for all GitHub repositories.
    """
    # Read current README
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Find all GitHub links and replace them with dated versions
    def replace_link(match):
        app_name = match.group(1)  # e.g., **Track and Graph**
        full_url = match.group(2)  # e.g., https://github.com/SamAmco/track-and-graph
        owner = match.group(3)     # e.g., SamAmco
        repo = match.group(4)      # e.g., track-and-graph
        
        # Get last updated date
        last_updated = get_last_updated(owner, repo)
        
        # Return link with date appended
        return f'[{app_name}]({full_url}) – Updated: {last_updated}'
    
    # Replace all GitHub links with dated versions
    updated_content = re.sub(GITHUB_LINK_PATTERN, replace_link, content)
    
    # Write back if there were changes
    if updated_content != original_content:
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print("README.md updated successfully!")
    else:
        print("No changes needed.")

if __name__ == '__main__':
    update_readme()
