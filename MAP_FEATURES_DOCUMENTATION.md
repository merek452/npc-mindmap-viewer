# World Map Features Documentation

This document describes all the features of the World Map tab in the NPC Mindmap Viewer and the critical code that implements them. Use this as a reference when debugging or maintaining the map functionality.

## Table of Contents
1. [Core Features](#core-features)
2. [Map Loading & Rendering](#map-loading--rendering)
3. [Pan & Zoom](#pan--zoom)
4. [Markers System](#markers-system)
5. [Annotation/Drawing System](#annotationdrawing-system)
6. [Undo/Redo System](#undoredo-system)
7. [Data Persistence](#data-persistence)
8. [Coordinate System](#coordinate-system)
9. [Performance Optimizations](#performance-optimizations)
10. [Canvas Resolution & Quality](#canvas-resolution--quality)
11. [Known Issues & Fixes](#known-issues--fixes)

---

## Core Features

### 1. Tab Visibility Control
**Feature**: The World Map tab should only be visible when active, not appearing in other tabs.

**Critical Code**:
```787:800:npc_mindmap_viewer.html
.tab-content.active {
    display: block !important;
}

#mapTab {
    display: none;
    flex-direction: column;
    gap: 0;
}

#mapTab.active {
    display: flex !important;
}
```

**Why it matters**: The `#mapTab` CSS rule was originally set to `display: flex` unconditionally, which caused the map content to appear in the Card view tab. The fix ensures it only displays when the `active` class is present.

---

## Map Loading & Rendering

### 2. Map File Loading
**Feature**: Loads map from either HTML/Canvas format (preferred) or SVG format (fallback).

**Critical Code**:
```5071:5248:npc_mindmap_viewer.html
// Function to load map (SVG or HTML/Canvas)
function loadSvgMap() {
    // Tries to load HTML/Canvas version first, falls back to SVG
    // Handles both formats and sets up appropriate rendering
}
```

**Key Functions**:
- `loadSvgMap()` - Main loading function
- `setupHtmlMap(htmlContent)` - Sets up HTML/Canvas map rendering
- `fitMapToViewport()` - Auto-fits map to viewport on load

### 3. Viewport Auto-Fit
**Feature**: Automatically fits the map to the viewport when first loaded.

**Critical Code**:
```5285:5337:npc_mindmap_viewer.html
function fitMapToViewport() {
    if (!mapContainer) return;
    const containerRect = mapContainer.getBoundingClientRect();
    const containerWidth = containerRect.width || window.innerWidth;
    const containerHeight = containerRect.height || window.innerHeight;
    
    // Ensure container has dimensions
    if (containerWidth === 0 || containerHeight === 0) {
        console.warn('Map container has no dimensions, retrying...');
        setTimeout(fitMapToViewport, 100);
        return;
    }
    
    // Get base map dimensions from first page
    let mapWidth = 1097.25; // Default from your debug output
    let mapHeight = 474.00;
    
    // Query pageContainer from mapSvgContainer (it's defined in setupHtmlMap scope)
    const pageContainer = mapSvgContainer ? mapSvgContainer.querySelector('#page-container') : null;
    if (pageContainer) {
        const firstPage = pageContainer.querySelector('.pf');
        if (firstPage) {
            const pageRect = firstPage.getBoundingClientRect();
            mapWidth = pageRect.width || mapWidth;
            mapHeight = pageRect.height || mapHeight;
        }
    }
    
    // Simple: use larger scale to fill viewport completely
    const scaleX = containerWidth / mapWidth;
    const scaleY = containerHeight / mapHeight;
    mapScale = Math.max(scaleX, scaleY);
    
    // Center the map
    mapX = 0;
    mapY = 0;
    
    // Store base dimensions - CRITICAL for coordinate calculations
    baseMapWidth = mapWidth;
    baseMapHeight = mapHeight;
    
    // Update bounds and transform
    updateMapTransform();
}
```

**Important Fix**: The `pageContainer` variable was originally referenced from outside its scope, causing a `ReferenceError`. The fix queries it directly from `mapSvgContainer` inside the function.

---

## Pan & Zoom

### 4. Mouse Wheel Zoom
**Feature**: Zoom in/out with mouse wheel, keeping the point under the cursor fixed.

**Critical Code**:
```5542:5589:npc_mindmap_viewer.html
mapContainer.addEventListener('wheel', function(e) {
    e.preventDefault();
    
    const rect = mapContainer.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.max(0.5, Math.min(20, mapScale * delta));
    
    // Calculate world coordinates under mouse
    const viewportCenterX = rect.width / 2;
    const viewportCenterY = rect.height / 2;
    const worldX = (mouseX - viewportCenterX + mapWidth / 2 - mapX) / mapScale;
    const worldY = (mouseY - viewportCenterY + mapHeight / 2 - mapY) / mapScale;
    
    // After zoom, keep same world point under mouse
    mapX = mouseX - viewportCenterX + mapWidth / 2 - worldX * newScale;
    mapY = mouseY - viewportCenterY + mapHeight / 2 - worldY * newScale;
    
    mapScale = newScale;
    updateMapTransform();
});
```

### 5. Click and Drag Panning
**Feature**: Click and drag to pan the map around.

**Critical Code**: Mouse and touch event handlers manage panning state and update `mapX` and `mapY` coordinates.

### 6. Reset View Button
**Feature**: Reset button to return map to initial view.

**Critical Code**:
```4900:4915:npc_mindmap_viewer.html
function resetMapView() {
    if (!mapContainer || !mapSvgContainer) return;
    mapScale = 1;
    mapX = 0;
    mapY = 0;
    updateMapTransform();
}
```

### 7. Transform Updates
**Feature**: Updates the CSS transform to position and scale the map.

**Critical Code**:
```5397:5538:npc_mindmap_viewer.html
function updateMapTransform() {
    if (!mapSvgContainer && !mapCanvas) return;
    
    // Constrain pan to bounds (only when not actively panning/zooming for performance)
    if (!isPanning && !isZooming) {
        constrainPan();
    }
    
    // Throttle transform updates during pan/zoom for better performance
    if (transformUpdateScheduled) return;
    
    transformUpdateScheduled = true;
    
    requestAnimationFrame(function() {
        // Canvas mode is MUCH faster - just transform the canvas element
        if (isCanvasMode && mapCanvas) {
            mapCanvas.style.transform = `translate(calc(-50% + ${mapX}px), calc(-50% + ${mapY}px)) scale(${mapScale})`;
            mapCanvas.style.transformOrigin = 'center center';
        } else if (mapSvgContainer) {
            // SVG mode - transform the container
            const centerX = -(containerWidth / 2) + mapX;
            const centerY = -(containerHeight / 2) + mapY;
            mapSvgContainer.style.transform = `translate(${centerX}px, ${centerY}px) scale(${mapScale})`;
            mapSvgContainer.style.transformOrigin = '0 0';
        }
        
        // Update zoom display
        if (zoomLevelDisplay) {
            zoomLevelDisplay.textContent = `Zoom: ${Math.round(mapScale * 100)}%`;
        }
        
        transformUpdateScheduled = false;
        
        // Render markers and annotations (throttled)
        if (svgLoaded && !isZooming && !isPanning) {
            renderMarkers();
            renderAnnotations();
        }
    });
}
```

---

## Markers System

### 8. Add Marker Mode
**Feature**: Click to add location markers on the map.

**Critical Code**:
```4917:4932:npc_mindmap_viewer.html
function toggleMarkerMode() {
    if (!mapContainer) return;
    markerMode = !markerMode;
    annotationMode = false;
    const btn = document.getElementById('addMarkerBtn');
    const drawBtn = document.getElementById('drawAnnotationBtn');
    if (btn) {
        btn.style.background = markerMode ? 'rgba(33,150,243,0.6)' : 'rgba(33,150,243,0.3)';
        btn.textContent = markerMode ? '📍 Cancel' : '📍 Add Marker';
    }
    if (drawBtn) {
        drawBtn.style.background = 'rgba(156,39,176,0.3)';
        drawBtn.textContent = '✏️ Draw';
    }
    mapContainer.style.cursor = markerMode ? 'crosshair' : 'grab';
}
```

### 9. Marker Dialog
**Feature**: Dialog to add/edit markers with name, category, color, and notes.

**Critical Code**:
```6233:6313:npc_mindmap_viewer.html
function showMarkerDialog(mapCoords, callback, existingMarker) {
    // Creates a modal dialog for marker creation/editing
    // Handles category selection, color picker, and notes
}
```

### 10. Marker Categories
**Feature**: Markers can be categorized (City, Dungeon, Landmark, Other) with different icons and default colors.

**Critical Code**:
```4882:4887:npc_mindmap_viewer.html
const markerCategories = {
    'city': { name: 'City', color: '#4CAF50', icon: '🏙️' },
    'dungeon': { name: 'Dungeon', color: '#F44336', icon: '🏰' },
    'landmark': { name: 'Landmark', color: '#FF9800', icon: '🗿' },
    'other': { name: 'Other', color: '#9E9E9E', icon: '📍' }
};
```

### 11. Location List Sidebar
**Feature**: Sidebar showing all markers with search and filter capabilities.

**Critical Code**:
```6349:6381:npc_mindmap_viewer.html
function updateLocationList() {
    if (!locationList) return;
    const filter = document.getElementById('markerCategoryFilter')?.value || 'all';
    const searchTerm = (document.getElementById('markerSearchInput')?.value || '').toLowerCase().trim();
    
    // Filter markers by category and search term
    // Render list items with click-to-zoom functionality
}
```

### 12. Zoom to Marker
**Feature**: Click a marker in the sidebar to zoom to its location.

**Critical Code**:
```6387:6399:npc_mindmap_viewer.html
function zoomToMarker(marker) {
    const rect = mapContainer.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    // Set zoom level first
    mapScale = Math.max(2, mapScale);
    // Center the marker
    mapX = centerX - (marker.x * mapScale);
    mapY = centerY - (marker.y * mapScale);
    updateMapTransform();
}
```

---

## Annotation/Drawing System

### 13. Drawing Mode
**Feature**: Freehand drawing on the map with annotations.

**Critical Code**:
```4934:4952:npc_mindmap_viewer.html
function toggleAnnotationMode() {
    if (!mapContainer) return;
    annotationMode = !annotationMode;
    markerMode = false;
    const btn = document.getElementById('drawAnnotationBtn');
    const markerBtn = document.getElementById('addMarkerBtn');
    if (btn) {
        btn.style.background = annotationMode ? 'rgba(156,39,176,0.6)' : 'rgba(156,39,176,0.3)';
        btn.textContent = annotationMode ? '✏️ Cancel' : '✏️ Draw';
    }
    mapContainer.style.cursor = annotationMode ? 'crosshair' : 'grab';
    if (!annotationMode && isDrawing) {
        finishAnnotation();
    }
}
```

### 14. Annotation Rendering
**Feature**: Renders drawn paths as SVG elements that scale with zoom.

**Critical Code**: Annotation paths are stored as arrays of world coordinates and rendered as SVG `<path>` elements in the `mapOverlay` SVG element.

---

## Undo/Redo System

### 15. History Stack
**Feature**: Undo/redo functionality for markers and annotations.

**Critical Code**:
```5904:5962:npc_mindmap_viewer.html
function saveToHistory() {
    const state = {
        markers: JSON.parse(JSON.stringify(markers)),
        annotations: JSON.parse(JSON.stringify(annotations))
    };
    // Remove any future history if we're not at the end
    if (historyIndex < historyStack.length - 1) {
        historyStack = historyStack.slice(0, historyIndex + 1);
    }
    historyStack.push(state);
    if (historyStack.length > MAX_HISTORY) {
        historyStack.shift();
    } else {
        historyIndex++;
    }
    updateUndoRedoButtons();
}

function undoMapAction() {
    if (historyIndex > 0) {
        historyIndex--;
        const state = historyStack[historyIndex];
        markers = JSON.parse(JSON.stringify(state.markers));
        annotations = JSON.parse(JSON.stringify(state.annotations));
        renderMarkers();
        renderAnnotations();
        updateLocationList();
        updateUndoRedoButtons();
        saveMapData();
    }
}

function redoMapAction() {
    if (historyIndex < historyStack.length - 1) {
        historyIndex++;
        const state = historyStack[historyIndex];
        markers = JSON.parse(JSON.stringify(state.markers));
        annotations = JSON.parse(JSON.stringify(state.annotations));
        renderMarkers();
        renderAnnotations();
        updateLocationList();
        updateUndoRedoButtons();
        saveMapData();
    }
}
```

---

## Data Persistence

### 16. Save/Load Map Data
**Feature**: Saves markers and annotations to Firebase (with localStorage fallback).

**Critical Code**:
```5869:5901:npc_mindmap_viewer.html
function loadMapData() {
    loadFromFirebase('mapMarkers', function(data) {
        if (data && Array.isArray(data)) {
            markers = data;
        }
        loadFromFirebase('mapAnnotations', function(annotData) {
            if (annotData && Array.isArray(annotData)) {
                annotations = annotData;
            }
            // Initialize history with initial state
            const initialState = {
                markers: JSON.parse(JSON.stringify(markers)),
                annotations: JSON.parse(JSON.stringify(annotations))
            };
            historyStack = [initialState];
            historyIndex = 0;
            updateUndoRedoButtons();
            renderMarkers();
            renderAnnotations();
            updateLocationList();
        });
    });
}

function saveMapData() {
    saveToFirebase('mapMarkers', markers);
    saveToFirebase('mapAnnotations', annotations);
    // Save to history
    saveToHistory();
}
```

---

## Coordinate System

### 17. Screen to Map Coordinates
**Feature**: Converts screen coordinates to world map coordinates.

**Critical Code**:
```5983:5998:npc_mindmap_viewer.html
function screenToMap(screenX, screenY) {
    const rect = mapContainer.getBoundingClientRect();
    const containerX = screenX - rect.left;
    const containerY = screenY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    // World coordinates: account for transform-origin 0,0 and the centering transform
    // Transform is: translate(-containerWidth/2 + mapX, -containerHeight/2 + mapY) scale(mapScale)
    // So: containerX = centerX + (-containerWidth/2 + mapX) + worldX * mapScale
    // Therefore: worldX = (containerX - centerX + containerWidth/2 - mapX) / mapScale
    const containerWidth = baseMapWidth || rect.width / mapScale;
    const containerHeight = baseMapHeight || rect.height / mapScale;
    const coordX = (containerX - centerX + containerWidth / 2 - mapX) / mapScale;
    const coordY = (containerY - centerY + containerHeight / 2 - mapY) / mapScale;
    return { x: coordX, y: coordY };
}
```

### 18. Map to Screen Coordinates
**Feature**: Converts world map coordinates to screen coordinates.

**Critical Code**:
```6001:6010:npc_mindmap_viewer.html
function mapToScreen(worldX, worldY) {
    const rect = mapContainer.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    // Use stored base dimensions (not calculated from rect which is scaled)
    const containerWidth = baseMapWidth || 1097.25;
    const containerHeight = baseMapHeight || 474.00;
    // Transform: translate(-containerWidth/2 + mapX, -containerHeight/2 + mapY) scale(mapScale)
    const screenX = centerX - containerWidth / 2 + mapX + worldX * mapScale;
    const screenY = centerY - containerHeight / 2 + mapY + worldY * mapScale;
    return { x: screenX, y: screenY };
}
```

**Important**: The coordinate system uses `baseMapWidth` and `baseMapHeight` which are set during `fitMapToViewport()`. These are critical for accurate coordinate conversions.

---

## Performance Optimizations

### 19. Throttled Rendering
**Feature**: Markers and annotations are only re-rendered when not actively panning/zooming.

**Critical Code**:
```5518:5536:npc_mindmap_viewer.html
// Skip marker/annotation rendering during active zoom/pan for better performance
// SVG scales perfectly without needing to re-render markers
const now = Date.now();
if (svgLoaded && !isZooming && !isPanning && (now - lastRenderTime > RENDER_THROTTLE)) {
    if (renderRafId) cancelAnimationFrame(renderRafId);
    renderRafId = requestAnimationFrame(function() {
        const renderStart = isDebugMode() ? performance.now() : 0;
        renderMarkers();
        renderAnnotations();
        if (isDebugMode()) {
            const renderTime = performance.now() - renderStart;
            if (renderTime > 10) {
                console.warn(`⚠️ Slow marker render: ${renderTime.toFixed(2)}ms`);
            }
        }
        lastRenderTime = now;
        renderRafId = null;
    });
}
```

### 20. Transform Update Throttling
**Feature**: Transform updates are throttled using `requestAnimationFrame` and a scheduling flag.

**Critical Code**:
```5416:5420:npc_mindmap_viewer.html
// Throttle transform updates during pan/zoom for better performance
if (transformUpdateScheduled) return;

transformUpdateScheduled = true;
```

---

## Canvas Resolution & Quality

### 21. High-Resolution Canvas Rendering
**Feature**: Canvas is rendered at high resolution to maintain text readability when zoomed in.

**Critical Code**:
```5115:5146:npc_mindmap_viewer.html
if (canvasEl) {
    // Get device pixel ratio for high-DPI displays
    const dpr = window.devicePixelRatio || 1;
    // Use higher resolution for better text quality when zoomed (max zoom is 20x)
    // For standard displays: 4x, for high-DPI: 2x DPR (so 4x on 2x displays, 6x on 3x displays)
    const scaleFactor = Math.max(4, dpr * 2);
    
    // Set canvas to high resolution (internal resolution)
    const baseWidth = canvasEl.width || 2000;
    const baseHeight = canvasEl.height || 2000;
    const canvasWidth = baseWidth * scaleFactor;
    const canvasHeight = baseHeight * scaleFactor;
    
    mapCanvas.width = canvasWidth;
    mapCanvas.height = canvasHeight;
    
    // Set display size (CSS) to original size
    mapCanvas.style.width = baseWidth + 'px';
    mapCanvas.style.height = baseHeight + 'px';
    
    // Get the canvas context and configure for high quality
    const ctx = mapCanvas.getContext('2d');
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.scale(scaleFactor, scaleFactor);
}
```

**How it works**:
- Canvas internal resolution is set to `baseSize * scaleFactor` (minimum 4x)
- Canvas display size remains at base size (CSS)
- Context is scaled so the image is drawn at the correct size in the high-res canvas
- When zoomed, the browser scales the high-resolution canvas, preserving detail

**Resolution Strategy**:
- Standard displays (1x DPR): 4x resolution
- High-DPI displays (2x DPR): 4x resolution (2 * 2)
- Ultra-high DPI (3x DPR): 6x resolution (3 * 2)

This ensures text remains readable even at maximum zoom (20x).

---

## Known Issues & Fixes

### Issue 1: `pageContainer is not defined` Error
**Problem**: The `fitMapToViewport()` function was trying to access `pageContainer` which was defined in a different scope.

**Fix**: Query `pageContainer` directly from `mapSvgContainer` inside the function:
```5302:5309:npc_mindmap_viewer.html
// Query pageContainer from mapSvgContainer (it's defined in setupHtmlMap scope)
const pageContainer = mapSvgContainer ? mapSvgContainer.querySelector('#page-container') : null;
if (pageContainer) {
    const firstPage = pageContainer.querySelector('.pf');
    if (firstPage) {
        const pageRect = firstPage.getBoundingClientRect();
        mapWidth = pageRect.width || mapWidth;
        mapHeight = pageRect.height || mapHeight;
    }
}
```

### Issue 2: Map Content Appearing in Card View Tab
**Problem**: The `#mapTab` CSS rule had `display: flex` unconditionally, causing it to appear even when not active.

**Fix**: Changed CSS to only display when active:
```791:800:npc_mindmap_viewer.html
#mapTab {
    display: none;
    flex-direction: column;
    gap: 0;
}

#mapTab.active {
    display: flex !important;
}
```

---

## Key Global Variables

- `mapScale` - Current zoom level (1.0 = 100%)
- `mapX`, `mapY` - Pan offset from center
- `baseMapWidth`, `baseMapHeight` - Original map dimensions (set during `fitMapToViewport()`)
- `markers` - Array of marker objects
- `annotations` - Array of annotation objects
- `markerMode` - Boolean, true when in marker placement mode
- `annotationMode` - Boolean, true when in drawing mode
- `historyStack` - Array of history states for undo/redo
- `historyIndex` - Current position in history stack

---

## Debugging Tips

1. **Enable debug mode**: Set `window.DEBUG_PERFORMANCE = true` in console
2. **Check base dimensions**: Look for `🔍 BASE DIMENSIONS SET:` in console
3. **Monitor transform updates**: Debug mode shows transform update frequency
4. **Check coordinate conversions**: Use `screenToMap()` and `mapToScreen()` in console to test

---

## File Locations

- Main HTML file: `npc_mindmap_viewer.html`
- Map image files: `Images/Gienia World Map.svg` or `Images/Gienia-World-Map.html`
- This documentation: `MAP_FEATURES_DOCUMENTATION.md`

---

*Last updated: After fixing pageContainer scope issue and mapTab visibility issue*
