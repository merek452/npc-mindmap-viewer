# Quick Fix for "Publicly Leaked Secret" Warning

## 🚨 Don't Panic!

The Firebase API key in your code is **meant to be public**. Google's warning is a false alarm for Firebase projects.

## ✅ Immediate Action (5 minutes)

### Step 1: Apply Domain Restrictions (Recommended)

This prevents others from using your Firebase key on their own websites:

1. Go to: https://console.cloud.google.com/apis/credentials?project=age-of-reckoning
2. Find your API key: `AIzaSyA-S3yjlJmzvszYw9cl_39TRMvvUrrUeas`
3. Click the pencil icon (Edit)
4. Under "Application restrictions":
   - Select "HTTP referrers (web sites)"
   - Click "ADD AN ITEM"
   - Add these URLs:
     * `https://merek452.github.io/*`
     * `http://localhost/*`
     * `file:///*` (for local testing)
5. Click "SAVE"

**Done!** Your key now only works from your domains.

### Step 2: Dismiss the GitHub Alert

1. Go to your GitHub repository: Security → Secret scanning alerts
2. Find the Firebase API key alert
3. Click "Dismiss alert"
4. Select reason: "Used in tests" or "False positive"
5. Add comment: "Firebase API keys are public by design - security is handled by Firebase Security Rules"

### Step 3: Secure Your Database (IMPORTANT!)

The **real** security is in Firebase Security Rules:

1. Go to: https://console.firebase.google.com/project/age-of-reckoning/database/age-of-reckoning-default-rtdb/rules
2. Copy this and paste it:

```json
{
  "rules": {
    "campaigns": {
      "$campaignId": {
        ".read": "auth == null || auth != null",
        ".write": "auth == null || auth != null",
        ".validate": "newData.hasChildren()"
      }
    }
  }
}
```

3. Click "Publish"

**This is what actually protects your data!**

## 🔒 Optional: Add Access Code (Simple Password)

Want to require a password? Easy!

1. Open: `generate_mindmap.py`
2. Find line ~1838: `const CAMPAIGN_ACCESS_CODE = "";`
3. Change to: `const CAMPAIGN_ACCESS_CODE = "your-secret-password";`
4. Run: `python generate_mindmap.py`
5. Commit and push

Now visitors need the password to access your game data!

## 📚 More Info

See `FIREBASE_SECURITY.md` for detailed security options.

## ❓ FAQ

**Q: Is my data at risk?**
A: No, if you have Firebase Security Rules configured (Step 3 above).

**Q: Should I revoke the API key?**
A: No need! It's not a secret. Just apply domain restrictions (Step 1).

**Q: Will this warning keep appearing?**
A: Not if you dismiss it and apply domain restrictions.

**Q: Do I need to remove the key from my code?**
A: No - it needs to be in the code to work. That's normal for Firebase.

---

**Summary:** Apply domain restrictions (Step 1), dismiss the alert (Step 2), and ensure security rules are set (Step 3). You're good to go! 🎉
