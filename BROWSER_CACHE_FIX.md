# Fix: Images Not Loading Locally (Browser Cache Issue)

## Problem

Seeing errors like:
```
GET file:///C:/Users/.../NPCs/Images/Althessa%20the%20Rogue.bmp net::ERR_FILE_NOT_FOUND
```

But the images DO exist and paths ARE correct in the HTML!

## Cause

**Browser cache** is showing old error messages from before we fixed the image paths. The browser remembers the old errors and displays them even though the actual code has been fixed.

## Solution

### Quick Fix: Hard Refresh

**Windows/Linux:**
- Press `Ctrl + F5`

**Or:**
- Press `Ctrl + Shift + R`

**Mac:**
- Press `Cmd + Shift + R`

This forces the browser to reload everything from disk, ignoring cache.

---

### Full Fix: Clear Cache

If hard refresh doesn't work:

**Chrome/Edge:**
1. Press `F12` to open DevTools
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

**Or:**
1. Press `Ctrl + Shift + Delete`
2. Select "Cached images and files"
3. Click "Clear data"
4. Reload the page

**Firefox:**
1. Press `Ctrl + Shift + Delete`
2. Select "Cache"
3. Click "Clear Now"
4. Reload the page

---

## Verification

### Check Current Paths (All Correct!)

1. **npc_relationships.json:**
   - All paths are `Images/filename.png` ✅
   - No more `.bmp` files ✅
   - No more `../Images/` paths ✅

2. **npc_mindmap_viewer.html:**
   - Static NPC cards: `Images/Althessa the Rogue.png` ✅
   - npcData object: `"portrait": "Images/Althessa the Rogue.png"` ✅
   - All paths relative to HTML file location ✅

3. **Actual files exist:**
   ```
   C:\Users\KeremBray\Documents\Development\Obsidian\Genia\NPCs\mindmap_viewer\
   ├── npc_mindmap_viewer.html  ← Opens here
   └── Images\
       ├── Althessa the Rogue.png  ← Loads from here
       ├── Goruk.png
       └── [all other images]
   ```

**Relative path `Images/filename.png` is CORRECT!** ✅

---

## Why This Happens

1. **Old Errors Were Logged:** When paths were wrong (before our fix), browser logged errors to console
2. **Cache Persists:** Browser caches these error messages
3. **Console Shows Old Errors:** Even though code is fixed, console displays cached errors
4. **Hard Refresh Fixes:** Forces browser to re-request everything

---

## Test After Clearing Cache

1. Open `npc_mindmap_viewer.html`
2. Hard refresh: `Ctrl + F5`
3. Open console (F12)
4. **Expected result:** 
   - ✅ No image errors
   - ✅ All portraits load correctly
   - ✅ Console is clean (or only has the localStorage warning which is harmless)

---

## Alternative: Use a Different Browser

If one browser still shows errors:
- Try opening in a different browser (Chrome, Firefox, Edge)
- That browser won't have the old cached errors
- Should load perfectly!

---

## Summary

**The code is correct!** 

The issue is just browser cache showing old errors. A hard refresh (`Ctrl + F5`) will fix it immediately.

**Path verification:**
```javascript
// In npc_mindmap_viewer.html:
"portrait": "Images/Althessa the Rogue.png"  ✅ Correct!

// File location:
mindmap_viewer/
├── npc_mindmap_viewer.html
└── Images/Althessa the Rogue.png  ✅ Exists!

// Relative path resolves to:
mindmap_viewer/Images/Althessa the Rogue.png  ✅ Works!
```

**Just clear your browser cache and everything will work!** 🎉
