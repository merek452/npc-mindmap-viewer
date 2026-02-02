# Firebase Security Guide

## ⚠️ About the "Public API Key" Warning

**IMPORTANT:** The Firebase API key you received a warning about is **meant to be public**. This is not like traditional API keys!

### Why Firebase API Keys Are Public

Firebase API keys are **not secret** because:
1. They're used in client-side JavaScript (always visible in browser)
2. They only identify your Firebase project (like a project ID)
3. **Real security comes from Firebase Security Rules**, not hiding the key

From Firebase Documentation:
> "Unlike how API keys are typically used, API keys for Firebase services are not used to control access to backend resources... That can only be done with Firebase Security Rules."

## 🔒 Real Security: Firebase Security Rules

Your database is secured by the rules in `database.rules.json`. These rules control who can read/write your data.

### Current Setup (Open Access)

```json
{
  "rules": {
    "campaigns": {
      "$campaignId": {
        ".read": true,
        ".write": true
      }
    }
  }
}
```

This allows **anyone** with your Firebase URL to read/write data. This is fine for a private D&D game, but you may want to add protection.

## 🛡️ Security Options

### Option 1: Access Code Protection (Recommended for D&D Games)

Add an access code to your app:

1. In `generate_mindmap.py`, find:
```javascript
const CAMPAIGN_ACCESS_CODE = "";
```

2. Change to:
```javascript
const CAMPAIGN_ACCESS_CODE = "your-secret-code-here";
```

3. Regenerate: `python generate_mindmap.py`

4. Share the code with your players. The app will prompt for it on first visit.

### Option 2: Domain Restrictions

Restrict your Firebase API key to only work from specific domains:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Find your API key: `AIzaSyA-S3yjlJmzvszYw9cl_39TRMvvUrrUeas`
3. Click "Edit API key"
4. Under "Application restrictions", select "HTTP referrers"
5. Add your allowed domains:
   - `https://merek452.github.io/*` (GitHub Pages)
   - `http://localhost/*` (local testing)
   - `https://yourdomain.com/*` (custom domain)

### Option 3: Firebase Authentication (Most Secure)

Require users to sign in:

1. Enable Firebase Authentication in your Firebase Console
2. Update security rules to require authentication:

```json
{
  "rules": {
    "campaigns": {
      "$campaignId": {
        ".read": "auth != null",
        ".write": "auth != null"
      }
    }
  }
}
```

3. Add sign-in to your app (requires code changes)

## 📋 Applying Security Rules

### Method 1: Firebase Console (Easiest)

1. Go to: https://console.firebase.google.com/project/age-of-reckoning/database/age-of-reckoning-default-rtdb/rules
2. Copy the contents of `database.rules.json`
3. Paste into the Rules tab
4. Click "Publish"

### Method 2: Firebase CLI

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in your project
firebase init database

# Deploy rules
firebase deploy --only database
```

## 🔍 Monitoring Access

View who's accessing your database:

1. Go to: https://console.firebase.google.com/project/age-of-reckoning/database/age-of-reckoning-default-rtdb/usage
2. Monitor read/write operations
3. Check for suspicious activity

## ❓ FAQ

**Q: Should I regenerate my API key?**
A: No need! The key itself isn't secret. Just apply proper security rules.

**Q: Can I hide the API key?**
A: No. It's in client-side code, always visible in the browser. That's by design.

**Q: Is my data secure?**
A: Yes, if you have proper security rules. The API key alone doesn't grant access.

**Q: What about GitHub's warning?**
A: GitHub's scanner flags all API keys, but Firebase keys are safe to commit. You can:
- Dismiss the alert (it's a false positive for Firebase)
- Or use the `.gitignore` approach below (cosmetic only)

## 📝 Optional: Hide Key from Git (Cosmetic)

If you want to stop GitHub's warnings (though it doesn't improve security):

1. Create `.env` file (add to `.gitignore`):
```
FIREBASE_API_KEY=AIzaSyA-S3yjlJmzvszYw9cl_39TRMvvUrrUeas
FIREBASE_PROJECT_ID=age-of-reckoning
```

2. Update code to load from environment variables
3. Note: The key will still be visible in the browser!

## ✅ Recommended Setup for Your D&D Game

1. ✅ Use the access code feature (simple password protection)
2. ✅ Apply domain restrictions to your API key
3. ✅ Monitor usage in Firebase Console
4. ✅ Keep security rules at campaign level
5. ✅ Don't worry about the "leaked secret" warning

**Your players' data is safe as long as you have security rules configured!**
