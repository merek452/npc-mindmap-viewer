# New Issues Identified - Security & Scalability Audit

**Date:** 2026-02-05  
**Status:** Issues identified, no code changes made

---

## 🔴 **CRITICAL SECURITY ISSUES**

### 1. ❌ **No Campaign Isolation (All Users Share Data)**

**Severity:** CRITICAL - Privacy & Data Integrity Risk

**Problem:**
- `CAMPAIGN_ID` is hardcoded to `"genia"` in the HTML
- Everyone who visits the URL shares the same Firebase data
- No way to create separate campaigns
- Line: `generate_mindmap.py` line 1841

**Evidence:**
```javascript
const CAMPAIGN_ID = "genia";  // Hardcoded - everyone uses this!
```

**Impact:**
- ❌ Multiple D&D groups would interfere with each other
- ❌ No privacy between campaigns
- ❌ Anyone with the URL can access/edit your campaign
- ❌ Cannot host for multiple groups

**Possible Solutions:**
1. **URL-based Campaign ID**
   ```javascript
   // Use URL parameter: https://yoursite.com/?campaign=genia
   const urlParams = new URLSearchParams(window.location.search);
   const CAMPAIGN_ID = urlParams.get('campaign') || 'default';
   ```

2. **Campaign Selection Screen**
   - Prompt for campaign name on load
   - Store in localStorage
   - Allow switching between campaigns

3. **Authentication-based**
   - Each user creates account
   - Can create/join multiple campaigns
   - Proper authorization per campaign

---

### 2. ❌ **No Access Control (Anyone Can Edit)**

**Severity:** HIGH - Security Risk

**Problem:**
- Anyone with the URL can edit anything
- No DM-only features
- No read-only player mode
- Uses anonymous authentication (everyone has full access)

**Impact:**
- ❌ Players can edit NPCs (should be DM-only)
- ❌ Trolls/griefers could delete everything
- ❌ No way to restrict sensitive information
- ❌ Cannot share URL publicly

**Example Attack:**
```
1. Bad actor finds your GitHub Pages URL
2. Opens app, sees your campaign data
3. Deletes all NPCs, markers, inventory
4. Your campaign is ruined
```

**Possible Solutions:**
1. **Simple Access Code**
   ```javascript
   const CAMPAIGN_ACCESS_CODE = "dragon123";
   // Prompt on load, store in sessionStorage
   ```

2. **Firebase Security Rules**
   ```json
   {
     "rules": {
       "campaigns": {
         "$campaignId": {
           ".read": "auth != null",
           ".write": "auth != null && (
             root.child('campaigns/' + $campaignId + '/owners').child(auth.uid).exists() ||
             root.child('campaigns/' + $campaignId + '/editors').child(auth.uid).exists()
           )"
         }
       }
     }
   }
   ```

3. **Role-based Access**
   - DM role: Full edit access
   - Player role: Limited access (can edit inventory/maps, not NPCs)
   - Viewer role: Read-only

---

### 3. ⚠️ **XSS Vulnerability in Marker Names**

**Severity:** MEDIUM - Security Risk

**Problem:**
- Marker names are directly concatenated into `innerHTML` without escaping
- User-provided data could contain malicious script tags
- Lines: `generate_mindmap.py` lines 4434, 6183

**Evidence:**
```javascript
// VULNERABLE:
item.innerHTML = '... <strong>' + marker.name + '</strong> ...';
// If marker.name = '<img src=x onerror=alert(1)>', code executes!
```

**Impact:**
- ❌ Malicious marker name could execute JavaScript
- ❌ Could steal Firebase credentials
- ❌ Could delete all data
- ❌ Cross-site scripting attack vector

**Current Mitigation:**
- ✅ `escapeHtml()` function exists (line 9208)
- ❌ But NOT used for marker names

**Fix Required:**
```javascript
// SAFE:
item.innerHTML = '... <strong>' + escapeHtml(marker.name) + '</strong> ...';
```

**Also check:** NPC names, item names, notes, annotations

---

### 4. ⚠️ **Exposed Firebase API Keys**

**Severity:** LOW - Rate Limiting Risk

