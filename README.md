# NPC Relationship Mind Map - Collaborative D&D Campaign Tracker

A **real-time collaborative** web application for managing D&D campaign NPCs, relationships, inventory, and world maps. Built for multi-player groups with **transaction-safe concurrent editing** and **Firebase real-time synchronization**.

🎮 **Live Demo:** [Your GitHub Pages URL]

---

## 🌟 **Key Features**

### 🤝 **Real-Time Multi-Player Collaboration**
- **Concurrent editing** - Multiple players can edit simultaneously without data loss
- **Transaction-based saves** - Intelligent merge system prevents "last-write-wins" conflicts
- **Real-time sync** - See other players' changes instantly
- **Save notifications** - Visual feedback for save status and failures
- **Automatic retry** - Network failures retry with exponential backoff

### 👥 **NPC Management**
- **Interactive mind map** - Visual relationship graph with zoom, pan, and physics simulation
- **NPC card view** - Browse NPCs with filters (faction, status, location, tags)
- **Visual editor** - Add, edit, and delete NPCs with real-time sync
- **Portrait uploads** - Upload and crop NPC portraits to Firebase Storage
- **Relationship tracking** - Define allies, enemies, family, and custom relationships
- **Spoiler mode** - Hide sensitive information from players

### 🗺️ **World Map System**
- **Interactive world map** - Pan, zoom, and annotate your campaign world
- **Markers** - Add location markers with categories (cities, dungeons, landmarks)
- **Annotations** - Draw paths, regions, and notes directly on the map
- **Mini-map** - Additional detailed area map
- **Transaction-safe** - Concurrent map editing without data loss

### 🎒 **Party Inventory Tracker**
- **Party gold** - Track shared party funds
- **Player inventories** - Individual item tracking for each party member
- **Bag of Holding** - Shared party storage
- **D&D 5e item database** - 900+ pre-loaded items with autocomplete
- **Drag-and-drop** - Move items between containers
- **Auto-stacking** - Stackable items combine automatically
- **Transaction-safe** - No data loss when multiple players edit simultaneously

### 🔧 **Technical Features**
- **Firebase integration** - Real-time database and cloud storage
- **Offline fallback** - localStorage backup when Firebase unavailable
- **Responsive design** - Works on desktop, tablet, and mobile
- **No backend required** - Pure client-side application
- **Automatic image optimization** - Portraits resized and compressed (500x500px, 80% quality)
- **Debounced saves** - Efficient Firebase usage (500ms debounce)
- **Anonymous authentication** - Frictionless access with Firebase Auth

---

## 🚀 **Quick Start**

### **For Players:**

1. **Open the live app:** Visit your GitHub Pages URL
2. **Start using immediately** - No login required (anonymous authentication)
3. **Bookmark the URL** - All your changes sync in real-time

### **For DMs:**

1. **Fork this repository** to your GitHub account
2. **Set up Firebase:**
   - Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
   - Enable Realtime Database, Storage, and Anonymous Authentication
   - Copy your config to `generate_mindmap.py` (line 1830)
3. **Add your data:**
   - Edit `npc_relationships.json` with your NPCs
   - Add world map SVG to parent directory as `Gienia World Map.svg`
4. **Generate HTML:**
   ```bash
   python generate_mindmap.py
   ```
5. **Deploy:**
   - Push to GitHub (automatically deploys to GitHub Pages)
   - Or use any static hosting service

---

## 📋 **Requirements**

### **For Users (Players/DMs):**
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for real-time sync (offline mode with localStorage fallback)

### **For Development (DMs only):**
- Python 3.6+ (to regenerate HTML from JSON)
- Firebase project (free tier is sufficient)
- Git (for version control)

---

## 🎮 **How to Use**

### **NPC Cards Tab**
- **Filter** - By faction, status, location, or search by name
- **Group** - Organize by faction, location, or status
- **Sort** - Alphabetically or by various criteria
- **Click cards** - Highlight corresponding nodes in mind map
- **Real-time updates** - See new NPCs instantly when others add them

### **Mind Map Tab**
- **Zoom** - Mouse wheel or pinch gesture
- **Pan** - Click and drag
- **Physics** - Toggle node physics simulation
- **Relationships** - Hover over edges to see relationship types
- **Node colors** - Color-coded by faction
- **Click nodes** - Highlight corresponding NPC cards

### **World Map Tab**
- **Pan & Zoom** - Navigate your campaign world
- **Add Markers** - Click to place location markers (cities, dungeons, etc.)
- **Draw Annotations** - Sketch paths, regions, or notes
- **Edit Markers** - Click markers to edit name, category, and notes
- **Delete** - Right-click to delete markers or annotations
- **Auto-save** - Changes save automatically (debounced)

### **Inventory Tab**
- **Party Gold** - Track shared funds at the top
- **Player Cards** - Individual inventory for each party member
- **Bag of Holding** - Shared party storage
- **Add Items** - Search from 900+ D&D 5e items
- **Drag & Drop** - Move items between containers
- **Delete** - Click × to remove items
- **Auto-sync** - All changes sync in real-time

