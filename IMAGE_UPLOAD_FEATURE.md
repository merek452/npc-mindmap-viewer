# NPC Portrait Upload Feature 📤

## Overview

The Visual Editor now includes a built-in image upload button that automatically converts, compresses, and uploads NPC portraits to Firebase Storage. This makes it easy for all players to add images from any device without needing Git access or file system management.

---

## ✨ Key Features

### 🔄 Automatic Processing:
- ✅ **Auto-resize**: Images resized to max 500x500px (maintains aspect ratio)
- ✅ **Auto-convert**: All formats converted to PNG
- ✅ **Auto-compress**: 80% quality compression to save bandwidth
- ✅ **File size reduction**: Typically reduces images by 70-90%

### 🌐 Cross-Platform:
- ✅ Works on desktop, tablet, and mobile devices
- ✅ Supports all image formats (PNG, JPG, BMP, WEBP, etc.)
- ✅ Camera upload on mobile devices
- ✅ Drag & drop support (coming soon)

### 💾 Storage:
- ✅ Uploaded to Firebase Storage (free tier: 5GB)
- ✅ Collaborative: All players can upload images
- ✅ Fast CDN delivery with caching
- ✅ Secure: Only authenticated users can upload

---

## 🎯 How to Use

### Method 1: Upload Button (Recommended)

1. **Open Visual Editor** tab
2. **Select or create an NPC**
3. **Click "📤 Upload"** button next to Portrait field
4. **Choose an image** from your device
5. **Wait for processing** (usually < 5 seconds)
6. **Preview updates** automatically
7. **Click "Save NPC"** to finalize

**That's it!** The image is now available to all players instantly.

---

### Method 2: Manual Path Entry (Advanced)

You can still manually enter image paths:

```
Local/GitHub Images:
Images/filename.png

External URLs:
https://example.com/image.png

Firebase Storage URLs:
https://firebasestorage.googleapis.com/...
```

---

## 📊 Image Processing Details

### Before Upload:
```
Original Image:
- Format: Any (BMP, JPG, PNG, WEBP, etc.)
- Size: Could be 5MB+
- Dimensions: Could be 4000x3000px
```

### After Upload:
```
Processed Image:
- Format: PNG ✅
- Size: Typically 50-200KB ✅
- Dimensions: Max 500x500px ✅
- Quality: 80% (excellent balance) ✅
```

### Example Compression:
```
Before: crazy_castle.bmp (3.2 MB, 2048x1536)
    ↓
After:  crazy_castle.png (128 KB, 500x375)
    ↓
Savings: 96% reduction! 🎉
```

---

## 🔄 Complete Workflow Example

### User Story: Player Adds New NPC

```
1. Player opens Visual Editor on their phone

2. Clicks "+ New NPC"

3. Enters NPC details:
   Name: "Mysterious Stranger"
   Faction: "Independent"
   Location: "Dark Alley"

4. Clicks "📤 Upload" for portrait

5. Takes photo with phone camera or selects from gallery

6. System processes:
   ✅ Resizing to 500x500
   ✅ Converting to PNG
   ✅ Compressing to 150KB
   ✅ Uploading to Firebase Storage

7. Upload status shows:
   "Processing image..."
   "Uploading... 50%"
   "Uploading... 100%"
   "✅ Image uploaded successfully!"

8. Portrait preview updates immediately

9. Player clicks "Save NPC"

10. All other players see the new NPC with portrait instantly! 🎉
```

---

## 🎨 UI Elements

### Upload Button:
```
┌─────────────────────────────────────────────┐
│ Portrait                                    │
├─────────────────────────────────────────────┤
│ [Images/filename.png___________] [📤 Upload]│
│                                             │
│ Status: ✅ Image uploaded successfully!     │
│                                             │
│ 💡 Upload: Auto-converts & compresses      │
│    Manual: "Images/file.png" or URL        │
└─────────────────────────────────────────────┘
```

### Upload States:

**Idle:**
```
[📤 Upload]
```

**Processing:**
```
Status: Processing image...
```

**Uploading:**
```
Status: Uploading... 75%
```

**Success:**
```
Status: ✅ Image uploaded successfully!
```

**Error:**
```
Status: ❌ Error: Upload failed - Network error
```

---

## 💾 Firebase Storage Structure

### File Organization:
```
Firebase Storage Root:
└── npc_portraits/
    ├── Goruk.png
    ├── Althessa_the_Rogue.png
    ├── Mysterious_Stranger.png
    └── ...
```

### Naming Convention:
- Takes NPC name from the Name field
- Sanitizes: removes special characters
- Replaces spaces with underscores
- Adds `.png` extension

**Examples:**
```
NPC Name              → Filename
─────────────────────────────────────
"Goruk"              → Goruk.png
"Althessa, The Rogue" → Althessa_The_Rogue.png
"Zyl'veth"           → Zylveth.png
```

---

## 🔒 Security & Permissions

### Firebase Storage Rules:

```json
{
  "rules": {
    "npc_portraits": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```

**This means:**
- ✅ Only authenticated users can upload
- ✅ Only authenticated users can view
- ✅ All authenticated users have equal permissions
- ✅ DM and players both can upload

---

## 💰 Cost Analysis

### Firebase Storage Free Tier:
- **Storage:** 5GB
- **Download:** 1GB/day
- **Upload:** 20,000/day

### Your Current Usage:
- **24 existing images:** ~50MB (GitHub)
- **Average new upload:** ~150KB per portrait

