# World Map Tab - Architecture & Design Document

## Overview
This document outlines the complete architecture for a new, cleanly-designed World Map tab that supports high-resolution rendering, interactive features, and easy extensibility.

## Core Requirements Checklist

### ✅ Map Loading & Display
- [x] **Load SVG file** - Load SVG map from file system
- [x] **Convert SVG to Canvas** - Convert SVG to high-resolution canvas for rendering
- [x] **Center map on load** - Automatically center map in viewport on initial load
- [x] **High-resolution rendering** - Support high detail without performance degradation

### ✅ Zoom & Pan
- [x] **Zoom in/out** - Mouse wheel zoom with smooth transitions
- [x] **Zoom to mouse position** - Zoom centers on mouse cursor position (not viewport center)
- [x] **Pan map** - Click and drag to pan the map
- [x] **Pan bounds** - Prevent panning outside map boundaries

### ✅ Markers
- [x] **Place markers** - Click to place markers at mouse position
- [x] **Fixed to map** - Markers stay fixed to world coordinates during zoom/pan
- [x] **Color coding** - Markers support custom colors
- [x] **Various icons** - Markers support different icon types
- [x] **Add notes** - Markers have description/notes field
- [x] **Search markers** - Search functionality for finding markers
- [x] **Delete markers** - Ability to delete markers

### ✅ Drawings/Annotations
- [x] **Place drawings** - Draw annotations at mouse position
- [x] **Fixed to map** - Drawings stay fixed to world coordinates during zoom/pan
- [x] **Delete drawings** - Ability to delete annotations

---

## 1. Core Architecture

### 1.1 Module Structure
```
WorldMapModule
├── Core
│   ├── MapRenderer (handles all rendering logic)
│   ├── MapController (handles all user interactions)
│   ├── MapState (manages all state)
│   └── MapCoordinateSystem (world ↔ screen conversions)
├── Features
│   ├── MarkerSystem (markers/POIs)
│   ├── AnnotationSystem (drawing/paths)
│   ├── LayerSystem (multiple map layers)
│   └── MeasurementSystem (distance/ruler)
├── Data
│   ├── MapDataManager (loading/saving)
│   ├── FirebaseSync (real-time sync)
│   └── LocalStorage (offline cache)
└── UI
    ├── ControlPanel (buttons/controls)
    ├── Sidebar (markers list/filters)
    └── Toolbar (tools/utilities)
```

### 1.2 Separation of Concerns
- **Rendering**: Completely isolated from business logic
- **State Management**: Single source of truth, immutable updates
- **Event Handling**: Centralized event dispatcher
- **Data Persistence**: Abstracted behind interfaces

---

## 2. Data Models

### 2.1 Map State
```javascript
MapState = {
    // Viewport
    viewport: {
        panX: number,        // Pan offset in pixels
        panY: number,        // Pan offset in pixels
        zoom: number,         // Zoom level (1.0 = 100%)
        minZoom: number,      // Minimum zoom (e.g., 0.1)
        maxZoom: number,      // Maximum zoom (e.g., 20.0)
        bounds: {             // Viewport bounds in world coordinates
            minX: number,
            maxX: number,
            minY: number,
            maxY: number
        }
    },
    
    // Map Source
    mapSource: {
        type: 'svg' | 'image' | 'tiles',
        url: string,
        baseWidth: number,    // Original map width in pixels
        baseHeight: number,   // Original map height in pixels
        worldBounds: {         // World coordinate bounds
            minX: number,
            maxX: number,
            minY: number,
            maxY: number
        }
    },
    
    // Rendering
    rendering: {
        mode: 'canvas' | 'svg',
        resolution: number,   // Current canvas resolution multiplier
        targetResolution: number, // Target resolution for re-rendering
        isRendering: boolean,
        lastRenderTime: number
    },
    
    // Interaction
    interaction: {
        mode: 'pan' | 'marker' | 'annotation' | 'measure' | 'select',
        isPanning: boolean,
        isZooming: boolean,
        isDrawing: boolean,
        cursor: string
    },
    
    // Features
    markers: Marker[],
    annotations: Annotation[],
    layers: Layer[],
    measurements: Measurement[]
}
```

