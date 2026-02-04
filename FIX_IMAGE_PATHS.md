# Fix: Images Still Not Loading (Firebase Has Old Data)

## The Real Problem

Your **JSON and HTML files are correct**, but **Firebase has old data** with the wrong image paths!

### What's Happening:

1. ✅ **npc_relationships.json** has correct paths: `Images/filename.png`
2. ✅ **npc_mindmap_viewer.html** has correct paths: `Images/filename.png`
3. ❌ **Firebase** still has old paths: `../Images/filename.bmp`
4. 🔄 When the app loads, Firebase data **overrides** the correct JSON data
5. ❌ Browser tries to load images from wrong paths

### Evidence:

**Browser error shows:**
```
GET file:///C:/Users/.../NPCs/Images/Veris the Ex-Sorcerer.bmp
                          ^^^^ Wrong directory! Missing /mindmap_viewer/
                                                       ^^^ Wrong format! Should be .png
```

**Should be:**
```
GET file:///C:/Users/.../NPCs/mindmap_viewer/Images/Veris the Ex-Sorcerer.png
```

---

## Solution: Clear Firebase NPC Data

### Option 1: Use the Clear Tool (Easiest)

1. **Open** `clear_firebase_npcs.html` in your browser
2. **Click** "View Current Firebase Data" to confirm old paths exist
3. **Click** "Clear Firebase NPC Data"
4. **Reload** `npc_mindmap_viewer.html`
5. **Check console** - should see "Migrating NPCs to Firebase..."
6. ✅ **All images should now load!**

---

### Option 2: Manual Clear (Alternative)

If you prefer to manually clear:

1. Open `npc_mindmap_viewer.html`
2. Open browser console (F12)
3. Paste and run:

```javascript
firebase.database().ref('campaigns/genia/npc_data').remove()
  .then(() => {
    console.log('✅ Cleared! Now reload the page.');
  });
```

4. Reload the page
5. ✅ Images should load correctly!

---

## Why This Happened

### Timeline:

1. **Originally:** NPCs had paths like `../Images/name.bmp`
2. **We fixed:** Changed JSON to `Images/name.png`
3. **Problem:** Old data was already saved to Firebase
4. **Result:** Firebase keeps serving old paths even though JSON is fixed
5. **Solution:** Delete Firebase data to force reload from fixed JSON

---

## How the App Works

```
1. App loads
   ↓
2. Checks Firebase for NPC data
   ↓
3a. If Firebase has data → Use it (OVERRIDES JSON)
3b. If Firebase empty → Load from JSON, then save to Firebase
```

**The issue:** Firebase had old data, so step 3a was using wrong paths!

**The fix:** Clear Firebase, forcing step 3b to run with correct JSON paths!

---

## Verification After Fix

### Check Console:

**You should see:**
```
Migrating NPCs to Firebase...
Successfully migrated X NPCs to Firebase
```

**You should NOT see:**
```
Loaded X NPCs from Firebase
```
(This means it's using old data!)

### Check Images:

**All portraits should load correctly, no 404 errors!**

---

## Technical Details

### Current File Structure:

```
C:\Users\KeremBray\Documents\Development\Obsidian\Genia\NPCs\
├── mindmap_viewer\
│   ├── npc_mindmap_viewer.html       ← Opens here
│   ├── npc_relationships.json         ← Correct paths ✅
│   ├── clear_firebase_npcs.html       ← Use this tool!
│   └── Images\
│       ├── Tivannis Fal.png          ← File exists ✅
│       ├── Veris the Ex-Sorcerer.png ← File exists ✅
│       └── ... (all other images)
```

### Correct Path Format:

```javascript
// In JSON/HTML:
"portrait": "Images/Althessa the Rogue.png"

// Resolves to:
mindmap_viewer/Images/Althessa the Rogue.png  ✅
```

### Old Path Format (in Firebase):

```javascript
// Old format (WRONG):
"portrait": "../Images/Althessa the Rogue.bmp"

// Resolves to:
NPCs/Images/Althessa the Rogue.bmp  ❌ Wrong directory!
```

---

## Summary

### The Issue:
- ❌ Firebase has old portrait paths (`../Images/*.bmp`)
- ✅ JSON has correct paths (`Images/*.png`)
- 🔄 Firebase overrides JSON on page load
- ❌ Images fail to load from wrong paths

### The Fix:
1. 🧹 Clear Firebase NPC data
2. 🔄 App reloads from correct JSON
3. 💾 Saves correct paths to Firebase
4. ✅ Images load perfectly!

### Action Required:
**Open `clear_firebase_npcs.html` and click "Clear Firebase NPC Data"**

Then reload `npc_mindmap_viewer.html` and everything will work! 🎉
