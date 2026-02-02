# Firebase Setup Guide

## Step 1: Get Your Firebase Configuration

1. Go to https://console.firebase.google.com
2. Select your project
3. Click the gear icon ⚙️ next to "Project Overview"
4. Select "Project settings"
5. Scroll down to "Your apps" section
6. Click the `</>` (Web) icon to add a web app
7. Register your app (name it "NPC Mind Map Viewer")
8. Copy the `firebaseConfig` object - it looks like this:

```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "your-project.firebaseapp.com",
  databaseURL: "https://your-project-default-rtdb.firebaseio.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

## Step 2: Enable Realtime Database

1. In Firebase Console, go to "Build" → "Realtime Database"
2. Click "Create Database"
3. Choose your region (closest to you)
4. Start in **test mode** (we'll add security rules later)
5. Click "Enable"

## Step 3: Set Up Security Rules

1. In Realtime Database, go to "Rules" tab
2. Replace the rules with:

```json
{
  "rules": {
    "campaigns": {
      "$campaignId": {
        ".read": "auth != null || query.orderByChild('accessCode').equalTo($accessCode).exists()",
        ".write": "auth != null || newData.child('accessCode').val() == $accessCode"
      }
    }
  }
}
```

**OR for simple password protection (easier):**

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

⚠️ **Note:** The simple rules allow anyone with the URL to read/write. For production, use proper authentication.

## Step 4: Get Your Config Values

You'll need to provide these values when running the setup:
- `apiKey`
- `authDomain`
- `databaseURL`
- `projectId`

## Step 5: Set Campaign Access Code (Optional)

You can set a simple password/access code for your campaign. This will be stored in the code (not super secure, but good enough for a D&D campaign).
