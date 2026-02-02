# Mobile Debugging Guide

## Issues to Test

1. **Scrolling through item list**
   - Open the Inventory tab
   - Try to scroll through the item lookup list
   - Should scroll smoothly without triggering drag

2. **Dragging items**
   - Touch and hold an item in the lookup list
   - Move finger horizontally or significantly (>20px)
   - Release over a player inventory or bag of holding
   - Item should be added to the container

3. **Tapping items**
   - Quick tap on an item (<300ms, <10px movement)
   - Should show item description popup

## Debug Steps

1. Open browser DevTools on mobile (or use Chrome DevTools remote debugging)
2. Check console for errors
3. Test touch events:
   - `touchstart` - should not prevent default (allows scrolling)
   - `touchmove` - should only prevent default if horizontal drag
   - `touchend` - should handle tap vs drag vs scroll

## Known Issues

- Touch events might conflict with native scrolling
- `touch-action: pan-y` should allow vertical scrolling
- `-webkit-overflow-scrolling: touch` enables smooth iOS scrolling

## Testing Checklist

- [ ] Can scroll item list vertically
- [ ] Can drag items horizontally
- [ ] Quick tap shows description
- [ ] Drag and drop works to containers
- [ ] No console errors

