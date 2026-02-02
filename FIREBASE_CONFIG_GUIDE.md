# Firebase Configuration Guide

## 📍 Where Configuration is Set Up

The Firebase configuration is embedded in the generated HTML file (`npc_mindmap_viewer.html`). It's defined in the Python script at:

**File:** `generate_mindmap.py`  
**Lines:** 1633-1647

```javascript
const FIREBASE_CONFIG = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    databaseURL: "https://YOUR_PROJECT-default-rtdb.firebaseio.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
};

const CAMPAIGN_ID = "genia";
const CAMPAIGN_ACCESS_CODE = "";
```

## 🎯 Optimal Configuration Strategy

### Option 1: Single Firebase Project, Multiple Campaigns (Recommended)

**Best for:** Multiple D&D campaigns, shared resources

- **One Firebase project** for all your campaigns
- **Different `CAMPAIGN_ID`** for each campaign (e.g., "genia", "waterdeep", "ravenloft")
- **Same `FIREBASE_CONFIG`** for all campaigns
- **Data isolation:** Each campaign's data is stored separately under `campaigns/{campaignId}/`

**Advantages:**
- ✅ Single Firebase project to manage
- ✅ Shared free tier quota across campaigns
- ✅ Easy to add new campaigns (just change `CAMPAIGN_ID`)
- ✅ All campaigns in one place

**Setup:**
1. Create one Firebase project
2. Get the Firebase config once
3. For each campaign, change only `CAMPAIGN_ID` in the generated HTML
4. Share the appropriate HTML file with each campaign's players

### Option 2: One Firebase Project Per Campaign

**Best for:** Separate campaigns with different DMs, maximum isolation

- **Separate Firebase project** for each campaign
- **Different `FIREBASE_CONFIG`** for each campaign
- **Same or different `CAMPAIGN_ID`** (can use "main" or campaign name)

**Advantages:**
- ✅ Complete data isolation
- ✅ Separate billing/quota per campaign
- ✅ Different security rules per campaign

**Disadvantages:**
- ❌ More Firebase projects to manage
- ❌ Need to get config for each project

## 📤 What Needs to be Shared

### For Players (End Users)

**Share ONLY:**
- ✅ The `npc_mindmap_viewer.html` file (with Firebase config already embedded)
- ✅ The `Images/` folder (for NPC portraits and world map)

**Do NOT share:**
- ❌ `generate_mindmap.py` (source code, not needed)
- ❌ `npc_relationships.json` (source data, not needed)
- ❌ Firebase console access (security risk)

### For Other DMs/Developers

**Share:**
- ✅ `generate_mindmap.py` (to generate their own HTML)
- ✅ `npc_relationships.json` (if they want to modify NPCs)
- ✅ `items.json` (if they want to modify items)
- ✅ Firebase config values (if using shared project)

## 🔒 Security Considerations

### Current Setup (Simple)

The current configuration uses **open read/write** rules:
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

**This means:**
- ✅ Anyone with the HTML file can read/write data
- ✅ No authentication required
- ⚠️ Anyone who finds the Firebase config can access your data
- ⚠️ Not suitable for sensitive data

**Is this safe for D&D campaigns?**
- **Yes, for most use cases** - D&D inventory/map data is not sensitive
- The Firebase config is embedded in the HTML, so anyone with the file can access it
- This is fine for a shared campaign tool

### Enhanced Security (Optional)

If you want password protection:

1. **Add access code check:**
   - Set `CAMPAIGN_ACCESS_CODE = "your-secret-code"`
   - Modify Firebase rules to check access code
   - Add UI prompt for access code on page load

2. **Use Firebase Authentication:**
   - Require users to sign in with Google/Email
   - Update rules to check `auth != null`
   - More secure but requires user accounts

## 🚀 Recommended Setup Workflow

### Step 1: Create Firebase Project
1. Go to https://console.firebase.google.com
2. Create new project: "D&D Campaign Manager" (or similar)
3. Enable Realtime Database
4. Get your Firebase config

### Step 2: Configure Python Script (Optional)
You can hardcode your Firebase config in `generate_mindmap.py` so it's automatically included:

```python
# At the top of generate_html_viewer() method
FIREBASE_CONFIG = {
    'apiKey': 'YOUR_API_KEY',
    'authDomain': 'YOUR_PROJECT.firebaseapp.com',
    # ... etc
}
CAMPAIGN_ID = 'genia'
```

Then in the HTML template, use:
```python
const FIREBASE_CONFIG = {{
    apiKey: "{FIREBASE_CONFIG['apiKey']}",
    # ... etc
}};
```

### Step 3: Generate HTML
```bash
python generate_mindmap.py
```

### Step 4: Share with Players
- Upload `npc_mindmap_viewer.html` to GitHub Pages (or host elsewhere)
- Share the URL with players
- They can also download and use locally (will sync if online)

## 📊 Data Structure in Firebase

Your data is stored like this:

```
campaigns/
  └── genia/
      ├── inventory_data/
      │   ├── partyGold: 1500
      │   ├── players: [...]
      │   └── bagOfHolding: [...]
      ├── mapMarkers: [...]
      └── mapAnnotations: [...]
```

Each campaign is completely isolated by `CAMPAIGN_ID`.

## 🔄 Updating Configuration

### To Change Campaign ID:
1. Edit `CAMPAIGN_ID` in `generate_mindmap.py` (line 1644)
2. Regenerate HTML: `python generate_mindmap.py`
3. Share new HTML with players

### To Change Firebase Project:
1. Get new Firebase config from Firebase Console
2. Update `FIREBASE_CONFIG` in `generate_mindmap.py` (lines 1633-1641)
3. Regenerate HTML: `python generate_mindmap.py`
4. **Note:** Changing projects creates a new database - old data won't transfer automatically

## 💡 Best Practices

1. **Backup your data:**
   - Export from Firebase Console periodically
   - Keep local copies of `npc_relationships.json`

2. **Version control:**
   - Don't commit Firebase config to public GitHub repos
   - Use environment variables or config files (not in repo)

3. **Campaign isolation:**
   - Use unique `CAMPAIGN_ID` for each campaign
   - Prevents data mixing between campaigns

4. **Testing:**
   - Test with one browser window first
   - Open two windows to verify real-time sync works
   - Check Firebase Console to see data being written

## ❓ FAQ

**Q: Can I use the same Firebase project for multiple campaigns?**  
A: Yes! Just use different `CAMPAIGN_ID` values. Each campaign's data is stored separately.

**Q: What if I want to keep campaigns completely separate?**  
A: Create separate Firebase projects for each campaign.

**Q: Can players see other campaigns' data?**  
A: No, as long as they use the HTML file with the correct `CAMPAIGN_ID`. Data is isolated by campaign ID.

**Q: What happens if I change the Firebase config?**  
A: The app will try to connect to the new Firebase project. Old data won't be accessible unless you migrate it.

**Q: Can I use this offline?**  
A: Yes, but changes won't sync until you're online. The app falls back to localStorage when Firebase isn't available.