### 2.2 Marker Model
```javascript
Marker = {
    id: string,              // Unique identifier
    worldX: number,           // World X coordinate
    worldY: number,           // World Y coordinate
    name: string,
    category: string,         // 'city' | 'dungeon' | 'landmark' | 'other'
    description: string,
    icon: string,             // Icon identifier or URL
    color: string,            // Hex color
    visible: boolean,
    locked: boolean,          // Prevent accidental movement
    metadata: object,         // Custom data
    createdAt: timestamp,
    updatedAt: timestamp
}
```

### 2.3 Annotation Model
```javascript
Annotation = {
    id: string,
    type: 'path' | 'polygon' | 'circle' | 'rectangle' | 'text',
    points: [{worldX: number, worldY: number}], // World coordinates
    style: {
        stroke: string,
        fill: string,
        strokeWidth: number,
        opacity: number
    },
    label: string,
    visible: boolean,
    locked: boolean,
    layer: string,            // Layer ID
    metadata: object,
    createdAt: timestamp,
    updatedAt: timestamp
}
```

### 2.4 Layer Model
```javascript
Layer = {
    id: string,
    name: string,
    type: 'overlay' | 'base' | 'marker' | 'annotation',
    visible: boolean,
    opacity: number,
    zIndex: number,
    locked: boolean,
    data: object             // Layer-specific data
}
```

---

## 3. Rendering System

### 3.1 Renderer Architecture
```
MapRenderer
├── initialize()
├── loadMap(source)
├── render()
├── renderMap()
├── renderMarkers()
├── renderAnnotations()
├── renderMeasurements()
└── cleanup()
```

### 3.2 Canvas Rendering Strategy
- **Initial Load**: Convert SVG to canvas at 8x resolution (supports up to 20x zoom)
- **Dynamic Re-rendering**: Only re-render when zoom exceeds current resolution capacity
- **Resolution Threshold**: Re-render when `targetResolution > currentResolution * 1.1`
- **Memory Management**: Cap maximum resolution at 40x to prevent memory issues

### 3.3 Rendering Pipeline
1. **Pre-render**: Check if re-render is needed
2. **Background Render**: If needed, render map at higher resolution (async)
3. **Foreground Render**: Render markers, annotations, measurements (sync)
4. **Transform Apply**: Apply CSS transform for pan/zoom
5. **Post-render**: Update UI indicators, trigger callbacks

### 3.4 Coordinate System
- **World Coordinates**: Map's native coordinate system (0,0 to mapWidth, mapHeight)
  - **Markers and drawings use world coordinates** - Ensures they stay fixed to the map
  - Coordinates are stored in world space, not screen space
- **Screen Coordinates**: Viewport pixel coordinates
- **Conversion Functions**: 
  - `worldToScreen(worldX, worldY) → {screenX, screenY}` - Convert world coords to screen for rendering
  - `screenToWorld(screenX, screenY) → {worldX, worldY}` - Convert mouse position to world coords
  - `worldDistance(worldX1, worldY1, worldX2, worldY2) → number` - Calculate distance in world space
- **Zoom to Mouse**: When zooming, calculate world position under mouse, maintain that position during zoom

---

## 4. Interaction System

### 4.1 Event Flow
```
User Input → Event Handler → State Update → Render → UI Update
```

### 4.2 Interaction Modes
- **Pan Mode** (default): Click and drag to pan
- **Marker Mode**: Click to place marker
- **Annotation Mode**: Click to start drawing path/polygon
- **Measure Mode**: Click two points to measure distance
- **Select Mode**: Click to select markers/annotations

### 4.3 Input Handling
- **Mouse**: 
  - **Wheel zoom to mouse position** - Zoom centers on mouse cursor, not viewport center
  - Click-drag pan
  - Double-click reset
  - Click to place markers/drawings at mouse position
- **Touch**: 
  - Pinch zoom (centers on pinch center point)
  - Drag pan
  - Tap interactions
- **Keyboard**: Arrow keys pan, +/- zoom, Escape cancel

### 4.5 Zoom-to-Mouse Implementation
When zooming with mouse wheel:
1. Get mouse position in screen coordinates
2. Convert to world coordinates: `worldPos = screenToWorld(mouseX, mouseY)`
3. Apply zoom change to `mapScale`
4. Calculate new pan offset to keep `worldPos` under mouse cursor
5. Update viewport state
6. Re-render map

