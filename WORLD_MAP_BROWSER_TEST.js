// World Map Module - Browser Console Test Script
// Copy and paste this into the browser console (F12) after opening npc_mindmap_viewer.html

console.log('🧪 Starting World Map Module Tests...\n');

// Test 1: Check if WorldMapModule is defined
console.log('Test 1: Module Definition');
if (typeof WorldMapModule !== 'undefined') {
    console.log('✅ WorldMapModule is defined');
    console.log('   - init:', typeof WorldMapModule.init);
    console.log('   - editMarkerById:', typeof WorldMapModule.editMarkerById);
    console.log('   - deleteMarkerById:', typeof WorldMapModule.deleteMarkerById);
    console.log('   - zoomToMarkerById:', typeof WorldMapModule.zoomToMarkerById);
} else {
    console.error('❌ WorldMapModule is NOT defined');
}

// Test 2: Check if DOM elements exist
console.log('\nTest 2: DOM Elements');
const elements = {
    'worldMapTab': document.getElementById('worldMapTab'),
    'worldMapContainer': document.getElementById('worldMapContainer'),
    'worldMapWrapper': document.getElementById('worldMapWrapper'),
    'worldMapCanvas': document.getElementById('worldMapCanvas'),
    'worldMapOverlay': document.getElementById('worldMapOverlay'),
    'worldMapResetBtn': document.getElementById('worldMapResetBtn'),
    'worldMapPanModeBtn': document.getElementById('worldMapPanModeBtn'),
    'worldMapMarkerModeBtn': document.getElementById('worldMapMarkerModeBtn'),
    'worldMapDrawModeBtn': document.getElementById('worldMapDrawModeBtn'),
    'worldMapZoomLevel': document.getElementById('worldMapZoomLevel'),
    'worldMapLocationList': document.getElementById('worldMapLocationList'),
    'worldMapMarkerSearchInput': document.getElementById('worldMapMarkerSearchInput'),
    'worldMapMarkerCategoryFilter': document.getElementById('worldMapMarkerCategoryFilter')
};

let allElementsExist = true;
for (const [name, element] of Object.entries(elements)) {
    if (element) {
        console.log(`✅ ${name} exists`);
    } else {
        console.error(`❌ ${name} is MISSING`);
        allElementsExist = false;
    }
}

// Test 3: Try to initialize the module
console.log('\nTest 3: Module Initialization');
if (typeof WorldMapModule !== 'undefined' && typeof WorldMapModule.init === 'function') {
    try {
        WorldMapModule.init();
        console.log('✅ WorldMapModule.init() called successfully');
        
        // Wait a bit and check if map loaded
        setTimeout(function() {
            const svgContainer = document.querySelector('#worldMapSvgContainer');
            const canvas = document.getElementById('worldMapCanvas');
            const hasMap = (svgContainer && svgContainer.innerHTML.trim() !== '') || 
                          (canvas && canvas.style.display !== 'none');
            
            if (hasMap) {
                console.log('✅ Map appears to be loaded');
            } else {
                console.warn('⚠️ Map may not be loaded - check PLACEHOLDER_SVG_CONTENT');
            }
        }, 500);
    } catch(e) {
        console.error('❌ Error initializing WorldMapModule:', e);
        console.error('   Stack:', e.stack);
    }
} else {
    console.error('❌ Cannot initialize - WorldMapModule.init is not a function');
}

// Test 4: Check Firebase functions
console.log('\nTest 4: Firebase Functions');
if (typeof loadFromFirebase === 'function') {
    console.log('✅ loadFromFirebase is defined');
} else {
    console.error('❌ loadFromFirebase is NOT defined');
}

if (typeof saveToFirebase === 'function') {
    console.log('✅ saveToFirebase is defined');
} else {
    console.error('❌ saveToFirebase is NOT defined');
}

// Test 5: Check if PLACEHOLDER_SVG_CONTENT exists
console.log('\nTest 5: Map Content');
if (typeof PLACEHOLDER_SVG_CONTENT !== 'undefined') {
    const contentLength = PLACEHOLDER_SVG_CONTENT ? PLACEHOLDER_SVG_CONTENT.length : 0;
    console.log(`✅ PLACEHOLDER_SVG_CONTENT exists (${contentLength} characters)`);
    if (contentLength === 0) {
        console.warn('⚠️ PLACEHOLDER_SVG_CONTENT is empty - map may not load');
    }
} else {
    console.error('❌ PLACEHOLDER_SVG_CONTENT is NOT defined');
}

// Test 6: Test tab switching
console.log('\nTest 6: Tab Switching');
if (typeof switchTab === 'function') {
    console.log('✅ switchTab function exists');
    try {
        // Try switching to worldMap tab
        switchTab('worldMap');
        console.log('✅ switchTab("worldMap") called');
        
        setTimeout(function() {
            const tab = document.getElementById('worldMapTab');
            if (tab && tab.style.display !== 'none') {
                console.log('✅ worldMapTab is visible');
            } else {
                console.error('❌ worldMapTab is not visible');
            }
        }, 100);
    } catch(e) {
        console.error('❌ Error switching to worldMap tab:', e);
    }
} else {
    console.error('❌ switchTab function is NOT defined');
}

// Test 7: Check for JavaScript errors
console.log('\nTest 7: JavaScript Errors');
const errors = [];
window.addEventListener('error', function(e) {
    errors.push(e);
    console.error('❌ JavaScript Error:', e.message, 'at', e.filename, ':', e.lineno);
});

setTimeout(function() {
    if (errors.length === 0) {
        console.log('✅ No JavaScript errors detected');
    } else {
        console.error(`❌ Found ${errors.length} JavaScript error(s)`);
    }
}, 1000);

console.log('\n🧪 Test script completed. Check results above.');
console.log('💡 To test manually:');
console.log('   1. Click "🌍 World Map (New)" tab');
console.log('   2. Try zooming (mouse wheel)');
console.log('   3. Try panning (click and drag)');
console.log('   4. Try adding a marker (click "📍 Add Marker" then click on map)');
console.log('   5. Try drawing (click "✏️ Draw" then click and drag on map)');
