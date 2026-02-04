# Firebase Storage CORS Fix 🔧

## The Error Explained

```
Access to XMLHttpRequest at 'https://firebasestorage.googleapis.com/...' 
from origin 'null' has been blocked by CORS policy
```

### What This Means:

**CORS (Cross-Origin Resource Sharing)** is a security feature that blocks web requests from unauthorized origins.

**Origin 'null'** = You're opening the HTML file directly (`file://` protocol), which browsers treat as having no origin.

**Firebase Storage** blocks `null` origin by default for security.

---

## ✅ Quick Fixes

### **Option 1: Use a Local Web Server** (Recommended for Testing)

#### Windows - Double-click this file:
```
start_local_server.bat
```

Then open: `http://localhost:8000/npc_mindmap_viewer.html`

**Or manually:**
```powershell
cd "C:\Users\KeremBray\Documents\Development\Obsidian\Genia\NPCs\mindmap_viewer"
python -m http.server 8000
```

---

### **Option 2: Deploy to GitHub Pages** (Recommended for Production)

Push your changes to GitHub and access via:
```
https://[your-username].github.io/[repo-name]/npc_mindmap_viewer.html
```

GitHub Pages provides a proper HTTP origin, so uploads will work!

---

### **Option 3: Configure Firebase Storage CORS** (Advanced)

If you want local `file://` uploads to work, you need to configure Firebase Storage CORS rules.

#### Step 1: Create `cors.json`

```json
[
  {
    "origin": ["*"],
    "method": ["GET", "POST", "PUT", "DELETE"],
    "maxAgeSeconds": 3600
  }
]
```

#### Step 2: Install Google Cloud SDK

Download from: https://cloud.google.com/sdk/docs/install

#### Step 3: Apply CORS Rules

```bash
gsutil cors set cors.json gs://age-of-reckoning.firebasestorage.app
```

⚠️ **Warning:** Using `"*"` allows uploads from any origin. Only do this for testing!

---

## 🔒 Firebase Storage Security Rules

You also need to configure Firebase Storage security rules to allow authenticated uploads.

### Go to Firebase Console:
1. Open: https://console.firebase.google.com/
2. Select project: **age-of-reckoning**
3. Go to: **Storage** → **Rules** tab

### Add These Rules:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Allow authenticated users to read/write NPC portraits
    match /npc_portraits/{filename} {
      allow read: if request.auth != null;
      allow write: if request.auth != null 
                   && request.resource.size < 5 * 1024 * 1024  // Max 5MB
                   && request.resource.contentType.matches('image/.*');  // Images only
    }
    
    // Deny all other access
    match /{allPaths=**} {
      allow read, write: if false;
    }
  }
}
```

### Rule Breakdown:

```javascript
allow read: if request.auth != null;
```
✅ Only authenticated users can view images

```javascript
allow write: if request.auth != null 
          && request.resource.size < 5 * 1024 * 1024
```
✅ Only authenticated users can upload
✅ Max 5MB file size

```javascript
&& request.resource.contentType.matches('image/.*');
```
✅ Only image files allowed

---

## 🧪 Testing Upload Feature

### **Test 1: Local Server**

1. Run `start_local_server.bat`
2. Open `http://localhost:8000/npc_mindmap_viewer.html`
3. Go to Visual Editor tab
4. Click "📤 Upload" button
5. Select an image
6. **Expected:** Upload succeeds! ✅

---

### **Test 2: GitHub Pages**

1. Push changes to GitHub
2. Open `https://[username].github.io/[repo]/npc_mindmap_viewer.html`
3. Try uploading an image
4. **Expected:** Upload succeeds! ✅

---

### **Test 3: Direct File (Will Fail Without CORS)**

1. Open `npc_mindmap_viewer.html` directly
2. Try uploading an image
3. **Expected:** CORS error ❌

**This is normal!** Browser security blocks `file://` uploads.

---

## 🎯 Recommended Workflow

### **For Development (DM/You):**
```
1. Use local server: start_local_server.bat
2. Test uploads at http://localhost:8000
3. Push to GitHub when ready
```

### **For Players (Everyone):**
```
1. Access via GitHub Pages
2. Upload works automatically ✅
3. No CORS issues!
```

---

## 🔍 Debugging CORS Errors

### Check Browser Console:

**Good (No CORS error):**
```
✅ Firebase Storage initialized
✅ Image uploaded successfully
```

**Bad (CORS error):**
```
❌ Access to XMLHttpRequest blocked by CORS policy
❌ Origin 'null' has been blocked
```

### Solutions by Error:

| Error | Cause | Solution |
|-------|-------|----------|
| Origin 'null' | Opening HTML directly | Use local server or GitHub Pages |
| No 'Access-Control-Allow-Origin' | CORS not configured | Configure CORS rules (see above) |
| 401 Unauthorized | Not logged in | Authenticate with Firebase |
| 403 Forbidden | Storage rules too strict | Update Firebase Storage rules |

---

## 🚀 Quick Start Guide

### **Immediate Solution (Right Now):**

1. Open PowerShell in the mindmap_viewer folder
2. Run:
   ```powershell
   python -m http.server 8000
   ```
3. Open browser to: `http://localhost:8000/npc_mindmap_viewer.html`
4. Try uploading again!

**Upload should work now!** ✅

---

### **Long-term Solution (For Players):**

1. Push to GitHub
2. Share GitHub Pages URL with players
3. Everyone can upload from any device
4. No CORS issues!

---

## 💡 Why This Happens

### Browser Security Model:

```
file:// protocol (Opening HTML directly)
    ↓
Origin = "null"
    ↓
Firebase Storage blocks "null" origin
    ↓
CORS error ❌
```

```
http:// protocol (Local server or GitHub Pages)
    ↓
Origin = "http://localhost:8000" or "https://github.io"
    ↓
Firebase Storage allows known origins
    ↓
Upload works ✅
```

---

## 📋 Checklist

### Before Upload Works:
- [ ] Firebase Storage rules configured (allow authenticated uploads)
- [ ] Using HTTP origin (local server or GitHub Pages)
- [ ] User is authenticated with Firebase
- [ ] Storage bucket exists and is active

### After Upload Works:
- [x] Images upload successfully
- [x] URLs saved to Firebase Database
- [x] All players can view images
- [x] Automatic compression working

---

## 🎉 Summary

**The CORS error is normal when opening HTML files directly.**

### Solutions:
1. ✅ **Use local server** (`start_local_server.bat`)
2. ✅ **Use GitHub Pages** (recommended for players)
3. ⚠️ **Configure CORS** (advanced, allows file:// but less secure)

### Quick Fix:
```powershell
python -m http.server 8000
```

Then open: `http://localhost:8000/npc_mindmap_viewer.html`

**Upload will work!** 🚀
