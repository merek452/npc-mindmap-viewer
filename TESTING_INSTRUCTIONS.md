# World Map Module - Testing Instructions

## Quick Start

1. **Open the HTML file**: `npc_mindmap_viewer.html` in your browser
2. **Open Developer Console**: Press F12 to open browser developer tools
3. **Click the tab**: Click "🌍 World Map (New)" tab
4. **Run test script**: Copy and paste the contents of `WORLD_MAP_BROWSER_TEST.js` into the console

## Automated Test Script

The file `WORLD_MAP_BROWSER_TEST.js` contains automated tests that will:
- Check if WorldMapModule is defined
- Verify all DOM elements exist
- Test module initialization
- Check for JavaScript errors
- Verify Firebase functions are available

## Manual Testing Checklist

### ✅ Module Structure
- [x] WorldMapModule is defined and modular
- [x] All core modules (MapState, MapRenderer, MapController, MapCoordinateSystem) exist
- [x] All feature modules (MarkerSystem, AnnotationSystem) exist
- [x] All data modules (MapDataManager) exist
- [x] All UI modules (ControlPanel, Sidebar) exist

### 🔍 Test Each Function

#### 1. Map Loading
1. Click "🌍 World Map (New)" tab
2. Check console for: "🌍 [WorldMap] Module initialized successfully"
3. Verify map displays (should see map content)
4. If map doesn't load, check console for errors

#### 2. Zoom Functionality
1. **Mouse wheel zoom**: Scroll mouse wheel up/down
   - Map should zoom in/out
   - Zoom should center on cursor position
   - Zoom level display should update
2. **Double-click reset**: Double-click on map
   - Map should reset to initial view
3. **Reset button**: Click "🔄 Reset View" button
   - Map should reset to initial view

#### 3. Pan Functionality
1. **Mouse drag**: Click and drag on map
   - Map should pan smoothly
   - Cursor should change to "grabbing" while dragging
2. **Touch drag** (mobile/tablet): Touch and drag
   - Map should pan with finger movement

#### 4. Marker System
1. **Add marker**:
   - Click "📍 Add Marker" button (should highlight)
   - Click anywhere on map
   - Dialog should open
   - Fill in name, select category, choose color, add notes
   - Click "Add" button
   - Marker should appear on map
2. **View marker**:
   - Click on a marker
   - Info dialog should open showing marker details
3. **Edit marker**:
   - Click marker to open info dialog
   - Click "✏️ Edit" button
   - Edit dialog should open with existing data
   - Make changes and save
   - Marker should update
4. **Delete marker**:
   - Click marker to open info dialog
   - Click "🗑️ Delete" button
   - Confirm deletion
   - Marker should disappear
5. **Search markers**:
   - Type in search box in sidebar
   - Marker list should filter
6. **Filter by category**:
   - Select category from dropdown
   - Marker list should filter
7. **Zoom to marker**:
   - Click marker in sidebar list
   - Map should zoom to and center on marker
   - Or click "🔍 Zoom To" in marker info dialog

#### 5. Annotation System
1. **Draw annotation**:
   - Click "✏️ Draw" button (should highlight)
   - Click and drag on map to draw
   - Path should appear as you draw
   - Release mouse to finish
   - Annotation should be saved
2. **Delete annotation**:
   - Click on a drawn path
   - Confirmation dialog should appear
   - Confirm deletion
   - Path should disappear

#### 6. Touch/Mobile Support
1. **Pinch zoom**: Use two fingers to pinch
   - Map should zoom in/out
   - Zoom should center on pinch point
2. **Touch pan**: Single finger drag
   - Map should pan
3. **Touch marker**: Tap on map in marker mode
   - Marker dialog should open
4. **Touch draw**: Tap and drag in draw mode
   - Annotation should be drawn

#### 7. Real-time Sync (Firebase)
1. Open the page in two browser windows/tabs
2. In window 1: Add a marker
3. In window 2: Marker should appear automatically
4. In window 1: Edit the marker
5. In window 2: Changes should appear automatically
6. In window 1: Delete the marker
7. In window 2: Marker should disappear automatically

#### 8. Data Persistence
1. Add several markers and annotations
2. Refresh the page (F5)
3. Markers and annotations should still be there
4. Check console for load messages

## Expected Console Output

When the tab is opened, you should see:
```
🌍 [WorldMap] Initializing World Map Module...
🌍 [MapRenderer] Loading map...
🌍 [MapRenderer] Canvas map loaded (or SVG map loaded)
🌍 [WorldMap] Module initialized successfully
```

## Common Issues to Check

1. **Map doesn't load**:
   - Check if PLACEHOLDER_SVG_CONTENT is defined
   - Check console for errors
   - Verify map file exists

2. **Markers don't appear**:
   - Check if worldMapOverlay element exists
   - Check console for rendering errors
   - Verify MapState has markers data

3. **Zoom/Pan doesn't work**:
   - Check if worldMapContainer element exists
   - Verify event handlers are attached
   - Check console for errors

4. **Real-time sync doesn't work**:
   - Check if Firebase is initialized
   - Check if database variable is accessible
   - Verify Firebase rules allow read/write

5. **Touch doesn't work**:
   - Verify touch event handlers are attached
   - Check if device supports touch
   - Test on actual mobile device

## Code Verification

The module is structured as:
- **Core**: MapState, MapCoordinateSystem, MapRenderer, MapController
- **Features**: MarkerSystem, AnnotationSystem
- **Data**: MapDataManager
- **UI**: ControlPanel, Sidebar

All modules are properly scoped within the WorldMapModule IIFE and communicate through defined interfaces.

## Reporting Issues

If you find any issues:
1. Note the exact steps to reproduce
2. Check browser console for errors
3. Note browser and OS version
4. Check if issue occurs in both old map tab and new worldMap tab
