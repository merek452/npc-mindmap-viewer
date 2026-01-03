#!/usr/bin/env python3
"""
Item Validator and Formatter
Validates and formats D&D items for JavaScript generation using JSON-first approach
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple


class ItemValidator:
    """Validates and formats items for JavaScript generation"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def clean_5etools_syntax(self, text: str) -> str:
        """Clean 5etools syntax markers from text"""
        if not isinstance(text, str):
            return str(text) if text is not None else ""
        
        # Remove all {@...} markers
        text = re.sub(r'\{@[^}]+\}', '', text)
        
        # Remove |Source} and |Source| patterns
        text = re.sub(r'\|\w+\}', '', text)
        text = re.sub(r'\|\w+\|', '', text)
        
        # Fix patterns like "text}spell" -> "text spell"
        text = re.sub(r'\}\s*([a-z])', r' \1', text)
        text = re.sub(r'\}([a-z])', r' \1', text)
        
        # Remove stray } characters
        text = re.sub(r'([^"])\}[^",}]+"', r'\1"', text)
        
        # Fix "Proficiency})" -> "Proficiency Bonus)"
        text = text.replace('Proficiency})', 'Proficiency Bonus)')
        text = text.replace('})', '')
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def escape_js_string(self, text: str) -> str:
        """Escape string for safe inclusion in JavaScript string literal"""
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        
        # Escape backslashes first
        text = text.replace('\\', '\\\\')
        # Escape double quotes
        text = text.replace('"', '\\"')
        # Remove newlines and carriage returns
        text = text.replace('\n', ' ').replace('\r', ' ')
        # Truncate very long descriptions
        if len(text) > 2000:
            text = text[:1997] + "..."
        
        return text
    
    def clean_item_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize item data"""
        cleaned = {}
        
        # Required fields
        if 'name' not in item:
            self.errors.append(f"Item missing 'name' field: {item}")
            return None
        
        cleaned['name'] = str(item['name']).strip()
        
        # Optional fields with cleaning
        for key in ['category', 'type', 'cost', 'source', 'rarity', 'damage', 
                    'damageType', 'range', 'ac', 'armorType', 'versatile']:
            if key in item and item[key]:
                value = item[key]
                if isinstance(value, str):
                    value = self.clean_5etools_syntax(value)
                cleaned[key] = value
        
        # Weight (can be number or string)
        if 'weight' in item:
            cleaned['weight'] = item['weight']
        
        # Properties (array)
        if 'properties' in item:
            props = item['properties']
            if isinstance(props, list):
                # Clean each property string
                cleaned['properties'] = [self.clean_5etools_syntax(str(p)) for p in props if p]
            elif isinstance(props, str):
                # Try to parse as comma-separated
                cleaned['properties'] = [self.clean_5etools_syntax(p.strip()) 
                                        for p in props.split(',') if p.strip()]
        
        # Attunement (boolean)
        if 'attunement' in item:
            cleaned['attunement'] = bool(item['attunement']) if item['attunement'] else False
        
        # Stealth (boolean)
        if 'stealth' in item:
            cleaned['stealth'] = bool(item['stealth']) if item['stealth'] else False
        
        # Description (needs special cleaning)
        if 'description' in item and item['description']:
            desc = str(item['description'])
            # Clean 5etools syntax first
            desc = self.clean_5etools_syntax(desc)
            
            # Remove duplicate text patterns - look for repeated closing patterns
            # Pattern: "...text"} more text"} more text"
            # Find the first complete description (ends with ", source:)
            source_match = re.search(r'",\s*source:\s*"', desc)
            if source_match:
                # Take only up to the first source marker
                desc = desc[:source_match.start() + 1]  # Keep the closing quote
            
            # Remove duplicate closing patterns like "} or have" or "} action"
            desc = re.sub(r'\}\s*(or|action|spell|check|for|from)\s+[^"]*",\s*source:', r'", source:', desc)
            
            # Remove any remaining duplicate text after closing quote
            # Pattern: "...text", source: "X"} more text", source: "X"
            desc = re.sub(r'",\s*source:\s*"[^"]+"\s*\}\s*[^"]*",\s*source:', r'", source:', desc)
            
            # Final cleanup - remove any stray } patterns
            desc = re.sub(r'\}\s*([a-z])', r' \1', desc)
            desc = desc.replace('})', '')
            
            cleaned['description'] = desc
        
        return cleaned
    
    def validate_item(self, item: Dict[str, Any], item_name: Optional[str] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate an item by attempting to serialize it as JSON"""
        if item_name is None:
            item_name = item.get('name', 'Unknown')
        
        # Clean the item first
        cleaned_item = self.clean_item_data(item)
        if cleaned_item is None:
            return False, None
        
        # Try to serialize as JSON to validate structure
        try:
            json_str = json.dumps(cleaned_item, ensure_ascii=False)
            # Parse it back to ensure it's valid
            parsed = json.loads(json_str)
            return True, parsed
        except (TypeError, ValueError) as e:
            self.errors.append(f"Item '{item_name}' failed JSON validation: {e}")
            return False, None
    
    def format_item_as_js(self, item: Dict[str, Any]) -> str:
        """Format a validated item dictionary as JavaScript object literal"""
        parts = []
        
        # Order properties consistently
        property_order = ['name', 'category', 'weight', 'cost', 'type', 'source', 
                         'damage', 'damageType', 'properties', 'range', 'versatile',
                         'ac', 'armorType', 'stealth', 'rarity', 'attunement', 'description']
        
        # Add properties in order
        for key in property_order:
            if key in item:
                value = item[key]
                if isinstance(value, str):
                    # Escape and quote strings
                    escaped = self.escape_js_string(value)
                    parts.append(f'{key}: "{escaped}"')
                elif isinstance(value, bool):
                    parts.append(f'{key}: {str(value).lower()}')
                elif isinstance(value, (int, float)):
                    parts.append(f'{key}: {value}')
                elif isinstance(value, list):
                    # Format array
                    if all(isinstance(v, str) for v in value):
                        escaped_items = [f'"{self.escape_js_string(v)}"' for v in value]
                        parts.append(f'{key}: [{", ".join(escaped_items)}]')
                    else:
                        # Mixed types - convert to strings
                        escaped_items = [f'"{self.escape_js_string(str(v))}"' for v in value]
                        parts.append(f'{key}: [{", ".join(escaped_items)}]')
                else:
                    # Fallback: convert to string
                    escaped = self.escape_js_string(str(value))
                    parts.append(f'{key}: "{escaped}"')
        
        # Add any remaining properties not in the order list
        for key, value in item.items():
            if key not in property_order:
                if isinstance(value, str):
                    escaped = self.escape_js_string(value)
                    parts.append(f'{key}: "{escaped}"')
                elif isinstance(value, bool):
                    parts.append(f'{key}: {str(value).lower()}')
                elif isinstance(value, (int, float)):
                    parts.append(f'{key}: {value}')
                elif isinstance(value, list):
                    escaped_items = [f'"{self.escape_js_string(str(v))}"' for v in value]
                    parts.append(f'{key}: [{", ".join(escaped_items)}]')
                else:
                    escaped = self.escape_js_string(str(value))
                    parts.append(f'{key}: "{escaped}"')
        
        return '{' + ', '.join(parts) + '}'
    
    def validate_and_format_items(self, items: List[Dict[str, Any]]) -> Tuple[List[str], List[str], List[str]]:
        """
        Validate all items and format them as JavaScript.
        Returns: (formatted_items, errors, warnings)
        """
        formatted_items = []
        self.errors = []
        self.warnings = []
        
        for idx, item in enumerate(items):
            item_name = item.get('name', f'Item_{idx}')
            
            # Validate item
            is_valid, cleaned_item = self.validate_item(item, item_name)
            
            if not is_valid or cleaned_item is None:
                self.warnings.append(f"Skipping invalid item: {item_name}")
                continue
            
            # Format as JavaScript
            try:
                js_format = self.format_item_as_js(cleaned_item)
                formatted_items.append(js_format)
            except Exception as e:
                self.errors.append(f"Failed to format item '{item_name}': {e}")
                continue
        
        return formatted_items, self.errors, self.warnings
    
    def validate_js_syntax(self, js_code: str) -> Tuple[bool, Optional[str]]:
        """Validate JavaScript syntax using a simple approach"""
        # Basic validation: check for unmatched braces, quotes, etc.
        try:
            # Count braces
            open_braces = js_code.count('{')
            close_braces = js_code.count('}')
            if open_braces != close_braces:
                return False, f"Unmatched braces: {open_braces} open, {close_braces} close"
            
            # Check for common syntax errors
            if re.search(r',\s*,', js_code):  # Double commas
                return False, "Found double commas"
            
            if re.search(r',\s*}', js_code):  # Trailing comma before }
                return False, "Found trailing comma before closing brace"
            
            # Check for unclosed strings (simple check)
            in_string = False
            escape_next = False
            for char in js_code:
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"':
                    in_string = not in_string
            
            if in_string:
                return False, "Unclosed string literal"
            
            return True, None
        except Exception as e:
            return False, f"Validation error: {e}"

