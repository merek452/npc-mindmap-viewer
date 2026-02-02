# Push to GitHub - Authentication Help

You're getting a permission error because Git is using cached credentials for a different GitHub account.

## Solution Options

### Option 1: Use Personal Access Token (Recommended)

1. **Create a Personal Access Token:**
   - Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a name like "NPC Mind Map Viewer"
   - Select scope: `repo` (full control of private repositories)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again!)

2. **Update the remote URL to include your username:**
   ```bash
   git remote set-url origin https://merek452@github.com/merek452/npc-mindmap-viewer.git
   ```

3. **Push (it will prompt for password - use the token):**
   ```bash
   git push -u origin main
   ```
   - Username: `merek452`
   - Password: **Paste your Personal Access Token** (not your GitHub password)

### Option 2: Use GitHub CLI (Easier)

If you have GitHub CLI installed:
```bash
gh auth login
gh repo set-default merek452/npc-mindmap-viewer
git push -u origin main
```

### Option 3: Clear Cached Credentials

1. **Clear Windows Credential Manager:**
   - Press `Win + R`, type `control /name Microsoft.CredentialManager`
   - Go to "Windows Credentials"
   - Find any `git:https://github.com` entries
   - Delete them

2. **Then try pushing again:**
   ```bash
   git push -u origin main
   ```

### Option 4: Use SSH Instead

1. **Generate SSH key (if you don't have one):**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **Add SSH key to GitHub:**
   - Copy the public key: `cat ~/.ssh/id_ed25519.pub`
   - Go to GitHub → Settings → SSH and GPG keys → New SSH key
   - Paste and save

3. **Change remote to SSH:**
   ```bash
   git remote set-url origin git@github.com:merek452/npc-mindmap-viewer.git
   git push -u origin main
   ```

## Quick Command Reference

After setting up authentication, run:
```bash
cd "C:\Users\KeremBray\Documents\Development\Obsidian\Genia\NPCs\mindmap_viewer"
git push -u origin main
```

## Verify It Worked

After pushing, check your repository:
https://github.com/merek452/npc-mindmap-viewer

You should see all your files there!

