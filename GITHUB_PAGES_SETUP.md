# GitHub Pages Setup Guide

This guide will walk you through setting up your NPC Mind Map Viewer on GitHub Pages for free hosting.

## Prerequisites

- A GitHub account (free)
- Git installed on your computer
- Your `mindmap_viewer` folder ready

## Step-by-Step Instructions

### Step 1: Create a GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the repository details:
   - **Repository name:** `npc-mindmap-viewer` (or any name you prefer)
   - **Description:** "D&D NPC Relationship Mind Map Viewer"
   - **Visibility:** Choose **Public** (required for free GitHub Pages) or **Private** (if you have GitHub Pro)
   - **DO NOT** initialize with README, .gitignore, or license (we'll add files manually)
5. Click **"Create repository"**

### Step 2: Prepare Your Files

1. **Create a `.gitignore` file** in your `mindmap_viewer` folder:
   ```
   __pycache__/
   *.pyc
   *.pyo
   *.pyd
   .Python
   *.backup
   *.backup*
   *.png
   *.md
   !README.md
   ```

2. **Create a `README.md`** file (optional but recommended):
   ```markdown
   # NPC Mind Map Viewer
   
   Interactive D&D campaign NPC relationship tracker and mind map viewer.
   
   ## Features
   - NPC relationship visualization
   - Interactive mind map
   - Inventory tracker
   - NPC card view
   - Editor for managing relationships
   
   ## Usage
   Open `npc_mindmap_viewer.html` in a web browser.
   ```

### Step 3: Initialize Git and Push to GitHub

Open a terminal/command prompt in your `mindmap_viewer` folder and run:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: NPC Mind Map Viewer"

# Add GitHub repository as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/npc-mindmap-viewer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note:** You'll be prompted for your GitHub username and password (or use a Personal Access Token).

### Step 4: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on **"Settings"** (top menu)
3. Scroll down to **"Pages"** in the left sidebar
4. Under **"Source"**, select:
   - **Branch:** `main` (or `master` if that's your branch)
   - **Folder:** `/ (root)` or `/docs` if you put files in a docs folder
5. Click **"Save"**

### Step 5: Access Your Site

After a few minutes, your site will be available at:
```
https://YOUR_USERNAME.github.io/npc-mindmap-viewer/
```

**Note:** It may take 5-10 minutes for the site to be available the first time.

### Step 6: Update Files (Future Changes)

Whenever you make changes:

```bash
# Navigate to your mindmap_viewer folder
cd path/to/mindmap_viewer

# Regenerate HTML if needed
python generate_mindmap.py

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push
```

GitHub Pages will automatically update your site (usually within 1-2 minutes).

## Custom Domain (Optional)

If you have a custom domain:

1. In GitHub Pages settings, enter your custom domain
2. Add a `CNAME` file to your repository root with your domain name
3. Update your DNS records:
   - Type: `CNAME`
   - Name: `www` (or `@` for root)
   - Value: `YOUR_USERNAME.github.io`

## Troubleshooting

### Site Not Loading
- Wait 5-10 minutes after first setup
- Check repository is **Public** (or you have GitHub Pro)
- Verify branch and folder settings in Pages settings
- Check for errors in repository Actions tab

### Images Not Loading
- Ensure image paths use relative paths (e.g., `../../Images/`)
- Check that images exist in the correct location
- Verify file names match exactly (case-sensitive)

### Changes Not Appearing
- Wait 1-2 minutes for GitHub to rebuild
- Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)
- Check repository for latest commit

## File Structure for GitHub Pages

Your repository should look like:
```
npc-mindmap-viewer/
├── npc_mindmap_viewer.html    (main file - this is what users access)
├── generate_mindmap.py         (generation script)
├── npc_relationships.json      (data file)
├── items.json                  (items data)
├── item_processor.py           (utility)
├── item_validator.py           (utility)
├── README.md                   (documentation)
└── .gitignore                  (git ignore file)
```

**Note:** The `Images/` folder should be in the parent directory (`../../Images/`) relative to the HTML file.

## Security Note

Since your repository will be public (for free GitHub Pages), be careful not to commit:
- Personal information
- API keys
- Sensitive campaign details (if you want to keep them private)

Consider using GitHub's private repositories if you have GitHub Pro, or use environment variables for sensitive data.

## Alternative: Use `/docs` Folder

If you prefer to keep generation scripts separate:

1. Create a `docs` folder
2. Put `npc_mindmap_viewer.html` and data files in `docs/`
3. In GitHub Pages settings, select `/docs` as the source folder
4. Keep generation scripts in the root

This keeps your repository cleaner.

## Next Steps

- Add a custom 404 page
- Set up automatic deployment with GitHub Actions
- Add analytics (optional)
- Share the link with your players!

