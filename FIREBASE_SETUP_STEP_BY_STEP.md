# Firebase Setup - Step by Step (No npm Required!)

## ⚠️ Important: No npm Installation Needed!

This project uses Firebase via **CDN (script tags)**, not npm packages. You do NOT need to:
- ❌ Install npm
- ❌ Run `npm install firebase`
- ❌ Install `firebase-tools`
- ❌ Use Node.js

Everything is done through the **Firebase Console web interface**.

---

## Step 1: Create Firebase Project (Web Interface)

1. **Go to:** https://console.firebase.google.com
2. **Sign in** with your Google account
3. **Click "Add project"** (or "Create a project")
4. **Enter project name:** e.g., "D&D Campaign Manager" or "Genia Campaign"
5. **Click "Continue"**
6. **Disable Google Analytics** (optional, not needed for this)
7. **Click "Create project"**
8. **Wait for project to be created** (takes ~30 seconds)
9. **Click "Continue"**

---

## Step 2: Enable Realtime Database

1. In your Firebase project, look at the left sidebar
2. **Click "Build"** → **"Realtime Database"**
3. **Click "Create Database"**
4. **Choose location:** Select the region closest to you (e.g., `us-central1`)
5. **Choose security rules:** Select **"Start in test mode"**
6. **Click "Enable"**
7. **Wait for database to be created**

You'll see a URL like: `https://your-project-default-rtdb.firebaseio.com/`

---

## Step 3: Get Your Firebase Config (This is what you need!)

1. **Click the gear icon ⚙️** next to "Project Overview" (top left)
2. **Click "Project settings"**
3. **Scroll down** to the section called **"Your apps"**
4. **If you see a web app already:**
   - Click the `</>` icon next to it
   - You'll see your config
5. **If you DON'T see a web app:**
   - Click the **`</>` (Web) icon** in the "Your apps" section
   - **Register app:**
     - App nickname: "NPC Mind Map Viewer" (or any name)
     - **DO NOT check** "Also set up Firebase Hosting"
     - Click **"Register app"**
   - You'll see a screen with code that looks like this:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyC...",
  authDomain: "your-project.firebaseapp.com",
  databaseURL: "https://your-project-default-rtdb.firebaseio.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abc123def456"
};
```

6. **Copy these 7 values:**
   - `apiKey`
   - `authDomain`
   - `databaseURL`
   - `projectId`
   - `storageBucket`
   - `messagingSenderId`
   - `appId`

---

## Step 4: Set Security Rules (Simple Version)

1. Go back to **"Build"** → **"Realtime Database"**
2. Click the **"Rules"** tab
3. **Replace** the rules with:

```json
{
  "rules": {
    "campaigns": {
      "$campaignId": {
        ".read": "true",
        ".write": "true"
      }
    }
  }
}
```

4. **Click "Publish"**

⚠️ **Note:** These rules allow anyone with the HTML file to read/write. This is fine for a D&D campaign tool, but not for sensitive data.

---

## Step 5: Update Your Python Script

Now you have your Firebase config values. You need to update `generate_mindmap.py`:

**Option A: Edit the Python script directly**

1. Open `generate_mindmap.py`
2. Find lines 1633-1641 (the `FIREBASE_CONFIG` object)
3. Replace the placeholder values with your actual values:

```python
const FIREBASE_CONFIG = {{
    apiKey: "AIzaSyC...",  # Your actual apiKey
    authDomain: "your-project.firebaseapp.com",  # Your actual authDomain
    databaseURL: "https://your-project-default-rtdb.firebaseio.com",  # Your actual databaseURL
    projectId: "your-project-id",  # Your actual projectId
    storageBucket: "your-project.appspot.com",  # Your actual storageBucket
    messagingSenderId: "123456789012",  # Your actual messagingSenderId
    appId: "1:123456789012:web:abc123def456"  # Your actual appId
}};
```

**Option B: Use a setup script (if I create one)**

I can create a Python script that prompts you for these values and updates the config automatically.

---

## Step 6: Regenerate HTML

After updating the config:

```bash
cd "C:\Users\KeremBray\Documents\Development\Obsidian\Genia\NPCs\mindmap_viewer"
python generate_mindmap.py
```

This will generate `npc_mindmap_viewer.html` with your Firebase config embedded.

---

## Step 7: Test It

1. Open `npc_mindmap_viewer.html` in your browser
2. Open browser console (F12)
3. You should see: `"Firebase initialized successfully"`
4. Add an item to inventory
5. Open the same file in another browser window
6. The item should appear in both windows (real-time sync!)

---

## Troubleshooting

### "I don't see 'Your apps' section"
- Make sure you're in **Project settings** (gear icon → Project settings)
- Scroll down - it's below the "General" section

### "I don't see a web app icon `</>`"
- Click the `</>` icon to add a web app
- You don't need to set up hosting

### "databaseURL is missing"
- Make sure you've **created the Realtime Database** first (Step 2)
- The databaseURL should be: `https://your-project-default-rtdb.firebaseio.com`

### "Firebase not configured" in console
- Check that you replaced ALL placeholder values
- Make sure there are no extra quotes or typos
- Regenerate the HTML after making changes

### "Permission denied" error
- Make sure you published the security rules (Step 4)
- Check that the rules match exactly (including the `campaigns` structure)

---

## What You DON'T Need

- ❌ Node.js
- ❌ npm
- ❌ `npm install firebase`
- ❌ `npm install -g firebase-tools`
- ❌ Command line tools
- ❌ Firebase CLI

Everything is done through the **web interface** at https://console.firebase.google.com

---

## Summary

1. ✅ Create Firebase project (web interface)
2. ✅ Enable Realtime Database (web interface)
3. ✅ Get config from Project settings (web interface)
4. ✅ Update `generate_mindmap.py` with your config
5. ✅ Regenerate HTML
6. ✅ Test!

The Firebase config is just 7 strings you copy from the Firebase Console. No installation needed!