This ensures the point under the mouse cursor stays fixed during zoom, providing intuitive zoom behavior.

### 4.4 Interaction States
- **Idle**: No active interaction
- **Panning**: User is dragging to pan
- **Zooming**: User is zooming (wheel/pinch)
- **Drawing**: User is drawing annotation
- **Selecting**: User is selecting objects

---

## 5. Features & Functionality

### 5.1 Core Features
1. **Map Loading**
   - Load SVG files
   - **Convert SVG to Canvas** - Convert SVG to high-resolution canvas on load
   - Load image files (PNG, JPG) as fallback
   - Support for tile-based maps (future)
   - **Center map on load** - Automatically fit and center map in viewport
   - Error handling for missing files

2. **Zoom & Pan**
   - **Zoom to mouse position** - Zoom centers on mouse cursor, not viewport center
   - Smooth zoom with mouse wheel
   - Pinch-to-zoom on touch devices (centers on pinch center)
   - Pan with click-drag
   - Keyboard controls
   - Zoom limits (min/max)
   - Pan bounds (prevent panning outside map)

3. **High-Resolution Rendering**
   - Dynamic canvas resolution based on zoom
   - Smooth quality at all zoom levels
   - Performance optimization (throttling, debouncing)

### 5.2 Marker System
1. **Marker Management**
   - **Place markers at mouse position** - Click to place marker at cursor location
   - **Fixed to world coordinates** - Markers remain fixed to map coordinates during zoom/pan
   - Edit marker properties (name, category, description/notes)
   - **Delete markers** - Remove markers from map
   - Move markers (when not locked)
   - Lock/unlock markers

2. **Marker Display**
   - **Color coding** - Each marker can have custom color
   - **Various icons** - Support for different icon types (city, dungeon, landmark, custom)
   - Render markers as icons/circles
   - Show labels (toggleable)
   - Category-based styling
   - Hover tooltips
   - Click to view details

3. **Marker Notes**
   - **Add notes/description** - Each marker has a description field for notes
   - Rich text support (optional)
   - Notes visible in marker details modal

4. **Marker Filtering**
   - **Search markers** - Search by name, description, category
   - Filter by category
   - Show/hide markers
   - Group markers

4. **Marker Sidebar**
   - List all markers
   - Search/filter interface
   - Click to center on marker
   - Edit/delete from sidebar

### 5.3 Annotation System
1. **Drawing Tools**
   - **Place drawings at mouse position** - Draw annotations starting from cursor location
   - **Fixed to world coordinates** - Drawings remain fixed to map coordinates during zoom/pan
   - Freehand path drawing
   - Polygon drawing
   - Circle drawing
   - Rectangle drawing
   - Text annotations

2. **Annotation Management**
   - Edit annotations (move points, change style)
   - **Delete annotations** - Remove drawings from map
   - Lock/unlock annotations
   - Layer assignment

3. **Annotation Styling**
   - Stroke color
   - Fill color
   - Stroke width
   - Opacity
   - Line style (solid, dashed, dotted)

### 5.4 Layer System
1. **Layer Management**
   - Multiple overlay layers
   - Show/hide layers
   - Adjust layer opacity
   - Reorder layers (z-index)
   - Lock layers

2. **Layer Types**
   - Base map layer
   - Marker layer
   - Annotation layer
   - Custom overlay layers

### 5.5 Measurement System
1. **Distance Measurement**
   - Click two points to measure distance
   - Display distance in world units
   - Show measurement line
   - Multiple measurements

2. **Area Measurement**
   - Click points to create polygon
   - Calculate area
   - Display area in world units

### 5.6 UI Controls
1. **Toolbar**
   - Reset view button
   - Zoom in/out buttons
   - Fit to viewport button
   - Toggle labels button
   - Undo/Redo buttons

2. **Mode Buttons**
   - Pan mode
   - Add marker mode
   - Draw annotation mode
   - Measure mode
   - Select mode

3. **Sidebar**
   - Marker list
   - Search/filter
   - Category filter
   - Annotation list
   - Layer controls

4. **Status Bar**
   - Current zoom level
   - World coordinates (mouse position)
   - Selected object info
   - Performance metrics (debug mode)

---

## 6. State Management