### **Visual Editor Tab**
- **NPC List** - Browse and select NPCs to edit
- **Add NPC** - Create new characters
- **Edit Properties** - Name, faction, location, status, tags, notes
- **Upload Portrait** - Drag-and-drop or click to upload images
- **Relationships** - Add/edit connections to other NPCs
- **Delete** - Remove NPCs (with confirmation)
- **Export JSON** - Backup your data

---

## 🏗️ **Architecture**

### **Tech Stack:**
- **Frontend:** Pure JavaScript (ES6+), HTML5, CSS3
- **Database:** Firebase Realtime Database
- **Storage:** Firebase Cloud Storage (for NPC portraits)
- **Auth:** Firebase Anonymous Authentication
- **Hosting:** GitHub Pages (or any static host)
- **Build:** Python script generates single HTML file

### **Data Storage:**
```
Firebase Realtime Database
└── campaigns/
    └── {CAMPAIGN_ID}/
        ├── npc_data          (NPCs with relationships)
        ├── inventory_data    (Party inventory)
        ├── mapMarkers        (Mini-map markers)
        ├── mapAnnotations    (Mini-map drawings)
        ├── worldMapMarkers   (World map markers)
        └── worldMapAnnotations (World map drawings)

Firebase Storage
└── npc_portraits/
    └── {NPC_NAME}.png    (Uploaded portraits)
```

### **Concurrency Control:**
- **Firebase Transactions** - Used for inventory and maps to prevent data loss
- **Intelligent Merging** - Items merged by unique ID, players merged by name
- **Debouncing** - 500ms delay prevents excessive Firebase writes
- **Retry Mechanism** - 3 attempts with exponential backoff (1s, 3s, 5s)
- **User Notifications** - Visual feedback for all save operations

---

## 🔒 **Security & Privacy**

### **Current Implementation (Private Use):**
- ✅ **Anonymous authentication** - No user accounts needed
- ✅ **Campaign ID** - Hardcoded to "genia" (single campaign)
- ✅ **Firebase Security Rules** - Allow authenticated read/write
- ✅ **XSS Protection** - `escapeHtml()` function for user input (partially implemented)

### **For Public/Multi-Campaign Use:**
**⚠️ Additional setup required:**
- Campaign isolation (URL-based or selection screen)
- Access control (campaign codes or proper authentication)
- Complete XSS escaping
- Data validation and size limits

**See security documentation in Git history for implementation guidance.**

---

## 📊 **Data Format**

### **NPC Structure (npc_relationships.json):**
```json
{
  "npcs": {
    "Althessa the Rogue": {
      "name": "Althessa the Rogue",
      "faction": "Light Ring",
      "location": "Tormund",
      "status": "alive",
      "portrait": "Images/Althessa the Rogue.png",
      "tags": ["quest-giver", "important"],
      "notes": "A cunning thief with a heart of gold",
      "spoiler": false,
      "relationships": {
        "ally": ["Veris the Ex-Sorcerer"],
        "enemy": ["Mistress of Veils"],
        "family": []
      }
    }
  },
  "relationship_types": [
    {"name": "ally", "color": "#4CAF50"},
    {"name": "enemy", "color": "#F44336"},
    {"name": "family", "color": "#FF9800"}
  ],
  "factions": [
    {"name": "Light Ring", "color": "#FFD700"},
    {"name": "The Gilded Cage", "color": "#8B0000"}
  ]
}
```

### **Inventory Structure (Firebase):**
```json
{
  "partyGold": 1500,
  "version": 42,
  "lastModified": 1738794123456,
  "bagOfHolding": [
    {
      "_id": "item_1738794123_abc",
      "name": "Potion of Healing",
      "type": "potion",
      "quantity": 5,
      "weight": 0.5
    }
  ],
  "players": [
    {
      "name": "Theron",
      "gold": 50,
      "items": [...]
    }
  ]
}
```

---

## 🔧 **Customization**

### **Change Firebase Config:**
Edit `generate_mindmap.py` (line 1830):
```python
const FIREBASE_CONFIG = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT.firebaseapp.com",
    databaseURL: "https://YOUR_PROJECT.firebaseio.com",
    projectId: "YOUR_PROJECT",
    storageBucket: "YOUR_PROJECT.appspot.com"
};
```

### **Change Campaign ID:**
Edit `generate_mindmap.py` (line 1841):
```python
const CAMPAIGN_ID = "your-campaign-name";
```

### **Customize Factions:**
Edit faction colors in `npc_relationships.json`:
```json
"factions": [
  {"name": "My Faction", "color": "#FF0000"}
]
```

### **Add Custom Items:**
Edit `items.json` to add custom D&D items to the database.

---

## 🚀 **Deployment**