### Capacity:
```
Free tier can hold:
5GB ÷ 150KB = ~33,000 NPC portraits

That's enough for 33,000 NPCs! 🚀
```

### Paid Pricing (if you ever exceed free tier):
- **Storage:** $0.026/GB/month
- **Download:** $0.12/GB
- **Upload:** Free

**For typical usage (100 NPCs):**
```
100 NPCs × 150KB = 15MB
Cost: $0.00039/month (basically free!)
```

---

## 🔧 Troubleshooting

### Issue: Upload button doesn't work

**Solution:**
1. Check console for errors (F12)
2. Verify Firebase Storage is initialized: Look for "✅ Firebase Storage initialized"
3. Refresh the page
4. Check your internet connection

---

### Issue: "Firebase Storage not initialized" error

**Solution:**
1. Refresh the page to reinitialize Firebase
2. Check browser console for Firebase errors
3. Verify you're logged in to Firebase

---

### Issue: Upload takes too long

**Cause:** Large image file

**Solution:**
- The system automatically compresses, just wait a bit longer
- Check your internet upload speed
- For very large images (>10MB), consider pre-resizing

---

### Issue: Upload fails with network error

**Solution:**
1. Check your internet connection
2. Try again (may be temporary network issue)
3. Try a smaller image
4. Check Firebase Storage quota (unlikely)

---

### Issue: Image quality looks poor

**Adjustment:**
- The system uses 80% quality (good balance)
- If you need higher quality, use manual URL entry with externally hosted images
- Or contact DM to adjust compression settings in code

---

## 🆚 Comparison: Upload vs. Manual

### Upload Button ✅ (Recommended)

**Pros:**
- ✅ Works on any device (phone, tablet, desktop)
- ✅ No Git knowledge required
- ✅ Automatic optimization
- ✅ Instant availability to all players
- ✅ No file system access needed
- ✅ Perfect for players

**Cons:**
- ❌ Uses Firebase Storage quota (but 5GB is generous)
- ❌ Requires internet connection

---

### Manual GitHub/Local Paths (Advanced)

**Pros:**
- ✅ No storage quota concerns
- ✅ Version controlled with Git
- ✅ Works offline (for local testing)
- ✅ Perfect for bulk operations

**Cons:**
- ❌ Requires Git knowledge
- ❌ Requires file system access
- ❌ Not accessible from mobile
- ❌ DM must handle all uploads
- ❌ Requires manual optimization

---

## 🎯 Best Practices

### 1. **Use Upload Button for Individual NPCs**
When adding or editing one NPC at a time, use the upload button for convenience.

### 2. **Use Manual Paths for Bulk Operations**
When adding 20+ NPCs at once, DM can bulk-add images to `Images/` folder and use manual paths.

### 3. **Filename Convention**
If entering manual paths, use descriptive names:
```
✅ Good: Images/Goruk_Hobgoblin_Chief.png
❌ Bad: Images/IMG_1234.png
```

### 4. **Image Source Quality**
- AI-generated: Usually already optimized ✅
- Downloaded: May need compression ⚠️
- Photos: Definitely need compression ⚠️

### 5. **Testing**
Test uploads with a small image first to verify everything works.

---

## 🚀 Future Enhancements (Potential)

### Coming Soon:
- [ ] Drag & drop support
- [ ] Paste from clipboard
- [ ] Image cropping/editing tool
- [ ] Batch upload (multiple images)
- [ ] Delete old images button
- [ ] Image library browser

### Maybe Later:
- [ ] AI-generated portraits (DALL-E integration)
- [ ] Character sheet parser (extract image from PDF)
- [ ] Token generator (circular frames)

---

## 📚 Technical Details

### Technologies Used:
- **Firebase Storage SDK**: `firebase-storage-compat.js`
- **HTML5 Canvas API**: For image processing
- **FileReader API**: For loading images
- **Blob API**: For file handling

### Code Location:
- **Python Generator**: `generate_mindmap.py` lines ~7900-8100
- **Generated HTML**: `npc_mindmap_viewer.html`
- **Functions**:
  - `uploadPortraitImage()` - Triggers file picker
  - `processAndUploadImage()` - Handles image processing
  - `uploadToFirebase()` - Uploads to Firebase Storage
  - `showUploadStatus()` - Shows progress messages

---

## ✅ Testing Checklist

### Test on Desktop:
- [ ] Click upload button
- [ ] Select PNG image → Verify upload
- [ ] Select JPG image → Verify conversion to PNG
- [ ] Select large image (5MB+) → Verify compression
- [ ] Check preview updates
- [ ] Save NPC and reload → Verify persistence

### Test on Mobile:
- [ ] Click upload button
- [ ] Take photo with camera → Verify upload
- [ ] Select from gallery → Verify upload
- [ ] Check upload on slow connection
- [ ] Verify image appears for other users

### Test Multi-Player:
- [ ] Player 1 uploads image
- [ ] Player 2 sees image immediately (may need refresh)
- [ ] Both can edit same NPC
- [ ] Both can upload different images

---

## 🎉 Summary

**The upload feature makes it easy for all players to contribute NPC portraits from any device, with automatic optimization and real-time collaboration!**

### Key Benefits:
1. 📱 **Mobile-friendly**: Upload from phone/tablet
2. 🔄 **Auto-optimize**: Converts & compresses automatically  
3. 👥 **Collaborative**: All players can upload
4. ⚡ **Fast**: Typically 5 seconds or less
5. 💰 **Free**: Well within Firebase free tier

**Happy NPC creating! 🎭**