### 6.1 State Structure
- **Single Source of Truth**: All state in `MapState` object
- **Immutable Updates**: Use Object.assign or spread operator
- **State History**: Undo/redo stack

### 6.2 State Updates
```javascript
// Pattern for state updates
function updateState(updates) {
    const oldState = currentState;
    currentState = { ...currentState, ...updates };
    notifyStateChange(oldState, currentState);
    render();
}
```

### 6.3 State Persistence
- **Firebase**: Real-time sync for markers/annotations
- **LocalStorage**: Cache map state, preferences
- **Auto-save**: Periodic saves to prevent data loss

### 6.4 Undo/Redo System
- **Action History**: Stack of state snapshots
- **Undo**: Restore previous state
- **Redo**: Restore next state
- **History Limit**: Max 50 actions

---

## 7. Performance Considerations

### 7.1 Rendering Optimization
- **RequestAnimationFrame**: Use for smooth animations
- **Throttling**: Throttle transform updates during pan/zoom
- **Debouncing**: Debounce expensive operations (re-rendering)
- **Lazy Loading**: Load map data on demand

### 7.2 Memory Management
- **Canvas Resolution Cap**: Max 40x to prevent memory issues
- **Cleanup**: Revoke blob URLs, clear unused canvases
- **Garbage Collection**: Remove unused markers/annotations from memory

### 7.3 Event Optimization
- **Passive Listeners**: Use passive event listeners where possible
- **Event Delegation**: Delegate events to parent elements
- **Throttle/Debounce**: Throttle scroll, debounce resize

### 7.4 Performance Monitoring
- **FPS Counter**: Track frame rate
- **Render Time**: Measure render duration
- **Memory Usage**: Monitor memory consumption (debug mode)

---

## 8. Error Handling

### 8.1 Error Types
1. **Map Loading Errors**
   - File not found
   - Invalid file format
   - Network errors
   - Parse errors

2. **Rendering Errors**
   - Canvas context errors
   - Image loading errors
   - Memory errors

3. **Interaction Errors**
   - Invalid coordinates
   - State corruption
   - Event handler errors

### 8.2 Error Recovery
- **Graceful Degradation**: Fallback to simpler rendering
- **User Feedback**: Show error messages
- **Retry Logic**: Allow retry for failed operations
- **Logging**: Log errors for debugging

### 8.3 Validation
- **Input Validation**: Validate all user inputs
- **State Validation**: Validate state before rendering
- **Coordinate Validation**: Ensure coordinates are within bounds

---

## 9. Extensibility Points

### 9.1 Plugin System
- **Plugin Interface**: Standard interface for plugins
- **Event Hooks**: Hooks for plugin integration
- **Custom Tools**: Allow custom interaction modes
- **Custom Renderers**: Allow custom rendering logic

### 9.2 Customization
- **Themes**: Support for different color schemes
- **Icons**: Customizable marker icons
- **Styles**: Customizable annotation styles
- **Layouts**: Customizable UI layouts

### 9.3 API Surface
- **Public API**: Clean API for external integration
- **Event System**: Publish/subscribe event system
- **State Access**: Read-only state access
- **Action Dispatchers**: Functions to trigger actions

---

## 10. File Structure

### 10.1 Code Organization
```
worldMap/
├── core/
│   ├── MapRenderer.js
│   ├── MapController.js
│   ├── MapState.js
│   └── CoordinateSystem.js
├── features/
│   ├── MarkerSystem.js
│   ├── AnnotationSystem.js
│   ├── LayerSystem.js
│   └── MeasurementSystem.js
├── data/
│   ├── MapDataManager.js
│   ├── FirebaseSync.js
│   └── LocalStorage.js
├── ui/
│   ├── ControlPanel.js
│   ├── Sidebar.js
│   └── Toolbar.js
├── utils/
│   ├── EventDispatcher.js
│   ├── StateManager.js
│   └── PerformanceMonitor.js
└── WorldMapModule.js (main entry point)
```

