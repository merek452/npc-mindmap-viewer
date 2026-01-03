# NPC Mind Map Viewer

Interactive D&D campaign NPC relationship tracker and mind map viewer. A self-contained, offline-capable tool for managing NPCs, their relationships, and campaign inventory.

## 🌟 Features

- **NPC Relationship Visualization** - Interactive mind map showing connections between NPCs
- **NPC Card View** - Browse NPCs with filters by faction, status, location, and tags
- **Interactive Mind Map** - Zoom, pan, and explore NPC relationships visually
- **Inventory Tracker** - Track party inventory, player items, and gold
- **NPC Editor** - Visual editor for managing NPC relationships and data
- **Mobile Compatible** - Responsive design works on iPhone, Android, and desktop
- **Offline-First** - Single HTML file, works without internet connection
- **Self-Contained** - No backend required, all data stored locally

## 🚀 Quick Start

1. **For Players:** Simply open `npc_mindmap_viewer.html` in any web browser
2. **For DMs:** Edit `npc_relationships.json` and run `python generate_mindmap.py` to regenerate

## 📁 Files

### Main Files
- **npc_mindmap_viewer.html** - Main HTML viewer (open this in a browser)
- **generate_mindmap.py** - Python script that generates the HTML from JSON data
- **npc_relationships.json** - Source data file containing all NPC relationships
- **items.json** - Item database used by the inventory tracker

### Supporting Files
- **item_processor.py** - Utility module for processing items
- **item_validator.py** - Utility module for validating item data

## 🛠️ Usage

### For Players
Just open `npc_mindmap_viewer.html` in your web browser. All data is stored locally in your browser.

### For DMs
1. Edit `npc_relationships.json` to update NPC relationships
2. Run `python generate_mindmap.py` to regenerate the HTML viewer
3. Share the updated `npc_mindmap_viewer.html` with your players

## 📋 Requirements

- **Python 3.6+** (only needed for generating the HTML)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **No internet required** (after initial load, works offline)

## 🎮 How to Use

### NPC Cards Tab
- Filter NPCs by faction, status, location, or search by name
- Group by faction, location, or status
- Sort alphabetically or by various criteria
- Click NPC cards to highlight them in the mind map

### Mind Map Tab
- Zoom with mouse wheel or pinch gesture
- Pan by dragging
- Click nodes to highlight corresponding NPC cards
- Use controls to toggle physics, edge labels, and more

### Inventory Tab
- Track party gold and individual player inventories
- Add items from the D&D 5e item database
- Drag and drop items between containers
- Auto-stacking for stackable items

### Editor Tab
- Add, edit, and delete NPCs
- Manage relationships between NPCs
- Export JSON for backup
- Validate data integrity

## 🌐 Hosting

This tool can be hosted on:
- **GitHub Pages** (free) - See `GITHUB_PAGES_SETUP.md` for instructions
- **Netlify** (free)
- **Any static hosting service**

## 📝 Data Format

NPCs are stored in JSON format:
```json
{
  "npcs": {
    "NPC Name": {
      "name": "NPC Name",
      "faction": "Faction Name",
      "location": "Location",
      "status": "alive",
      "tags": ["tag1", "tag2"],
      "relationships": {
        "ally": ["Other NPC"],
        "enemy": ["Another NPC"]
      },
      "notes": "NPC description"
    }
  }
}
```

## 🔧 Customization

- Edit `generate_mindmap.py` to customize colors, layouts, and features
- Modify faction colors in the script
- Add custom relationship types
- Customize the item database in `items.json`

## 📄 License

Free to use and modify for personal or commercial use.

## 🤝 Contributing

Feel free to fork, modify, and use this tool for your own campaigns!

## 📚 Documentation

- `GITHUB_PAGES_SETUP.md` - How to host on GitHub Pages
- `IMPROVEMENTS_AND_HOSTING.md` - Feature ideas and hosting options
- `PERFORMANCE_IMPROVEMENTS.md` - Performance optimization guide

## 🐛 Issues

If you encounter any issues:
1. Check that all files are in the same directory
2. Ensure `npc_relationships.json` is valid JSON
3. Clear browser cache and reload
4. Check browser console for errors

## 💡 Tips

- Use tags to organize NPCs (e.g., "important", "quest-giver", "merchant")
- The mind map auto-arranges, but you can use "Spread Nodes" if things get clustered
- Export your data regularly as JSON backup
- Use spoiler-free mode when sharing with players

---

**Made for D&D 5e campaigns. Enjoy!**
