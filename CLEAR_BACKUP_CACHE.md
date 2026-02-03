# Fix for "Load backup?" Prompt on GitHub Pages

## Issue

When opening the Visual Editor on GitHub Pages, you see:
```
Found backup from 03/02/2026, 09:32:59 that differs from current data. Load it?
```

## Cause

This is old localStorage data from before the Firebase migration. The NPC Editor has an auto-save feature that stores backups locally.

## Solution

### Option 1: Clear in Browser (Recommended)

**On the GitHub Pages site:**

1. Open browser Developer Tools (F12)
2. Go to "Console" tab
3. Paste this command and press Enter:
   ```javascript
   localStorage.removeItem('npc_relationships_backup');
   location.reload();
   ```

This clears the old backup and reloads the page.

### Option 2: Clear All Site Data

**Chrome/Edge:**
1. Click the lock icon in address bar
2. Click "Site settings"
3. Click "Clear data"
4. Reload the page

**Firefox:**
1. Click the lock icon in address bar
2. Click "Clear cookies and site data"
3. Reload the page

### Option 3: Just Click "No"

The backup is from before Firebase migration and is outdated. Just:
1. Click "No" or "Cancel"
2. The editor will use the current Firebase data
3. The prompt won't appear again after you save something new

## Why This Happens

The NPC Editor auto-saves to localStorage every 30 seconds as a backup. This backup is from when NPCs were stored locally (before Firebase). Now that NPCs are in Firebase, this old backup is outdated.

## Prevention

Once you clear it or click "No", the prompt won't appear again because:
- The editor will save new backups to localStorage
- Those new backups will match the Firebase data
- Or you can disable auto-save in the editor

## For Future

If you want to disable the backup prompt entirely, you can modify the editor code, but it's actually a useful feature if you're working offline or Firebase is down.