### **Option 1: GitHub Pages (Recommended)**
1. Fork this repository
2. Go to Settings → Pages
3. Set Source to "Deploy from branch: main"
4. Your app will be live at `https://yourusername.github.io/npc-mindmap-viewer/`

### **Option 2: Netlify**
1. Connect your GitHub repository
2. Build command: `python generate_mindmap.py`
3. Publish directory: `.`
4. Auto-deploy on push

### **Option 3: Firebase Hosting**
```bash
npm install -g firebase-tools
firebase login
firebase init hosting
firebase deploy
```

---

## 🧪 **Testing Multi-Player Features**

### **Test Concurrent Editing:**
1. Open app in **two browser windows** (or one normal + one incognito)
2. **Both windows:** Add different items to inventory
3. **Both windows:** Click save
4. **Both windows:** Refresh
5. **Expected:** Both items visible (no data loss)

### **Test Real-Time Sync:**
1. Open app in **two browser windows**
2. **Window 1:** Edit an NPC
3. **Window 2:** Should see the update automatically
4. **Expected:** Changes appear within seconds

### **Test Offline Mode:**
1. Disconnect from internet
2. Make changes (should see "Saved locally" notification)
3. Reconnect
4. Changes should sync automatically

---

## 📚 **Project Structure**

```
mindmap_viewer/
├── generate_mindmap.py       # Main build script (generates HTML)
├── npc_mindmap_viewer.html   # Generated app (open in browser)
├── npc_relationships.json    # NPC data source
├── items.json                # D&D 5e item database
├── item_processor.py         # Item processing utilities
├── item_validator.py         # Data validation utilities
├── database.rules.json       # Firebase security rules
├── index.html                # Redirect to main viewer
├── Images/                   # NPC portrait images
│   ├── Althessa the Rogue.png
│   └── ...
├── npc_mindmap.png          # Generated mind map image
├── NPC_RELATIONSHIP_MINDMAP.md  # Text mindmap export
└── README.md                # This file
```

---

## 🐛 **Troubleshooting**

### **Changes Don't Sync:**
- Check Firebase console (is data being written?)
- Check browser console for errors
- Verify Firebase config in `generate_mindmap.py`
- Ensure anonymous authentication is enabled in Firebase

### **Images Don't Load:**
- Check that images are in the `Images/` folder
- Verify file names match exactly (case-sensitive)
- Check browser console for 404 errors
- Try hard refresh (Ctrl+Shift+R)

### **Inventory Items Disappear:**
- This was a known issue, now fixed with transactions
- Ensure you're using the latest version from GitHub
- Clear browser cache if using an old version

### **Map Not Showing:**
- Verify world map SVG exists at `../Gienia World Map.svg`
- Check file size (must be < 50MB for GitHub Pages)
- Regenerate HTML with `python generate_mindmap.py`

---

## 💡 **Tips & Best Practices**

### **For DMs:**
- ✅ Use tags to organize NPCs ("quest-giver", "vendor", "important")
- ✅ Export JSON regularly as backup (Visual Editor → Export)
- ✅ Use spoiler mode to hide plot-sensitive NPCs from players
- ✅ Update world map markers as the campaign progresses
- ✅ Commit changes to Git for version history

### **For Players:**
- ✅ Bookmark the GitHub Pages URL for quick access
- ✅ Use filters to find specific NPCs quickly
- ✅ Track your personal inventory in the Inventory tab
- ✅ Coordinate with party on shared resources (Bag of Holding)
- ✅ If you see "Saved locally" notification, tell your DM (Firebase may be down)

### **For Everyone:**
- ✅ **Don't edit simultaneously** if possible (though now safe with transactions)
- ✅ Wait for "Save successful" notification before closing tab
- ✅ Refresh if data looks out of sync
- ✅ Report bugs via GitHub Issues

---

## 🎯 **Production Readiness**

### **✅ Ready for Production:**
- Multi-player concurrent editing (transaction-safe)
- Real-time synchronization
- Inventory management without data loss
- Map editing without conflicts
- NPC real-time updates
- Save failure handling with retry
- Debounced saves (efficient Firebase usage)

### **⚠️ For Public/Multiple Campaigns, Add:**
- Campaign isolation (currently single campaign)
- Access control (currently anyone can edit)
- XSS escaping for all user input
- Data validation and size limits

**For trusted private groups:** ✅ **Use as-is!**  
**For public hosting:** Implement security enhancements first.

---

## 📄 **License**

Free to use, modify, and distribute for personal or commercial use.

---

## 🤝 **Contributing**

Contributions welcome! Feel free to:
- Fork the repository
- Create feature branches
- Submit pull requests
- Report issues
- Share ideas

---

## 🙏 **Credits**

Built for D&D 5e campaigns with love.  
Uses Firebase for real-time collaboration.  
Item database from D&D 5e SRD.

---

## 📧 **Support**

- **Issues:** [GitHub Issues](your-repo-url/issues)
- **Discussions:** [GitHub Discussions](your-repo-url/discussions)

---

**Happy adventuring!** 🎲✨
