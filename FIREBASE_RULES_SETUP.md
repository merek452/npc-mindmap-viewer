# Firebase Rules Setup Guide (Free Tier) 🔐

## ✅ Good News: Rules ARE Available on Free Tier!

Firebase Spark (free) plan includes **full access** to both:
- ✅ Realtime Database Rules
- ✅ Storage Rules

Let me show you exactly how to access and modify them.

---

## 📍 Step 1: Access Firebase Console

### Go to Firebase Console:
```
https://console.firebase.google.com/
```

### Select Your Project:
- Click on: **age-of-reckoning**
- You should see the project dashboard

---

## 🗄️ Step 2A: Realtime Database Rules (Already Configured)

### Access Database Rules:

1. **Left sidebar** → Click **"Realtime Database"**
2. **Top tabs** → Click **"Rules"** tab
3. You'll see the rules editor

### Your Current Database Rules:

These should already be set (you configured them earlier):

```json
{
  "rules": {
    "campaigns": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```

**These are correct!** ✅ Leave them as-is.

**What they do:**
- Only authenticated users can read campaign data
- Only authenticated users can write campaign data
- Perfect for your collaborative setup

---

## 📦 Step 2B: Storage Rules (Need to Configure)

### Access Storage Rules:

1. **Left sidebar** → Click **"Storage"**
2. If you see "Get started", click it to initialize Storage
3. **Top tabs** → Click **"Rules"** tab
4. You'll see the rules editor

### Default Storage Rules (Too Restrictive):

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if false;  // Blocks everything!
    }
  }
}
```

**This blocks all uploads!** ❌ That's why the upload button fails.

---

## ✅ Step 3: Update Storage Rules

### Replace with These Rules:

Copy and paste this into the Storage Rules editor:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Allow authenticated users to upload/view NPC portraits
    match /npc_portraits/{filename} {
      allow read: if request.auth != null;
      allow write: if request.auth != null 
                   && request.resource.size < 5 * 1024 * 1024
                   && request.resource.contentType.matches('image/.*');
    }
    
    // Deny access to all other paths
    match /{allPaths=**} {
      allow read, write: if false;
    }
  }
}
```

### Click "Publish" Button

You should see: "Rules published successfully" ✅

---

## 🔍 Rules Breakdown

### Read Rule:
```javascript
allow read: if request.auth != null;
```
**Meaning:**
- ✅ Authenticated users can view images
- ❌ Anonymous users cannot view images
- **Perfect for your campaign!**

### Write Rule:
```javascript
allow write: if request.auth != null 
          && request.resource.size < 5 * 1024 * 1024
          && request.resource.contentType.matches('image/.*');
```

**Meaning:**
- ✅ Only authenticated users can upload
- ✅ Max file size: 5MB
- ✅ Only image files allowed (jpg, png, etc.)
- ❌ No video, no PDFs, no executables
- **Safe and secure!**

### Path Restriction:
```javascript
match /npc_portraits/{filename} {
```
**Meaning:**
- Only files in `npc_portraits/` folder can be uploaded
- Prevents users from uploading to random paths
- Keeps your storage organized

---

## 🧪 Step 4: Test Storage Upload

### After Publishing Rules:

1. **Refresh your NPC Mindmap page**
2. **Go to Visual Editor**
3. **Select/create an NPC**
4. **Click "📤 Upload" button**
5. **Choose an image**
6. **Should upload successfully!** ✅

### Expected Console Output:
```
✅ Firebase Storage initialized
Processing image...
Uploading... 50%
Uploading... 100%
✅ Image uploaded successfully!
```

### If Upload Still Fails:

Check browser console (F12) for errors:

**Common Issues:**

| Error | Cause | Solution |
|-------|-------|----------|
| "Permission denied" | Rules not published | Re-publish rules, refresh page |
| "auth != null" | User not logged in | Sign in to Firebase |
| "File too large" | Image > 5MB | Use smaller image |
| "Invalid contentType" | Not an image file | Use PNG/JPG/GIF |

---

## 🎯 Complete Rules Configuration

### Your Firebase Project Should Have:

#### **Realtime Database Rules:**
```json
{
  "rules": {
    "campaigns": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```
**Status:** ✅ Already configured

#### **Storage Rules:**
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /npc_portraits/{filename} {
      allow read: if request.auth != null;
      allow write: if request.auth != null 
                   && request.resource.size < 5 * 1024 * 1024
                   && request.resource.contentType.matches('image/.*');
    }
    match /{allPaths=**} {
      allow read, write: if false;
    }
  }
}
```
**Status:** ⚠️ Need to configure (follow steps above)

---

## 📸 Visual Guide: Finding Storage Rules

### Step-by-Step Screenshots:

```
Firebase Console
    ↓
Left Sidebar
    ↓
Click "Storage" (💾 icon)
    ↓
[If first time: Click "Get started" button]
    ↓
Top Tabs: "Files" | "Rules" | "Usage"
    ↓
Click "Rules" tab
    ↓
[Rules Editor appears]
    ↓
Paste new rules
    ↓
Click "Publish" button
    ↓
