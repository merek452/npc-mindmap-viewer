# Collaborative D&D Campaign Tracker

A real-time collaborative web application for managing D&D campaign NPCs, relationships, inventory, and world maps. Built for multi-player groups with transaction-safe concurrent editing and Firebase real-time synchronization.

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

### 🗺️ **World Map System**
- **Interactive world map** - Pan, zoom, and annotate your campaign world
- **Markers** - Add location markers with categories (cities, dungeons, landmarks)
- **Annotations** - Draw paths, regions, and notes directly on the map
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

1. **Open the live app:** Visit the URL
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