### 10.2 HTML Structure
```html
<div id="worldMapTab" class="tab-content">
    <!-- Control Panel -->
    <div class="map-controls-panel">
        <!-- Toolbar buttons -->
    </div>
    
    <!-- Main Map Area -->
    <div class="map-main-area">
        <div class="map-content">
            <div id="mapContainer">
                <div id="mapWrapper">
                    <!-- Map Canvas/Container -->
                    <canvas id="worldMapCanvas"></canvas>
                    <!-- Overlay SVG for markers/annotations -->
                    <svg id="mapOverlay"></svg>
                </div>
            </div>
        </div>
        
        <!-- Sidebar -->
        <div id="mapSidebar">
            <!-- Marker list, filters, etc. -->
        </div>
    </div>
</div>
```

---

## 11. Implementation Phases

### Phase 1: Core Foundation
- [ ] MapState structure
- [ ] MapRenderer (basic canvas rendering)
- [ ] MapController (basic pan/zoom)
- [ ] Coordinate system
- [ ] Basic UI structure

### Phase 2: Map Loading
- [ ] SVG loading and conversion
- [ ] Image loading
- [ ] Error handling
- [ ] Loading indicators

### Phase 3: High-Resolution Rendering
- [ ] Dynamic resolution system
- [ ] Re-rendering logic
- [ ] Performance optimization

### Phase 4: Marker System
- [ ] Marker data model
- [ ] Marker rendering
- [ ] Marker interaction
- [ ] Marker sidebar

### Phase 5: Annotation System
- [ ] Annotation data model
- [ ] Drawing tools
- [ ] Annotation rendering
- [ ] Annotation editing

### Phase 6: Advanced Features
- [ ] Layer system
- [ ] Measurement system
- [ ] Undo/redo
- [ ] Search/filter

### Phase 7: Polish & Optimization
- [ ] Performance tuning
- [ ] Error handling improvements
- [ ] UI/UX refinements
- [ ] Documentation

---

## 12. Testing Strategy

### 12.1 Unit Tests
- State management functions
- Coordinate conversion functions
- Rendering calculations
- Utility functions

### 12.2 Integration Tests
- Map loading workflow
- Marker creation workflow
- Annotation drawing workflow
- State persistence

### 12.3 Manual Testing Checklist
- [ ] Map loads correctly
- [ ] Zoom works smoothly
- [ ] Pan works correctly
- [ ] Markers can be added/edited/deleted
- [ ] Annotations can be drawn/edited/deleted
- [ ] Undo/redo works
- [ ] Search/filter works
- [ ] Mobile touch interactions work
- [ ] Performance is acceptable
- [ ] Error handling works

---

## 13. Best Practices

### 13.1 Code Quality
- **Modularity**: Keep functions small and focused
- **Documentation**: Comment complex logic
- **Naming**: Use descriptive variable/function names
- **Consistency**: Follow consistent patterns

### 13.2 Error Prevention
- **Type Checking**: Validate inputs
- **Bounds Checking**: Check coordinate bounds
- **Null Checks**: Check for null/undefined
- **Defensive Programming**: Assume inputs may be invalid

### 13.3 Performance
- **Avoid Premature Optimization**: Profile first, optimize second
- **Batch Operations**: Batch DOM updates
- **Use Efficient Algorithms**: Choose appropriate data structures
- **Monitor Performance**: Track performance metrics

### 13.4 Maintainability
- **Separation of Concerns**: Keep rendering, logic, and data separate
- **Single Responsibility**: Each function should do one thing
- **DRY Principle**: Don't repeat yourself
- **Clear Abstractions**: Use clear, well-defined interfaces

---

## 14. Future Enhancements

### 14.1 Potential Features
- Tile-based map support (for very large maps)
- Fog of war system
- Multiple map support (switch between maps)
- Export/import functionality
- Print functionality
- Custom coordinate systems
- Grid overlay
- Compass/rotation
- Mini-map
- Bookmark system (save view positions)

### 14.2 Technical Improvements
- WebGL rendering for better performance
- Web Workers for background processing
- Service Worker for offline support
- IndexedDB for large data storage
- WebAssembly for performance-critical operations

---

## Conclusion

This architecture provides a solid foundation for a world map tab that is:
- **Modular**: Easy to modify individual components
- **Extensible**: Easy to add new features
- **Maintainable**: Clear separation of concerns
- **Performant**: Optimized for smooth interactions
- **Robust**: Comprehensive error handling
- **User-Friendly**: Intuitive interface and interactions

The separation of rendering, state management, and interaction logic ensures that changes to one area won't break others, minimizing bugs and making the codebase easier to work with.