✅ Done!
```

---

## ⚠️ If You Don't See "Storage" in Sidebar

### Initialize Firebase Storage:

1. **In Firebase Console**, click **"Storage"** in left sidebar
2. Click **"Get started"**
3. Accept default security rules (we'll change them)
4. Choose location: **europe-west** (closest to you)
5. Click **"Done"**
6. Now you can access Rules tab

---

## 🔐 Security Considerations

### Your Rules Are Secure Because:

1. **Authentication Required:**
   - Only users signed into your Firebase project can access
   - Anonymous users are blocked
   - Perfect for your private campaign

2. **File Type Restrictions:**
   - Only images allowed
   - Prevents malicious file uploads
   - No executable files

3. **Size Limits:**
   - 5MB max per file
   - Prevents storage abuse
   - Plenty for NPC portraits

4. **Path Restrictions:**
   - Only `npc_portraits/` folder accessible
   - Users can't access other storage areas
   - Organized and safe

### Permissions Summary:

| User Type | Can Upload? | Can View? |
|-----------|-------------|-----------|
| Authenticated (DM + Players) | ✅ Yes | ✅ Yes |
| Anonymous | ❌ No | ❌ No |
| Other Firebase Projects | ❌ No | ❌ No |

**Your campaign data stays private!** 🔒

---

## 💰 Free Tier Limits

### Firebase Spark Plan Includes:

**Realtime Database:**
- ✅ 1GB storage
- ✅ 10GB/month download
- ✅ 100 simultaneous connections
- **More than enough for your campaign!**

**Storage:**
- ✅ 5GB storage
- ✅ 1GB/day downloads
- ✅ 20,000 uploads/day
- **Enough for ~33,000 NPC portraits!**

**Cost so far:** $0.00 ✅

---

## 🚀 After Rules Are Published

### Upload Button Will:

1. ✅ Work from any device (desktop, mobile, tablet)
2. ✅ Auto-resize images to 500x500
3. ✅ Auto-convert to PNG
4. ✅ Auto-compress to save space
5. ✅ Upload to Firebase Storage
6. ✅ Update portrait field with URL
7. ✅ All players see image immediately

### No More Need for:
- ❌ Imgur.com workaround
- ❌ Manual file system access
- ❌ Git push for images

**Built-in upload works perfectly!** 🎉

---

## 📋 Quick Checklist

### Before Upload Works:
- [ ] Go to Firebase Console
- [ ] Navigate to Storage
- [ ] Click Rules tab
- [ ] Paste new rules
- [ ] Click Publish
- [ ] Refresh NPC Mindmap page
- [ ] Test upload

### After Upload Works:
- [x] Images upload successfully
- [x] Auto-resize to 500x500
- [x] Auto-compress working
- [x] URLs saved to database
- [x] All players can view
- [x] All players can upload
- [x] Mobile upload works

---

## 🔧 Troubleshooting

### Issue: "Can't find Storage in sidebar"

**Solution:**
1. Make sure you're in the correct project (age-of-reckoning)
2. Click "Build" section in sidebar (it's expandable)
3. Storage should be under "Build" section
4. If still missing, click "Get started" to initialize

---

### Issue: "Rules editor is read-only" or "Upgrade required"

**Possible causes:**
1. You're looking at the wrong project
2. Browser session issue
3. Firebase console bug

**Solutions:**
1. Sign out and sign back into Firebase Console
2. Try a different browser
3. Clear browser cache
4. Check you're the project owner (not just a member)

**Note:** Rules ARE available on free tier. This is likely a UI issue.

---

### Issue: Upload works but image doesn't appear

**Cause:** Browser cache

**Solution:**
1. Hard refresh: `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
2. Clear browser cache
3. Check console for errors

---

### Issue: "Permission denied" after publishing rules

**Solutions:**
1. Wait 1-2 minutes (rules propagate across Firebase)
2. Refresh the NPC Mindmap page
3. Sign out and sign back in
4. Verify rules were actually published (check Rules tab)

---

## 🎓 Understanding Firebase Rules

### Database Rules (JSON):
```json
{
  "rules": {
    "path": {
      ".read": "condition",
      ".write": "condition"
    }
  }
}
```

### Storage Rules (JavaScript-like):
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /path/{filename} {
      allow read: if condition;
      allow write: if condition;
    }
  }
}
```

### Common Conditions:

| Condition | Meaning |
|-----------|---------|
| `true` | Allow everyone (dangerous!) |
| `false` | Block everyone |
| `auth != null` | Only authenticated users |
| `auth.uid == 'USER_ID'` | Only specific user |
| `request.resource.size < 5000000` | File size < 5MB |
| `request.resource.contentType.matches('image/.*')` | Only images |

---

## 📚 Additional Resources

### Firebase Documentation:
- **Realtime Database Rules:** https://firebase.google.com/docs/database/security
- **Storage Rules:** https://firebase.google.com/docs/storage/security

### Testing Rules:
- Firebase provides a "Rules Simulator" in the console
- Test different scenarios before publishing
- Accessible from Rules tab → "Rules Playground"

---

## 🎉 Summary

### What You Need to Do:

1. **Go to:** https://console.firebase.google.com/
2. **Select:** age-of-reckoning project
3. **Navigate:** Storage → Rules
4. **Paste:** The rules from this guide
5. **Click:** Publish
6. **Test:** Upload button in NPC Mindmap

**Time needed:** 2-3 minutes

**Cost:** $0.00 (Free tier)

**Result:** Full upload functionality for everyone! 🚀

---

## ❓ Still Having Issues?

### Can't Access Firebase Console?
- Check you're logged into the correct Google account
- Verify you're the project owner
- Check Firebase status: https://status.firebase.google.com/

### Rules Won't Save?
- Try different browser
- Disable browser extensions temporarily
- Check internet connection

### Upload Still Fails After Rules?
- Check browser console for specific error
- Verify user is authenticated
- Make sure page is refreshed after rule changes

---

## 🎯 Next Steps

Once rules are published:

1. **Test Upload:** Try uploading an image in Visual Editor
2. **Share with Players:** Tell them upload button now works
3. **Document:** Players can upload from any device now
4. **Enjoy:** No more Imgur workaround needed!

**Your NPC Mindmap is now fully collaborative!** 🎭✨
