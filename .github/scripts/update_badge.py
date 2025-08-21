name: Update TryHackMe Badge

on:
  schedule:
    # Run every 6 hours
    - cron: '0 */6 * * *'
  workflow_dispatch: # Allow manual trigger
  push:
    branches: [ main ]

jobs:
  update-badge:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
        
    - name: Install dependencies
      run: |
        pip install requests pillow
        
    - name: Fetch TryHackMe stats and generate badge
      env:
        THM_USER_ID: "anishalx"
      run: |
        python .github/scripts/update_badge.py
        
    - name: Commit and push changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add assets/tryhackme-badge.svg
        git diff --staged --quiet || git commit -m "Update TryHackMe badge [automated]"
        git push
