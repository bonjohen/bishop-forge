# Quick Deployment Steps

## 1. Initialize and Push to GitHub

```bash
# In c:\Projects\bishop-forge
git init
git add .
git commit -m "Initial commit: BishopForge chess application"

# Create repo on GitHub (go to https://github.com/new)
# Name: bishop-forge
# Public repository
# Don't initialize with anything

# Then push
git remote add origin https://github.com/bonjohen/bishop-forge.git
git branch -M main
git push -u origin main
```

## 2. Enable GitHub Pages

1. Go to: https://github.com/bonjohen/bishop-forge/settings/pages
2. Under "Build and deployment" → Source: **GitHub Actions**
3. Under "Custom domain" → Enter: `bishop-forge.johnboen.com` → Save

## 3. Configure DNS (at your DNS provider)

Add this CNAME record:

```
Type:  CNAME
Name:  bishop-forge
Value: bonjohen.github.io
TTL:   3600
```

## 4. Wait and Verify

- GitHub Actions: https://github.com/bonjohen/bishop-forge/actions
- Once deployed, visit: https://bishop-forge.johnboen.com

## Done! 🎉

Future updates: just `git add . && git commit -m "message" && git push`

