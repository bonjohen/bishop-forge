# BishopForge Deployment Guide

This guide walks you through deploying BishopForge to GitHub Pages with a custom domain.

## Prerequisites

- GitHub account (bonjohen)
- Access to DNS settings for johnboen.com domain
- Git installed locally
- Node.js 20+ installed

## Step 1: Initialize Git Repository

```bash
# Navigate to project root
cd c:\Projects\bishop-forge

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: BishopForge chess application"
```

## Step 2: Create GitHub Repository

### Option A: Using GitHub CLI (if installed)
```bash
gh repo create bishop-forge --public --source=. --remote=origin
git push -u origin main
```

### Option B: Using GitHub Web Interface

1. Go to https://github.com/new
2. Repository name: `bishop-forge`
3. Description: "A minimal chess web application with vanilla JavaScript frontend"
4. Visibility: **Public** (required for GitHub Pages on free tier)
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

7. Add the remote and push:
```bash
git remote add origin https://github.com/bonjohen/bishop-forge.git
git branch -M main
git push -u origin main
```

## Step 3: Enable GitHub Pages

1. Go to your repository: https://github.com/bonjohen/bishop-forge
2. Click **Settings** tab
3. Click **Pages** in the left sidebar
4. Under "Build and deployment":
   - Source: **GitHub Actions** (not "Deploy from a branch")
5. The workflow will automatically deploy on the next push to main

## Step 4: Configure Custom Domain in GitHub

1. Still in **Settings > Pages**
2. Under "Custom domain":
   - Enter: `bishop-forge.johnboen.com`
   - Click **Save**
3. Wait for DNS check (may take a few minutes)
4. Once DNS is verified, check **Enforce HTTPS** (recommended)

## Step 5: Configure DNS Settings

Add the following DNS records to your `johnboen.com` domain:

### DNS Records to Add:

**CNAME Record:**
```
Type:  CNAME
Name:  bishop-forge
Value: bonjohen.github.io
TTL:   3600 (or your provider's default)
```

### Alternative: If your DNS provider doesn't support CNAME for subdomains

**A Records (use all four):**
```
Type:  A
Name:  bishop-forge
Value: 185.199.108.153
TTL:   3600

Type:  A
Name:  bishop-forge
Value: 185.199.109.153
TTL:   3600

Type:  A
Name:  bishop-forge
Value: 185.199.110.153
TTL:   3600

Type:  A
Name:  bishop-forge
Value: 185.199.111.153
TTL:   3600
```

**Note:** DNS propagation can take 5 minutes to 48 hours depending on your provider.

## Step 6: Verify Deployment

1. Wait for GitHub Actions workflow to complete:
   - Go to https://github.com/bonjohen/bishop-forge/actions
   - Watch the "Deploy to GitHub Pages" workflow
   - Should turn green when successful

2. Test the deployment:
   - **GitHub Pages URL**: https://bonjohen.github.io/bishop-forge/
   - **Custom Domain**: https://bishop-forge.johnboen.com/

3. Verify functionality:
   - Chess board displays correctly
   - Pieces can be moved
   - All controls work (New Game, Undo, etc.)
   - Pawn promotion works
   - Castling works

## Step 7: Future Updates

To deploy updates:

```bash
# Make your changes
git add .
git commit -m "Description of changes"
git push

# GitHub Actions will automatically build and deploy
```

## Troubleshooting

### DNS Not Resolving
- Check DNS records are correct
- Wait up to 48 hours for propagation
- Use `nslookup bishop-forge.johnboen.com` to check DNS
- Use `dig bishop-forge.johnboen.com` on Mac/Linux

### GitHub Pages Not Building
- Check Actions tab for errors
- Ensure repository is public
- Verify GitHub Pages is enabled in Settings

### 404 Errors on Custom Domain
- Verify CNAME file exists in `frontend/public/CNAME`
- Check custom domain is set in GitHub Settings > Pages
- Ensure DNS is properly configured

### Build Failures
- Check that all tests pass locally: `cd frontend && npm test -- --run`
- Verify build works locally: `cd frontend && npm run build`
- Check GitHub Actions logs for specific errors

## Files Created for Deployment

- `.gitignore` - Excludes node_modules, dist, etc.
- `.github/workflows/deploy.yml` - GitHub Actions workflow
- `frontend/public/CNAME` - Custom domain configuration
- `frontend/vite.config.js` - Updated with base path
- `DEPLOYMENT.md` - This file

## Architecture Notes

- **Frontend**: Static files served from GitHub Pages
- **Backend**: Optional (not deployed with GitHub Pages)
  - Can be deployed separately to Render, Railway, Fly.io, etc.
  - Update `frontend/src/core/backendClient.js` with backend URL when ready

## Security Notes

- HTTPS is automatically provided by GitHub Pages
- No sensitive data is stored in the frontend
- Backend API (when deployed) should use CORS and rate limiting

