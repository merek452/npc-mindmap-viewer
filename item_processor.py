#!/usr/bin/env python3
"""
Centralized Item Processor
All item processing (cleaning, escaping, validation) goes through this class.
This ensures consistency across all scripts that add or modify items.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from item_validator import ItemValidator


class ItemProcessor(ItemValidator):
    """
    Centralized processor for all D&D items.
    Extends ItemValidator with additional processing capabilities.
    """
    
    def __init__(self):
        super().__init__()
    
    def process_item(self, item: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Process a single item through the complete pipeline:
        1. Clean 5etools syntax
        2. Validate structure
        3. Return cleaned item or None with errors
        
        Returns: (success, cleaned_item, errors)
        """
        errors = []
        item_name = item.get('name', 'Unknown')
        
        # Validate and clean
        is_valid, cleaned_item = self.validate_item(item, item_name)
        
        if not is_valid or cleaned_item is None:
            errors.extend(self.errors)
            return False, None, errors
        
        # Additional validation checks
        if not cleaned_item.get('name'):
            errors.append(f"Item missing name: {item}")
            return False, None, errors
        
        # Ensure description doesn't have unescaped quotes
        if 'description' in cleaned_item:
            desc = cleaned_item['description']
            # Check for unescaped quotes (not preceded by backslash)
            if re.search(r'(?<!\\)"', desc):
                # This shouldn't happen after cleaning, but double-check
                cleaned_item['description'] = desc.replace('"', '\\"')
        
        return True, cleaned_item, errors
    
    def process_items(self, items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
        """
        Process multiple items through the complete pipeline.
        
        Returns: (processed_items, errors, warnings)
        """
        processed_items = []
        all_errors = []
        all_warnings = []
        
        for item in items:
            success, cleaned_item, errors = self.process_item(item)
            
            if success and cleaned_item:
                processed_items.append(cleaned_item)
            else:
                all_errors.extend(errors)
                all_warnings.append(f"Skipping invalid item: {item.get('name', 'Unknown')}")
        
        return processed_items, all_errors, all_warnings
    
    def format_items_for_js(self, items: List[Dict[str, Any]]) -> str:
        """
        Format a list of items as a JavaScript array string.
        Uses json.dumps for proper escaping, then converts to JS object literal format.
        """
        formatted_items = []
        
        for item in items:
            js_format = self.format_item_as_js(item)
            formatted_items.append(js_format)
        
        return '[\n            ' + ',\n            '.join(formatted_items) + '\n        ]'
    
    def load_items_from_json(self, json_file: Path) -> List[Dict[str, Any]]:
        """Load items from a JSON file"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'items' in data:
                return data['items']
            else:
                return []
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            self.errors.append(f"Failed to parse JSON file {json_file}: {e}")
            return []
    
    def save_items_to_json(self, items: List[Dict[str, Any]], json_file: Path):
        """Save items to a JSON file"""
        try:
            # Sort items by name for consistency
            sorted_items = sorted(items, key=lambda x: x.get('name', '').lower())
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(sorted_items, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.errors.append(f"Failed to save items to {json_file}: {e}")
            return False
    
    def merge_items(self, existing_items: List[Dict[str, Any]], 
                   new_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge new items into existing items, avoiding duplicates.
        If an item with the same name exists, the new item's properties are merged.
        """
        # Create a lookup by name (case-insensitive)
        item_map = {}
        for item in existing_items:
            name = item.get('name', '').lower()
            if name:
                item_map[name] = item
        
        # Process and merge new items
        for new_item in new_items:
            name = new_item.get('name', '').lower()
            if not name:
                continue
            
            # Process the new item
            success, cleaned_item, errors = self.process_item(new_item)
            if not success or not cleaned_item:
                continue
            
            if name in item_map:
                # Merge: update existing item with new properties
                existing = item_map[name]
                existing.update(cleaned_item)
            else:
                # Add new item
                item_map[name] = cleaned_item
        
        return list(item_map.values())