**Problem:**
- Firebase config with API keys is in public HTML
- Anyone can see and use your Firebase project
- Could cause rate limiting or quota exhaustion

**Evidence:**
```javascript
const FIREBASE_CONFIG = {
    apiKey: "AIzaSyA-S3yjlJmzvszYw9cl_39TRMvvUrrUeas",  // PUBLIC
    databaseURL: "https://age-of-reckoning-default-rtdb.firebaseio.com",
    // ...
};
```

**Impact:**
- ⚠️ Attacker could spam your Firebase (exhaust free tier)
- ⚠️ Could read your campaign data (if they know campaign ID)
- ⚠️ Rate limiting could affect legitimate users

**Note:** This is somewhat acceptable for Firebase client SDKs
- Firebase API keys are meant to be public
- Security is enforced by Firebase Security Rules
- BUT you need proper rules (see Issue #2)

**Mitigation:**
- ✅ Implement Firebase Security Rules
- ✅ Set up Firebase App Check (bot protection)
- ✅ Monitor Firebase usage quotas

---

## 🟠 **HIGH PRIORITY ISSUES**

### 5. ⚠️ **No Data Validation**

**Severity:** MEDIUM - Data Integrity Risk

**Problem:**
- No validation on user input before saving to Firebase
- No limits on text length, array sizes
- Could save invalid/malformed data

**Examples:**
- Marker name: 10,000 characters → breaks UI
- Inventory: 1,000,000 items → crashes browser
- Notes: HTML/scripts → XSS or rendering issues

**Impact:**
- ⚠️ Malicious user could save huge data → crash everyone
- ⚠️ Accidental paste of large text → breaks app
- ⚠️ Invalid data types → JavaScript errors

**Recommended Validation:**
```javascript
function validateMarker(marker) {
    if (!marker.name || marker.name.length > 200) {
        throw new Error('Marker name must be 1-200 characters');
    }
    if (!marker.id || typeof marker.id !== 'number') {
        throw new Error('Invalid marker ID');
    }
    // ... more validation
}
```

---

### 6. ⚠️ **No Data Size Limits**

**Severity:** MEDIUM - Performance & Cost Risk

**Problem:**
- No limits on number of NPCs, markers, items
- Could exceed Firebase limits or degrade performance
- No pagination or lazy loading

**Firebase Limits:**
- Max write: 256 MB per write
- Max document: 1 MB (Firestore) / 16 MB (Realtime Database node)
- Free tier: 10 GB total storage, 1 GB/day download

**Potential Issues:**
- Adding 10,000 markers → app becomes unusable
- Very large NPC notes → slow to load
- Huge inventory → transaction becomes expensive

**Recommendations:**
1. **Set reasonable limits**
   - Max 500 markers per map
   - Max 1000 items in bag
   - Max 100 NPCs
   - Max 5000 chars per note

2. **Add pagination**
   - Load NPCs 20 at a time
   - Virtual scrolling for large lists

3. **Warn users**
   - "You have 450/500 markers. Consider archiving old ones."

---

## 🟡 **MEDIUM PRIORITY ISSUES**

### 7. ⚠️ **No Offline Support**

**Severity:** LOW - UX Issue

**Problem:**
- App requires constant internet connection
- No offline caching of data
- Network loss = app stops working

**Current Behavior:**
- ✅ Falls back to localStorage on save failure
- ❌ But doesn't load from localStorage on startup
- ❌ No service worker / PWA support

**Impact:**
- Users in poor connectivity areas have bad experience
- DM can't use app without internet

**Possible Enhancement:**
- Implement service worker for offline caching
- Store last known good state in localStorage
- Show "Offline Mode" indicator

---

### 8. ⚠️ **No Backup/Export Mechanism**

**Severity:** MEDIUM - Data Loss Risk

**Problem:**
- Users cannot backup their campaign data
- No export to JSON
- If Firebase data is lost/corrupted, no recovery

**Current State:**
- ✅ NPC export exists
- ❌ No inventory export
- ❌ No map markers export
- ❌ No full campaign export

**Recommendation:**
```javascript
function exportCampaign() {
    const data = {
        npcs: editorNPCData,
        inventory: inventoryData,
        mapMarkers: markers,
        worldMapMarkers: MapState.getValue('markers'),
        timestamp: new Date().toISOString()
    };
    downloadJSON(data, `campaign-${CAMPAIGN_ID}-backup.json`);
}
```

---

### 9. ⚠️ **No Browser Compatibility Checks**

**Severity:** LOW - UX Issue

**Problem:**
- No checks for required browser features
- Could fail silently on old browsers
- No graceful degradation

**Required Features:**
- localStorage
- Firebase SDK support
- Canvas API (for maps)
- ES6 features (arrow functions, template literals, etc.)

**Recommendation:**
```javascript
if (!window.localStorage) {
    alert('Your browser is too old. Please update your browser.');
}
```

---

### 10. ⚠️ **No Mobile Optimization**

**Severity:** MEDIUM - UX Issue

**Problem:**
- Interface designed for desktop
- Touch interactions may not work well
- Small screens may have usability issues

**Observed Issues:**
- Map dragging on mobile
- Small buttons/touch targets
- Text input on mobile keyboards
- Viewport meta tag exists but needs testing

**Current Mitigation:**
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
select, input, textarea { font-size: 16px; /* Prevents zoom on focus */ }
```

**Needs Testing:** Actual mobile device testing

---

## 📊 **SUMMARY**

### Critical (Must Fix for Public Use):
1. ❌ Campaign Isolation
2. ❌ Access Control
3. ⚠️ XSS in Marker Names

### High Priority (Should Fix Soon):
4. ⚠️ Exposed API Keys (mitigated by rules)
5. ⚠️ No Data Validation
6. ⚠️ No Size Limits

### Medium Priority (Nice to Have):
7. ⚠️ No Offline Support
8. ⚠️ No Backup Export
9. ⚠️ Browser Compatibility
10. ⚠️ Mobile Optimization

---

## 🎯 **RECOMMENDATIONS**

### For Private Use (Your D&D Group Only):
**Current State: ✅ ACCEPTABLE**
- Your group trusts each other (no access control needed)
- One campaign (isolation not needed)
- Desktop usage (mobile not critical)

**Minimal Fixes:**
1. Fix XSS vulnerability (escape marker names)
2. Add data validation (prevent accidents)
3. Add export/backup feature

### For Public/Multiple Campaigns:
**Current State: ❌ NOT READY**

**Required Fixes:**
1. Implement campaign isolation (URL-based or selection screen)
2. Add access control (campaign codes or authentication)
3. Fix XSS vulnerability
4. Implement Firebase Security Rules
5. Add data validation & limits

**Estimated Effort:** 2-4 days of development

---

## 💡 **IMMEDIATE ACTION ITEMS**

### Quick Wins (< 1 hour):
1. Fix XSS: Use `escapeHtml()` for all user-provided strings in innerHTML
2. Add data validation: Max string lengths, array sizes
3. Add export button: Let users backup their data

### Medium Effort (2-4 hours):
4. Campaign isolation: URL parameter or localStorage selection
5. Firebase Security Rules: Restrict access properly
6. Access code: Simple password protection

### Larger Projects (1-2 days):
7. Role-based access: DM vs Player permissions
8. Proper authentication: User accounts instead of anonymous
9. Mobile optimization: Touch interactions, responsive UI

---

## 🧪 **HOW TO TEST THESE ISSUES**

### Test XSS Vulnerability:
```
1. Add a map marker with name: <img src=x onerror=alert('XSS')>
2. Refresh the page
3. If alert appears: VULNERABLE ❌
4. If marker name shows as text: SAFE ✅
```

### Test Campaign Isolation:
```
1. Share your GitHub Pages URL with a friend
2. Have them open it
3. They can see/edit your campaign data: NO ISOLATION ❌
```

### Test Data Limits:
```
1. Try adding 10,000 characters to a marker note
2. Try adding 1,000 items to inventory
3. Check if app slows down or crashes
```

---

**Conclusion:** The app is **production-ready for trusted private groups** but needs security hardening for public/multi-campaign use.
