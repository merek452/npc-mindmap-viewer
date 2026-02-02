# How to Test the World Map Module

## Which Tab Are We Working On?

**Answer: "🌍 World Map (New)"** - This is the NEW modular implementation.

There are TWO tabs:
1. **"🗺️ World Map"** - The OLD implementation (we're NOT modifying this)
2. **"🌍 World Map (New)"** - The NEW modular implementation (this is what we're working on)

## Quick Fix Applied

I just added the missing CSS styles for the `worldMapTab`. The tab should now display properly instead of being blank.

## How to Run the Browser Test Script

### Step 1: Open the HTML File
1. Open `npc_mindmap_viewer.html` in your web browser (Chrome, Firefox, Edge, etc.)

### Step 2: Open Developer Console
- **Chrome/Edge**: Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
- **Firefox**: Press `F12` or `Ctrl+Shift+K` (Windows) / `Cmd+Option+K` (Mac)
- **Safari**: Press `Cmd+Option+I` (Mac) - you may need to enable Developer menu first

### Step 3: Open the Console Tab
- In the Developer Tools window, click on the **"Console"** tab
- This is where you'll see JavaScript output and errors

### Step 4: Copy the Test Script
1. Open the file `WORLD_MAP_BROWSER_TEST.js` in a text editor
2. Select all the text (`Ctrl+A` / `Cmd+A`)
3. Copy it (`Ctrl+C` / `Cmd+C`)

### Step 5: Paste and Run
1. Click in the Console area of the browser
2. Paste the script (`Ctrl+V` / `Cmd+V`)
3. Press `Enter` to run it

### Step 6: View Results
- The script will automatically test various aspects of the module
- You'll see output like:
  - ✅ for things that work
  - ❌ for things that don't work
  - ⚠️ for warnings

## Alternative: Manual Testing

If you prefer to test manually:

1. **Click the "🌍 World Map (New)" tab**
2. **Check the console** (F12) for any errors
3. **Look for these messages**:
   - "🌍 [WorldMap] Initializing World Map Module..."
   - "🌍 [WorldMap] Module initialized successfully"
4. **Try these actions**:
   - Scroll mouse wheel to zoom
   - Click and drag to pan
   - Click "📍 Add Marker" then click on map
   - Click "✏️ Draw" then draw on map

## What Should You See?

After clicking "🌍 World Map (New)" tab, you should see:

1. **Control Panel** at the top with buttons:
   - 🔄 Reset View
   - ✋ Pan
   - 📍 Add Marker
   - ✏️ Draw
   - Zoom level display

2. **Map Area** in the center (should show the map or an error message)

3. **Sidebar** on the right with:
   - Search box
   - Category filter
   - Location list

## Troubleshooting

### If you still see a blank page:

1. **Check the console** (F12) for errors
2. **Look for these common issues**:
   - `WorldMapModule is not defined` - Module didn't load
   - `Cannot read property 'getElementById'` - DOM not ready
   - `PLACEHOLDER_SVG_CONTENT is not defined` - Map content missing

3. **Try refreshing the page** (F5)

4. **Check if the tab is actually visible**:
   - In console, type: `document.getElementById('worldMapTab')`
   - Should return an element, not `null`

### If the map doesn't load:

- The map content comes from `PLACEHOLDER_SVG_CONTENT`
- This is populated from the map file during HTML generation
- Check console for: "🌍 [MapRenderer] Loading map..."

## Next Steps

1. Run the browser test script
2. Report any errors you see
3. Test the manual functions (zoom, pan, markers, etc.)
4. Let me know what works and what doesn't!
