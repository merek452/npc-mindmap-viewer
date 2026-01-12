#!/usr/bin/env python3
"""
NPC Relationship Mind Map Generator
Generates a visual mind map of NPC relationships from npc_relationships.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from item_processor import ItemProcessor

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False
    print("Warning: networkx and matplotlib not installed. Install with: pip install networkx matplotlib")
    print("Will generate text-based output instead.")


class NPCRelationshipMapper:
    def __init__(self, json_file: str):
        self.json_file = Path(json_file)
        self.data = self.load_data()
        self.graph = None
        self.items_json = Path(__file__).parent / "items.json"
        self.item_processor = ItemProcessor()
        
    def load_data(self) -> Dict:
        """Load NPC relationship data from JSON file"""
        if not self.json_file.exists():
            print(f"Error: {self.json_file} not found!")
            sys.exit(1)
            
        with open(self.json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def build_graph(self):
        """Build a NetworkX graph from the relationship data"""
        if not HAS_VISUALIZATION:
            return None
            
        self.graph = nx.Graph()
        npcs = self.data.get('npcs', {})
        
        # Add all NPCs as nodes
        for npc_id, npc_data in npcs.items():
            self.graph.add_node(npc_id, **npc_data)
        
        # Add relationships as edges
        for npc_id, npc_data in npcs.items():
            relationships = npc_data.get('relationships', {})
            for rel_type, targets in relationships.items():
                if isinstance(targets, list):
                    for target in targets:
                        if target in npcs:
                            self.graph.add_edge(npc_id, target, relationship=rel_type)
                elif isinstance(targets, str):
                    if targets in npcs:
                        self.graph.add_edge(npc_id, targets, relationship=rel_type)
        
        return self.graph
    
    def generate_text_map(self) -> str:
        """Generate a text-based relationship map"""
        output = []
        output.append("# NPC Relationship Mind Map\n")
        output.append("*Generated from npc_relationships.json*\n\n")
        
        npcs = self.data.get('npcs', {})
        
        # Group by faction
        factions = {}
        for npc_id, npc_data in npcs.items():
            faction = npc_data.get('faction', 'Unknown')
            if faction not in factions:
                factions[faction] = []
            factions[faction].append((npc_id, npc_data))
        
        output.append("## NPCs by Faction\n\n")
        for faction, npc_list in sorted(factions.items()):
            output.append(f"### {faction}\n\n")
            for npc_id, npc_data in npc_list:
                name = npc_data.get('name', npc_id)
                status = npc_data.get('status', 'unknown')
                location = npc_data.get('location', 'unknown')
                output.append(f"- **{name}** ({status}) - {location}\n")
            output.append("\n")
        
        # Relationship connections
        output.append("## Relationship Connections\n\n")
        for npc_id, npc_data in npcs.items():
            name = npc_data.get('name', npc_id)
            relationships = npc_data.get('relationships', {})
            if relationships:
                output.append(f"### {name}\n\n")
                for rel_type, targets in relationships.items():
                    if isinstance(targets, list):
                        target_list = ", ".join([f"**{t}**" for t in targets])
                    else:
                        target_list = f"**{targets}**"
                    output.append(f"- *{rel_type.replace('_', ' ').title()}*: {target_list}\n")
                output.append("\n")
        
        return "".join(output)
    
    def generate_visual_map(self, output_file: str = "npc_mindmap.png"):
        """Generate a visual mind map using NetworkX and Matplotlib"""
        if not HAS_VISUALIZATION:
            print("Visualization libraries not available. Generating text map instead.")
            return self.generate_text_map()
        
        self.build_graph()
        if self.graph is None:
            return
        
        # Create figure
        plt.figure(figsize=(20, 16))
        
        # Use spring layout for better node distribution
        pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)
        
        # Color nodes by faction
        faction_colors = {
            'Light Ring': '#FFD700',
            'The Gilded Cage': '#8B0000',
            'Feywild': '#228B22',
            'Cinderfang Tribe': '#FF4500',
            'Underclasp': '#2F4F4F',
            "Asmodeus's Court": '#DC143C',
            "Dispater's Court": '#4B0082',
            'Fey Palace Archive': '#9370DB',
            'Spy Network': '#4682B4',
            'Independent': '#808080',
            'Civilians': '#D3D3D3',
            'Hag Coven': '#000000'
        }
        
        npcs = self.data.get('npcs', {})
        node_colors = []
        for node in self.graph.nodes():
            faction = npcs[node].get('faction', 'Unknown')
            node_colors.append(faction_colors.get(faction, '#CCCCCC'))
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, 
                             node_color=node_colors,
                             node_size=2000,
                             alpha=0.9)
        
        # Draw edges with different styles for different relationship types
        edge_colors = []
        for edge in self.graph.edges(data=True):
            rel_type = edge[2].get('relationship', 'neutral')
            if 'enemy' in rel_type or 'feeds_on' in rel_type:
                edge_colors.append('#FF0000')  # Red for negative
            elif 'ally' in rel_type or 'works_with' in rel_type:
                edge_colors.append('#00FF00')  # Green for positive
            elif 'controls' in rel_type or 'serves' in rel_type:
                edge_colors.append('#FFA500')  # Orange for hierarchical
            else:
                edge_colors.append('#808080')  # Gray for neutral
        
        nx.draw_networkx_edges(self.graph, pos,
                              edge_color=edge_colors,
                              width=2,
                              alpha=0.6)
        
        # Draw labels
        labels = {node: npcs[node].get('name', node)[:20] for node in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8, font_weight='bold')
        
        # Create legend
        legend_elements = [mpatches.Patch(color=color, label=faction) 
                          for faction, color in faction_colors.items()]
        plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        
        plt.title("NPC Relationship Mind Map - Genia Campaign", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Visual mind map saved to {output_file}")
    
    def export_to_markdown(self, output_file: str = "NPC_RELATIONSHIP_MINDMAP.md"):
        """Export relationship map to markdown file"""
        content = self.generate_text_map()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Markdown mind map saved to {output_file}")
    
    def load_items_for_html(self) -> str:
        """Load items from items.json and format as JavaScript array"""
        items = self.item_processor.load_items_from_json(self.items_json)
        if not items:
            print(f"Warning: No items loaded from {self.items_json}")
            return "[]"
        
        # Process items to ensure they're clean
        processed_items, errors, warnings = self.item_processor.process_items(items)
        
        if errors:
            print(f"Errors processing items: {len(errors)}")
            for error in errors[:5]:
                print(f"  {error}")
        
        if warnings:
            print(f"Warnings: {len(warnings)}")
        
        # Format as JavaScript array
        js_array = self.item_processor.format_items_for_js(processed_items)
        return js_array
    
    def generate_html_viewer(self, output_file: str = "npc_mindmap_viewer.html"):
        """Generate an interactive HTML viewer for players"""
        npcs = self.data.get('npcs', {})
        relationship_types = self.data.get('relationship_types', [])
        factions = self.data.get('factions', [])
        
        # Load SVG map content to embed directly
        svg_map_content = ""
        svg_map_path = Path(__file__).parent / "Images" / "Gienia World Map.svg"
        if svg_map_path.exists():
            try:
                with open(svg_map_path, 'r', encoding='utf-8') as f:
                    svg_map_content = f.read()
                    # Escape for JavaScript template literal
                    svg_map_content = svg_map_content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
            except Exception as e:
                print(f"Warning: Could not load SVG map: {e}")
                svg_map_content = ""
        
        # Faction colors
        faction_colors = {
            'Light Ring': '#FFD700',
            'The Gilded Cage': '#8B0000',
            'Feywild': '#228B22',
            'Cinderfang Tribe': '#FF4500',
            'Underclasp': '#2F4F4F',
            "Asmodeus's Court": '#DC143C',
            "Dispater's Court": '#4B0082',
            'Fey Palace Archive': '#9370DB',
            'Spy Network': '#4682B4',
            'Independent': '#808080',
            'Civilians': '#D3D3D3',
            'Hag Coven': '#000000'
        }
        
        # Load items from JSON
        print("Loading items from items.json...")
        dnd_items_js = self.load_items_for_html()
        print(f"Loaded items and formatted for JavaScript")
        
        # Prepare SVG content for JavaScript (escape and format)
        svg_js_content = repr(svg_map_content) if svg_map_content else "''"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NPC Relationship Mind Map - Genia Campaign</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            background-attachment: fixed;
            color: #fff;
            padding: 30px 20px;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        
        /* Mobile and Touch Optimizations */
        * {{
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
        }}
        
        body {{
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            overflow-x: hidden;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 15px 10px;
            }}
            
            .container {{
                max-width: 100%;
                padding: 0 5px;
                width: 100%;
                box-sizing: border-box;
            }}
            
            h1 {{
                font-size: 1.8em !important;
                margin-bottom: 20px !important;
                padding: 0 5px;
                width: 100%;
                box-sizing: border-box;
            }}
            
            .controls {{
                padding: 15px !important;
                margin-bottom: 15px !important;
            }}
            
            .filter-group {{
                flex-direction: column;
                gap: 12px !important;
                align-items: stretch;
            }}
            
            .filter-group label {{
                font-size: 0.95em;
                margin-bottom: 4px;
            }}
            
            select, input {{
                width: 100%;
                padding: 10px 14px;
                font-size: 16px; /* Prevents zoom on iOS */
            }}
            
            #npcContainer {{
                padding: 0 5px !important;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            
            .npc-grid {{
                grid-template-columns: 1fr !important;
                gap: 12px !important;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            
            .npc-card {{
                padding: 12px !important;
                margin: 0;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            
            .npc-header {{
                flex-direction: column;
                gap: 10px;
            }}
            
            .npc-portrait-container {{
                width: 100%;
                max-width: 150px;
                margin: 0 auto;
            }}
            
            .npc-info {{
                text-align: center;
            }}
            
            .npc-name {{
                font-size: 1.2em !important;
            }}
            
            .npc-location {{
                font-size: 0.9em !important;
            }}
            
            .tabs {{
                flex-wrap: wrap;
                gap: 5px;
                margin-bottom: 15px;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                width: 100%;
                padding: 0 5px;
                box-sizing: border-box;
            }}
            
            .tab {{
                padding: 12px 20px !important;
                font-size: 1em !important;
                flex: 1 1 auto;
                min-width: fit-content;
                white-space: nowrap;
            }}
            
            /* Mobile inventory improvements */
            #inventoryTab .container > div[style*="grid-template-columns: 300px 1fr"] {{
                grid-template-columns: 1fr !important;
                width: 100% !important;
                max-width: 100% !important;
                padding: 0 5px !important;
                box-sizing: border-box !important;
            }}
            
            #inventoryTab .container > div[style*="grid-template-columns: 300px 1fr"] > div {{
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            
            #playerInventories {{
                grid-template-columns: 1fr !important;
                max-width: 100% !important;
                width: 100% !important;
                overflow-x: hidden !important;
                padding: 0 5px !important;
                box-sizing: border-box !important;
            }}
            
            #itemLookup {{
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            
            .player-inventory {{
                max-width: 100% !important;
                overflow-x: hidden !important;
                box-sizing: border-box !important;
            }}
            
            .inventory-container {{
                max-width: 100% !important;
                overflow-x: hidden !important;
                box-sizing: border-box !important;
            }}
            
            .inventory-item {{
                font-size: 0.9em !important;
                padding: 8px !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
                overflow-x: hidden !important;
            }}
            
            .inventory-item button {{
                padding: 6px 12px !important;
                min-width: 44px !important;
                min-height: 44px !important;
                font-size: 0.85em !important;
                min-height: 36px; /* Better touch target */
            }}
            
            #itemLookup {{
                max-height: 300px !important;
                -webkit-overflow-scrolling: touch !important;
                touch-action: pan-y !important;
            }}
            
            /* Mind map mobile optimizations */
            #mindmapContainer {{
                height: 70vh !important;
                min-height: 400px !important;
                border-width: 2px;
            }}
            
            .mindmap-legend {{
                position: relative !important;
                top: auto !important;
                right: auto !important;
                margin-bottom: 15px;
                font-size: 0.9em;
                padding: 15px;
            }}
            
            /* Editor mobile */
            .editor-container {{
                flex-direction: column;
                gap: 15px;
            }}
            
            .editor-sidebar {{
                flex: 1 1 auto;
                max-height: 300px;
                overflow-y: auto;
            }}
            
            .editor-main {{
                flex: 1 1 auto;
                padding: 20px !important;
            }}
            
            .form-group {{
                margin-bottom: 15px;
            }}
            
            .form-group label {{
                font-size: 0.95em;
            }}
            
            .form-group input,
            .form-group select,
            .form-group textarea {{
                width: 100%;
                font-size: 16px; /* Prevents zoom on iOS */
            }}
            
            button {{
                min-height: 44px; /* iOS recommended touch target */
                min-width: 44px;
                padding: 12px 20px;
            }}
        }}
        
        @media (max-width: 480px) {{
            h1 {{
                font-size: 1.5em !important;
                letter-spacing: 1px;
            }}
            
            .controls {{
                padding: 12px !important;
            }}
            
            .filter-group {{
                gap: 10px !important;
            }}
            
            .npc-card {{
                padding: 10px !important;
            }}
            
            .npc-badges {{
                flex-wrap: wrap;
                gap: 5px;
            }}
            
            #playerInventories {{
                padding: 0 5px !important;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            
            .player-inventory {{
                margin-bottom: 10px !important;
                padding: 6px !important;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            
            .inventory-container {{
                max-height: 200px !important;
                min-height: 80px !important;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            
            #itemLookup {{
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            
            .inventory-item {{
                padding: 6px !important;
                font-size: 0.85em !important;
                width: 100% !important;
                max-width: 100% !important;
                box-sizing: border-box !important;
            }}
            
            .inventory-item button {{
                min-width: 44px !important;
                min-height: 44px !important;
                padding: 8px !important;
                font-size: 0.9em !important;
            }}
            
            .badge {{
                font-size: 0.75em !important;
                padding: 4px 8px !important;
            }}
            
            .inventory-item {{
                flex-direction: column !important;
                align-items: flex-start !important;
            }}
            
            .inventory-item > div:last-child {{
                margin-top: 8px;
                width: 100%;
                justify-content: flex-end;
            }}
            
            #mindmapContainer {{
                height: 60vh !important;
                min-height: 350px !important;
            }}
            
            .tab {{
                padding: 10px 15px !important;
                font-size: 0.9em !important;
            }}
        }}
        
        /* Touch-friendly improvements */
        @media (hover: none) and (pointer: coarse) {{
            .npc-card {{
                cursor: default;
            }}
            
            .tab:hover {{
                background: rgba(255,255,255,0.1);
            }}
            
            button:active {{
                transform: scale(0.98);
            }}
            
            .npc-card:active {{
                transform: scale(0.99);
            }}
        }}
        
        /* iOS Safari specific fixes */
        @supports (-webkit-touch-callout: none) {{
            body {{
                -webkit-overflow-scrolling: touch;
            }}
            
            select, input, textarea {{
                font-size: 16px; /* Prevents zoom on focus */
            }}
        }}
        
        h1 {{
            text-align: center;
            margin-bottom: 40px;
            font-size: 3.5em;
            font-weight: 700;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.7), 0 0 20px rgba(255,255,255,0.3);
            letter-spacing: 2px;
        }}
        
        .controls {{
            background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            backdrop-filter: blur(15px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            border: 2px solid rgba(255,255,255,0.3);
        }}
        
        .filter-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            align-items: center;
        }}
        
        .filter-group label {{
            font-weight: 600;
            font-size: 1.1em;
            margin-right: 8px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}
        
        select, input {{
            padding: 12px 18px;
            border-radius: 8px;
            border: 2px solid rgba(255,255,255,0.4);
            background: rgba(255,255,255,0.25);
            color: #fff;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s;
        }}
        
        select:hover, input:hover {{
            background: rgba(255,255,255,0.35);
            border-color: rgba(255,255,255,0.6);
        }}
        
        select:focus, input:focus {{
            outline: none;
            background: rgba(255,255,255,0.4);
            border-color: #FFD700;
            box-shadow: 0 0 15px rgba(255,215,0,0.5);
        }}
        
        select option {{
            background: #1a2f5a;
            color: #fff;
            padding: 10px;
            font-size: 16px;
        }}
        
        .npc-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 12px;
            margin-top: 20px;
        }}
        
        .npc-card {{
            background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
            border-radius: 12px;
            padding: 14px;
            backdrop-filter: blur(15px);
            border: 2px solid rgba(255,255,255,0.3);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            cursor: pointer;
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
        }}
        
        .npc-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .npc-card:hover {{
            transform: translateY(-4px) scale(1.01);
            box-shadow: 0 12px 30px rgba(0,0,0,0.3);
            border-color: rgba(255,255,255,0.6);
        }}
        
        .npc-card:hover::before {{
            opacity: 1;
        }}
        
        .npc-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .npc-portrait-container {{
            flex-shrink: 0;
        }}
        
        .npc-portrait {{
            width: 70px;
            height: 70px;
            border-radius: 8px;
            background: rgba(0,0,0,0.3);
            border: 2px solid rgba(255,255,255,0.3);
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background-size: cover;
            background-position: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        
        .npc-portrait img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .portrait-placeholder {{
            font-size: 2em;
            opacity: 0.5;
        }}
        
        .npc-info {{
            flex: 1;
            min-width: 150px;
        }}
        
        .npc-name {{
            font-size: 1.3em;
            font-weight: 700;
            margin-bottom: 6px;
            line-height: 1.2;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        
        .npc-tags {{
            margin-top: 15px;
            margin-bottom: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }}
        
        .tag-label {{
            font-weight: 600;
            color: rgba(255,255,255,0.8);
            font-size: 0.9em;
        }}
        
        .tag {{
            padding: 4px 12px;
            background: rgba(255,215,0,0.3);
            border: 1px solid rgba(255,215,0,0.5);
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .location-group {{
            margin-bottom: 40px;
        }}
        
        .location-group-title {{
            font-size: 2em;
            font-weight: 700;
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(255,255,255,0.15);
            border-radius: 10px;
            border-left: 5px solid #FFD700;
        }}
        
        .npc-badges {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 12px;
        }}
        
        .badge {{
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 1em;
            font-weight: 600;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .badge-faction {{
            background: rgba(255,255,255,0.4);
            border: 2px solid rgba(255,255,255,0.5);
        }}
        
        .badge-status {{
            background: rgba(76, 175, 80, 0.6);
            border: 2px solid rgba(76, 175, 80, 0.8);
        }}
        
        .badge-status.deceased {{
            background: rgba(244, 67, 54, 0.6);
            border: 2px solid rgba(244, 67, 54, 0.8);
        }}
        
        .badge-status.trapped {{
            background: rgba(255, 152, 0, 0.6);
            border: 2px solid rgba(255, 152, 0, 0.8);
        }}
        
        .badge-status.petrified {{
            background: rgba(158, 158, 158, 0.6);
            border: 2px solid rgba(158, 158, 158, 0.8);
        }}
        
        .npc-location {{
            color: rgba(255,255,255,0.95);
            font-size: 0.9em;
            margin: 8px 0;
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 500;
        }}
        
        .npc-location::before {{
            content: '📍';
            font-size: 1em;
        }}
        
        .relationships {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255,255,255,0.3);
        }}
        
        .relationship-group {{
            margin-bottom: 10px;
            padding: 8px;
            background: rgba(0,0,0,0.2);
            border-radius: 6px;
            border-left: 3px solid;
        }}
        
        .relationship-type {{
            font-weight: 700;
            color: #FFD700;
            margin-bottom: 6px;
            text-transform: capitalize;
            font-size: 0.9em;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
            letter-spacing: 0.5px;
        }}
        
        .relationship-targets {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }}
        
        .relationship-link {{
            padding: 5px 10px;
            background: rgba(255,255,255,0.25);
            border-radius: 6px;
            font-size: 0.85em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid transparent;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .relationship-link:hover {{
            background: rgba(255,255,255,0.4);
            transform: translateY(-1px);
            box-shadow: 0 3px 6px rgba(0,0,0,0.3);
            border-color: rgba(255,255,255,0.6);
        }}
        
        .relationship-link.enemy {{
            background: rgba(244, 67, 54, 0.5);
            border-color: rgba(244, 67, 54, 0.7);
        }}
        
        .relationship-link.enemy:hover {{
            background: rgba(244, 67, 54, 0.7);
        }}
        
        .relationship-link.ally {{
            background: rgba(76, 175, 80, 0.5);
            border-color: rgba(76, 175, 80, 0.7);
        }}
        
        .relationship-link.ally:hover {{
            background: rgba(76, 175, 80, 0.7);
        }}
        
        .relationship-link.hierarchical {{
            background: rgba(255, 152, 0, 0.5);
            border-color: rgba(255, 152, 0, 0.7);
        }}
        
        .relationship-link.hierarchical:hover {{
            background: rgba(255, 152, 0, 0.7);
        }}
        
        .npc-notes {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid rgba(255,255,255,0.3);
            font-size: 1.05em;
            color: rgba(255,255,255,0.95);
            font-style: italic;
            line-height: 1.6;
            background: rgba(0,0,0,0.15);
            padding: 15px;
            border-radius: 10px;
        }}
        
        .hidden {{
            display: none;
        }}
        
        .stats {{
            text-align: center;
            margin-bottom: 25px;
            font-size: 1.4em;
            font-weight: 600;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 3px solid rgba(255,255,255,0.3);
        }}
        
        .tab {{
            padding: 15px 30px;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 10px 10px 0 0;
            color: #fff;
            font-size: 1.2em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}
        
        .tab:hover {{
            background: rgba(255,255,255,0.2);
        }}
        
        .tab.active {{
            background: rgba(255,255,255,0.25);
            border-bottom: 3px solid #FFD700;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block !important;
        }}
        
        /* Editor Styles */
        .editor-container {{
            display: flex;
            gap: 20px;
            min-height: 60vh;
        }}
        
        .editor-sidebar {{
            flex: 0 0 300px;
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 10px;
            border: 2px solid rgba(255,255,255,0.2);
        }}
        
        .editor-main {{
            flex: 1;
            background: rgba(0,0,0,0.3);
            padding: 30px;
            border-radius: 10px;
            border: 2px solid rgba(255,255,255,0.2);
        }}
        
        .npc-list-item {{
            padding: 12px;
            margin: 8px 0;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .npc-list-item:hover {{
            background: rgba(255,255,255,0.2);
            border-color: rgba(255,255,255,0.4);
        }}
        
        .npc-list-item.active {{
            background: rgba(255,215,0,0.3);
            border-color: #FFD700;
        }}
        
        .npc-list-item input[type="checkbox"] {{
            cursor: pointer;
            margin-right: 8px;
            flex-shrink: 0;
        }}
        
        .npc-list-item span {{
            flex: 1;
        }}
        
        .form-group {{
            margin-bottom: 20px;
        }}
        
        .form-group label {{
            display: block;
            color: #FFD700;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        
        .form-group input,
        .form-group textarea {{
            width: 100%;
            padding: 12px;
            background: rgba(0,0,0,0.5);
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            color: #fff;
            font-size: 1em;
            font-family: inherit;
        }}
        
        .form-group input:focus,
        .form-group textarea:focus {{
            outline: none;
            border-color: #FFD700;
            background: rgba(0,0,0,0.7);
        }}
        
        .form-actions {{
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }}
        
        .editor-btn {{
            padding: 12px 24px;
            background: rgba(255,255,255,0.2);
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            color: #fff;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .editor-btn:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }}
        
        .relationship-item {{
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            align-items: center;
        }}
        
        .relationship-item select,
        .relationship-item input {{
            flex: 1;
            padding: 8px;
            background: rgba(0,0,0,0.5);
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 6px;
            color: #fff;
        }}
        
        .relationship-item button {{
            padding: 8px 12px;
            background: #f44336;
            border: none;
            border-radius: 6px;
            color: #fff;
            cursor: pointer;
        }}
        
        .npc-list-item.selected {{
            background: rgba(156,39,176,0.4) !important;
            border-color: #9C27B0 !important;
        }}
        
        .npc-list-item input[type="checkbox"] {{
            margin-right: 8px;
        }}
        
        .relationships-collapsible {{
            max-height: none;
            overflow-y: visible;
            transition: max-height 0.3s ease;
        }}
        
        .relationships-collapsible.collapsed {{
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .relationship-template-btn {{
            padding: 6px 12px;
            margin: 5px;
            background: rgba(255,152,0,0.3);
            border: 1px solid rgba(255,152,0,0.5);
            border-radius: 4px;
            color: #fff;
            cursor: pointer;
            font-size: 0.9em;
        }}
        
        .relationship-template-btn:hover {{
            background: rgba(255,152,0,0.5);
        }}
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 10000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
        }}
        
        .modal-content {{
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            margin: 5% auto;
            padding: 30px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 15px;
            width: 80%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .close-modal {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .close-modal:hover {{
            color: #fff;
        }}
        
        .stat-box {{
            display: inline-block;
            padding: 10px 15px;
            margin: 5px;
            background: rgba(0,0,0,0.3);
            border-radius: 6px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .stat-label {{
            font-size: 0.8em;
            color: #ccc;
        }}
        
        .stat-value {{
            font-size: 1.2em;
            color: #FFD700;
            font-weight: bold;
        }}
        
        #mindmapContainer {{
            width: 100%;
            height: 80vh;
            min-height: 600px;
            background: rgba(0,0,0,0.2);
            border-radius: 15px;
            border: 3px solid rgba(255,255,255,0.3);
            position: relative;
            overflow: hidden;
        }}
        
        .mindmap-legend {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.7);
            padding: 20px;
            border-radius: 10px;
            z-index: 1000;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,255,255,0.3);
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 10px 0;
            font-size: 1.1em;
        }}
        
        .legend-line {{
            width: 40px;
            height: 3px;
            border-radius: 2px;
        }}
        
        .legend-color {{
            width: 30px;
            height: 30px;
            border-radius: 50%;
            border: 2px solid rgba(255,255,255,0.5);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🗺️ NPC Relationship Mind Map</h1>
        
        <div class="stats" id="stats"></div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('cards')">📋 Card View</button>
            <button class="tab" onclick="switchTab('mindmap')">🗺️ Visual Mind Map</button>
            <button class="tab" onclick="switchTab('map')">🗺️ World Map</button>
            <button class="tab" onclick="switchTab('editor')">✏️ Visual Editor</button>
            <button class="tab" onclick="switchTab('inventory')">🎒 Inventory Tracker</button>
        </div>
        
        <script>
        // Define switchTab early so it's available for onclick handlers
        function switchTab(tabName) {{
            // Hide all tabs and content
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');
            tabs.forEach(function(t) {{ t.classList.remove('active'); }});
            contents.forEach(function(t) {{
                t.classList.remove('active');
                t.style.display = 'none';
            }});
            
            // Show selected tab button
            let tabIndex = -1;
            if (tabName === 'cards') tabIndex = 0;
            else if (tabName === 'mindmap') tabIndex = 1;
            else if (tabName === 'map') tabIndex = 2;
            else if (tabName === 'editor') tabIndex = 3;
            else if (tabName === 'inventory') tabIndex = 4;
            
            if (tabIndex >= 0 && tabs[tabIndex]) {{
                tabs[tabIndex].classList.add('active');
            }}
            
            // Show selected content
            const contentId = tabName + 'Tab';
            const content = document.getElementById(contentId);
            if (content) {{
                content.classList.add('active');
                content.style.display = 'block';
                
                // Initialize tab-specific functionality
                if (tabName === 'cards' && typeof initCardView === 'function') {{
                    initCardView();
                }} else if (tabName === 'mindmap' && typeof initMindMap === 'function') {{
                    initMindMap();
                }} else if (tabName === 'map') {{
                    // Map tab - no initialization needed, just display the SVG
                }} else if (tabName === 'editor' && typeof initEditor === 'function') {{
                    initEditor();
                }} else if (tabName === 'inventory' && typeof initInventory === 'function') {{
                    initInventory();
                }}
            }}
        }}
        window.switchTab = switchTab;
        </script>
        
        <div id="cardsTab" class="tab-content active">
        <div class="controls">
            <div class="filter-group">
                <label>Filter by Faction:</label>
                <select id="factionFilter">
                    <option value="">All Factions</option>
"""
        
        for faction in sorted(factions):
            html += f'                    <option value="{faction}">{faction}</option>\n'
        
        html += """                </select>
                
                <label>Filter by Status:</label>
                <select id="statusFilter">
                    <option value="">All Statuses</option>
                    <option value="alive">Alive</option>
                    <option value="deceased">Deceased</option>
                    <option value="trapped">Trapped</option>
                    <option value="petrified">Petrified</option>
                    <option value="spirit">Spirit</option>
                    <option value="unknown">Unknown</option>
                </select>
                
                <label>Group By:</label>
                <select id="groupBy">
                    <option value="none">None</option>
                    <option value="location">Location</option>
                    <option value="faction">Faction</option>
                    <option value="status">Status</option>
                </select>
                
                <label>Sort By:</label>
                <select id="sortBy">
                    <option value="name">Name (A-Z)</option>
                    <option value="name-desc">Name (Z-A)</option>
                    <option value="faction">Faction</option>
                    <option value="location">Location</option>
                    <option value="status">Status</option>
                </select>
                
                <label>Search:</label>
                <input type="text" id="searchBox" placeholder="Search NPCs...">
                
                <label style="margin-left: 20px;">
                    <input type="checkbox" id="spoilerFreeMode" style="margin-right: 5px;">
                    Spoiler-Free Mode
                </label>
                
                <button onclick="exportToImage()" style="padding: 12px 24px; background: rgba(255,215,0,0.3); border: 2px solid #FFD700; border-radius: 8px; color: #fff; font-weight: 600; cursor: pointer; margin-left: 20px;">
                    📷 Export Image
                </button>
            </div>
        </div>
        
        <div id="npcContainer">
        <div class="npc-grid" id="npcGrid">
"""
        
        # Generate NPC cards - sorted alphabetically by name
        sorted_npcs = sorted(npcs.items(), key=lambda x: x[1].get('name', x[0]).lower())
        for npc_id, npc_data in sorted_npcs:
            name = npc_data.get('name', npc_id)
            faction = npc_data.get('faction', 'Unknown')
            location = npc_data.get('location', 'Unknown')
            status = npc_data.get('status', 'unknown')
            notes = npc_data.get('notes', '')
            relationships = npc_data.get('relationships', {})
            
            faction_color = faction_colors.get(faction, '#808080')
            
            tags = npc_data.get('tags', [])
            tags_str = ', '.join(tags) if tags else ''
            portrait = npc_data.get('portrait', '')
            spoiler = npc_data.get('spoiler', False)
            
            portrait_html = ''
            if portrait:
                # Fix path: Images folder is now in the same directory as HTML (for GitHub Pages)
                # Convert any path to use local Images/ folder
                if portrait.startswith('../Images/') or portrait.startswith('../../Images/'):
                    # Extract just the filename
                    filename = portrait.split('/')[-1]
                    portrait = 'Images/' + filename
                elif not portrait.startswith('Images/'):
                    # If it's just a filename or different path, ensure it's in Images/
                    filename = portrait.split('/')[-1]
                    portrait = 'Images/' + filename
                
                # URL encode the path to handle special characters (apostrophes, spaces, etc.)
                # This is especially important for file:// protocol
                import urllib.parse
                # Split path to encode only the filename part
                path_parts = portrait.rsplit('/', 1)
                if len(path_parts) == 2:
                    encoded_filename = urllib.parse.quote(path_parts[1], safe='')
                    encoded_path = path_parts[0] + '/' + encoded_filename
                else:
                    encoded_path = urllib.parse.quote(portrait, safe='/')
                
                # Use encoded path for both background-image and img src
                # Improved error handling: suppress console errors for missing images
                # Use onerror to hide broken images and prevent console errors
                portrait_html = f'<img src="{encoded_path}" alt="{name}" onerror="this.style.display=\'none\'; this.parentElement.style.backgroundImage=\'none\'; this.onerror=null;" loading="lazy">'
                portrait_style = f"background-image: url('{encoded_path}');"
            else:
                portrait_html = '<div class="portrait-placeholder">📷</div>'
                portrait_style = ''
            
            tags_html = ''
            if tags:
                tags_html = '<div class="npc-tags"><span class="tag-label">Tags:</span> ' + ''.join([f'<span class="tag">{tag}</span>' for tag in tags]) + '</div>'
            
            html += f"""            <div class="npc-card" data-faction="{faction}" data-status="{status}" data-name="{name.lower()}" data-location="{location.lower()}" data-tags="{tags_str.lower()}" data-spoiler="{str(spoiler).lower()}" data-portrait="{portrait if portrait else ''}">
                <div class="npc-header">
                    <div class="npc-portrait-container">
                        <div class="npc-portrait" style="{portrait_style}">
                            {portrait_html}
                        </div>
                    </div>
                    <div class="npc-info">
                        <div class="npc-name">{name}</div>
                        <div class="npc-location">📍 {location}</div>
                    </div>
                </div>
                
                <div class="npc-badges">
                    <span class="badge badge-faction" style="background: {faction_color}80;">{faction}</span>
                    <span class="badge badge-status {status}">{status.title()}</span>
                </div>
                
                {tags_html}
"""
            
            if relationships:
                html += '                <div class="relationships">\n'
                for rel_type, targets in relationships.items():
                    if not targets:
                        continue
                    target_list = targets if isinstance(targets, list) else [targets]
                    
                    # Determine relationship class
                    rel_class = 'neutral'
                    if 'enemy' in rel_type or 'feeds_on' in rel_type:
                        rel_class = 'enemy'
                    elif 'ally' in rel_type or 'works_with' in rel_type:
                        rel_class = 'ally'
                    elif 'controls' in rel_type or 'serves' in rel_type or 'trapped_by' in rel_type:
                        rel_class = 'hierarchical'
                    
                    html += f'                    <div class="relationship-group">\n'
                    html += f'                        <div class="relationship-type">{rel_type.replace("_", " ").title()}:</div>\n'
                    html += f'                        <div class="relationship-targets">\n'
                    for target in target_list:
                        html += f'                            <span class="relationship-link {rel_class}" onclick="highlightNPC(\'{target}\')">{target}</span>\n'
                    html += '                        </div>\n'
                    html += '                    </div>\n'
                html += '                </div>\n'
            
            if notes:
                html += f'                <div class="npc-notes">{notes}</div>\n'
            
            html += '            </div>\n'
        
        html += """        </div>
        </div>
        </div>
        
        <div id="mindmapTab" class="tab-content">
            <div class="mindmap-legend">
                <h3 style="margin-top: 0; color: #FFD700;">Legend & Controls</h3>
                <div style="margin-bottom: 15px;">
                    <button id="toggleEdgeLabels" onclick="toggleEdgeLabels()" style="padding: 8px 12px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 8px; font-size: 0.9em; margin-bottom: 5px;">Toggle Edge Labels</button>
                    <button id="togglePhysics" onclick="togglePhysics()" style="padding: 8px 12px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9em; margin-bottom: 5px;">Pause Physics</button>
                    <br>
                    <button id="spreadNodes" onclick="spreadNodes()" style="padding: 8px 12px; background: #FF9800; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9em; margin-right: 8px; margin-bottom: 5px;">Spread Nodes</button>
                    <button id="fitNetwork" onclick="fitNetwork()" style="padding: 8px 12px; background: #9C27B0; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9em; margin-bottom: 5px;">Fit to Screen</button>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: #4CAF50;"></div>
                    <span>Ally / Works With</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: #f44336;"></div>
                    <span>Enemy / Feeds On</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: #FF9800;"></div>
                    <span>Controls / Serves</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: #9E9E9E;"></div>
                    <span>Other Relationships</span>
                </div>
            </div>
            <div id="mindmapContainer"></div>
        </div>
        
        <div id="mapTab" class="tab-content">
            <div style="padding: 20px;">
                <h2 style="color: #FFD700; margin-top: 0;">🗺️ Genia World Map</h2>
                <div style="background: rgba(0,0,0,0.3); border-radius: 10px; padding: 20px; border: 2px solid rgba(255,255,255,0.2); display: flex; gap: 15px; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 300px;">
                        <div style="margin-bottom: 15px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                            <button id="mapResetBtn" onclick="resetMapView()" style="padding: 8px 16px; background: rgba(255,215,0,0.3); border: 2px solid #FFD700; border-radius: 6px; color: #fff; font-weight: 600; cursor: pointer; font-size: 0.9em;">🔄 Reset View</button>
                            <button id="toggleLabelsBtn" onclick="toggleMapLabels()" style="padding: 8px 16px; background: rgba(76,175,80,0.3); border: 2px solid #4CAF50; border-radius: 6px; color: #fff; font-weight: 600; cursor: pointer; font-size: 0.9em;">🏷️ Labels: ON</button>
                            <button id="addMarkerBtn" onclick="toggleMarkerMode()" style="padding: 8px 16px; background: rgba(33,150,243,0.3); border: 2px solid #2196F3; border-radius: 6px; color: #fff; font-weight: 600; cursor: pointer; font-size: 0.9em;">📍 Add Marker</button>
                            <button id="drawAnnotationBtn" onclick="toggleAnnotationMode()" style="padding: 8px 16px; background: rgba(156,39,176,0.3); border: 2px solid #9C27B0; border-radius: 6px; color: #fff; font-weight: 600; cursor: pointer; font-size: 0.9em;">✏️ Draw</button>
                            <button id="undoBtn" onclick="undoMapAction()" style="padding: 8px 16px; background: rgba(158,158,158,0.3); border: 2px solid #9E9E9E; border-radius: 6px; color: #fff; font-weight: 600; cursor: pointer; font-size: 0.9em;" title="Undo">↶ Undo</button>
                            <button id="redoBtn" onclick="redoMapAction()" style="padding: 8px 16px; background: rgba(158,158,158,0.3); border: 2px solid #9E9E9E; border-radius: 6px; color: #fff; font-weight: 600; cursor: pointer; font-size: 0.9em;" title="Redo">↷ Redo</button>
                            <span id="mapZoomLevel" style="color: #aaa; font-size: 0.9em;">Zoom: 100%</span>
                        </div>
                        <div id="mapContainer" style="width: 100%; height: 80vh; min-height: 600px; overflow: hidden; background: rgba(0,0,0,0.2); border-radius: 8px; position: relative; cursor: grab; touch-action: none; -webkit-user-select: none; user-select: none; contain: layout style paint;">
                            <div id="mapWrapper" style="width: 100%; height: 100%; position: relative; overflow: hidden; will-change: transform; contain: layout style paint;">
                                <div id="worldMapSvgContainer" style="position: absolute; top: 50%; left: 50%; transform: translate3d(-50%, -50%, 0) scale(1); transform-origin: center center; user-select: none; -webkit-user-select: none; pointer-events: none; will-change: transform;"></div>
                                <svg id="mapOverlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10;"></svg>
                                <div id="mapError" style="display: none; text-align: center; padding: 40px; color: #ccc; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                                    <p style="font-size: 1.2em; margin-bottom: 10px;">⚠️ Map not found</p>
                                    <p>Please ensure "Gienia World Map.svg" is in the Images folder.</p>
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 15px; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 5px; font-size: 0.9em; color: #aaa;">
                            <p style="margin: 5px 0;">💡 <strong>Controls:</strong> Mouse wheel to zoom | Click and drag to pan | Double-click to reset | Pinch to zoom on mobile</p>
                        </div>
                    </div>
                    <div id="mapSidebar" style="width: 280px; min-width: 280px; background: rgba(0,0,0,0.2); border-radius: 8px; padding: 15px; max-height: 80vh; overflow-y: auto;">
                        <h3 style="color: #FFD700; margin-top: 0; margin-bottom: 15px; font-size: 1.1em;">📍 Locations</h3>
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; color: #aaa; font-size: 0.9em; margin-bottom: 5px;">🔍 Search:</label>
                            <input type="text" id="markerSearchInput" oninput="filterMarkersByCategory()" placeholder="Search locations..." style="width: 100%; padding: 6px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: #fff; font-size: 0.9em; box-sizing: border-box;">
                        </div>
                        <div style="margin-bottom: 15px;">
                            <label style="display: block; color: #aaa; font-size: 0.9em; margin-bottom: 5px;">Filter by Category:</label>
                            <select id="markerCategoryFilter" onchange="filterMarkersByCategory()" style="width: 100%; padding: 6px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; color: #fff; font-size: 0.9em;">
                                <option value="all">All Categories</option>
                                <option value="city">Cities</option>
                                <option value="dungeon">Dungeons</option>
                                <option value="landmark">Landmarks</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        <div id="locationList" style="display: flex; flex-direction: column; gap: 8px;">
                            <p style="color: #666; font-size: 0.85em; font-style: italic;">No locations added yet. Click "Add Marker" to place markers on the map.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        // Map zoom and pan functionality
        (function() {{
            let mapScale = 1;
            let mapX = 0;
            let mapY = 0;
            let isDragging = false;
            let dragStartX = 0;
            let dragStartY = 0;
            let dragStartMapX = 0;
            let dragStartMapY = 0;
            // Touch gesture variables (declared here, used in touch handlers)
            let lastTouchDistance = 0;
            let lastTouchCenterX = 0;
            let lastTouchCenterY = 0;
            let touchStartTime = 0;
            let touchStartPos = {{ x: 0, y: 0 }};
            let isPinching = false;
            let twoFingerPanStart = {{ x: 0, y: 0 }};
            let touches = [];
            
            // Marker and annotation system
            let markers = [];
            let annotations = [];
            let markerMode = false;
            let annotationMode = false;
            let isDrawing = false;
            let currentPath = null;
            let labelsVisible = true;
            let mapBounds = {{ minX: -2000, maxX: 2000, minY: -1000, maxY: 1000 }};
            
            const markerCategories = {{
                'city': {{ name: 'City', color: '#4CAF50', icon: '🏙️' }},
                'dungeon': {{ name: 'Dungeon', color: '#F44336', icon: '🏰' }},
                'landmark': {{ name: 'Landmark', color: '#FF9800', icon: '🗿' }},
                'other': {{ name: 'Other', color: '#9E9E9E', icon: '📍' }}
            }};
            
            const mapSvgContainer = document.getElementById('worldMapSvgContainer');
            const mapContainer = document.getElementById('mapContainer');
            const mapWrapper = document.getElementById('mapWrapper');
            const zoomLevelDisplay = document.getElementById('mapZoomLevel');
            const mapError = document.getElementById('mapError');
            const mapOverlay = document.getElementById('mapOverlay');
            const locationList = document.getElementById('locationList');
            
            // Expose functions globally first, even if elements don't exist yet
            function resetMapView() {{
                if (!mapContainer || !mapSvgContainer) return;
                mapScale = 1;
                mapX = 0;
                mapY = 0;
                updateMapTransform();
            }}
            
            // Define functions that need to be available immediately (before DOM elements exist)
            function resetMapView() {{
                if (!mapContainer || !mapSvgContainer) return;
                mapScale = 1;
                mapX = 0;
                mapY = 0;
                updateMapTransform();
            }}
            
            function toggleMarkerMode() {{
                if (!mapContainer) return;
                markerMode = !markerMode;
                annotationMode = false;
                const btn = document.getElementById('addMarkerBtn');
                const drawBtn = document.getElementById('drawAnnotationBtn');
                if (btn) {{
                    btn.style.background = markerMode ? 'rgba(33,150,243,0.6)' : 'rgba(33,150,243,0.3)';
                    btn.textContent = markerMode ? '📍 Cancel' : '📍 Add Marker';
                }}
                if (drawBtn) {{
                    drawBtn.style.background = 'rgba(156,39,176,0.3)';
                    drawBtn.textContent = '✏️ Draw';
                }}
                mapContainer.style.cursor = markerMode ? 'crosshair' : 'grab';
            }}
            
            function toggleAnnotationMode() {{
                if (!mapContainer) return;
                annotationMode = !annotationMode;
                markerMode = false;
                const btn = document.getElementById('drawAnnotationBtn');
                const markerBtn = document.getElementById('addMarkerBtn');
                if (btn) {{
                    btn.style.background = annotationMode ? 'rgba(156,39,176,0.6)' : 'rgba(156,39,176,0.3)';
                    btn.textContent = annotationMode ? '✏️ Cancel' : '✏️ Draw';
                }}
                if (markerBtn) {{
                    markerBtn.style.background = 'rgba(33,150,243,0.3)';
                    markerBtn.textContent = '📍 Add Marker';
                }}
                mapContainer.style.cursor = annotationMode ? 'crosshair' : 'grab';
                if (!annotationMode && isDrawing) {{
                    finishAnnotation();
                }}
            }}
            
            function toggleMapLabels() {{
                labelsVisible = !labelsVisible;
                const btn = document.getElementById('toggleLabelsBtn');
                if (btn) {{
                    btn.textContent = labelsVisible ? '🏷️ Labels: ON' : '🏷️ Labels: OFF';
                }}
                if (mapOverlay) renderMarkers();
            }}
            
            // Expose functions to window immediately (before early return)
            window.resetMapView = resetMapView;
            window.toggleMarkerMode = toggleMarkerMode;
            window.toggleAnnotationMode = toggleAnnotationMode;
            window.toggleMapLabels = toggleMapLabels;
            
            if (!mapSvgContainer || !mapContainer) return;
            
            let rafId = null;
            let pendingUpdate = false;
            let svgLoaded = false;
            let renderRafId = null;
            let lastRenderTime = 0;
            const RENDER_THROTTLE = 100; // Only render markers/annotations every 100ms
            
            // Undo/Redo history
            let historyStack = [];
            let historyIndex = -1;
            const MAX_HISTORY = 50;
            
            
            // Constrain pan to map bounds
            function constrainPan() {{
                const rect = mapContainer.getBoundingClientRect();
                const maxX = (mapBounds.maxX * mapScale) - (rect.width / 2);
                const minX = (mapBounds.minX * mapScale) + (rect.width / 2);
                const maxY = (mapBounds.maxY * mapScale) - (rect.height / 2);
                const minY = (mapBounds.minY * mapScale) + (rect.height / 2);
                
                mapX = Math.max(minX, Math.min(maxX, mapX));
                mapY = Math.max(minY, Math.min(maxY, mapY));
            }}
            
            // Simple function to load SVG map
            function loadSvgMap() {{
                if (svgLoaded) return;
                
                const svgContent = PLACEHOLDER_SVG_CONTENT;
                if (svgContent && svgContent.trim() !== '') {{
                    try {{
                        mapSvgContainer.innerHTML = svgContent;
                        svgLoaded = true;
                    }} catch(e) {{
                        console.error('Failed to load SVG:', e);
                        if (mapError) mapError.style.display = 'block';
                    }}
                }} else {{
                    // Fallback: try to load from file
                    const xhr = new XMLHttpRequest();
                    xhr.open('GET', 'Images/Gienia World Map.svg', true);
                    xhr.onreadystatechange = function() {{
                        if (xhr.readyState === 4 && (xhr.status === 0 || xhr.status === 200)) {{
                            mapSvgContainer.innerHTML = xhr.responseText;
                            svgLoaded = true;
                        }} else if (xhr.readyState === 4) {{
                            if (mapError) mapError.style.display = 'block';
                        }}
                    }};
                    xhr.onerror = function() {{
                        if (mapError) mapError.style.display = 'block';
                    }};
                    xhr.send();
                }}
            }}
            
            // Load SVG when map tab is opened
            const mapTab = document.getElementById('mapTab');
            if (mapTab) {{
                const observer = new MutationObserver(function(mutations) {{
                    if (mapTab.classList.contains('active') && !svgLoaded) {{
                        loadSvgMap();
                    }}
                }});
                observer.observe(mapTab, {{ attributes: true, attributeFilter: ['class'] }});
                
                // Also check if already active
                if (mapTab.classList.contains('active')) {{
                    loadSvgMap();
                }}
            }}
            
            function updateMapTransform() {{
                if (!mapSvgContainer) return;
                
                // Constrain pan to bounds
                constrainPan();
                
                // Use requestAnimationFrame for smooth updates
                if (rafId) {{
                    pendingUpdate = true;
                    return;
                }}
                
                rafId = requestAnimationFrame(function() {{
                    // Use translate3d for GPU acceleration
                    mapSvgContainer.style.transform = `translate3d(calc(-50% + ${{mapX}}px), calc(-50% + ${{mapY}}px), 0) scale3d(${{mapScale}}, ${{mapScale}}, 1)`;
                    if (zoomLevelDisplay) {{
                        zoomLevelDisplay.textContent = `Zoom: ${{Math.round(mapScale * 100)}}%`;
                    }}
                    // Throttle marker/annotation rendering for performance
                    const now = Date.now();
                    if (svgLoaded && (now - lastRenderTime > RENDER_THROTTLE || !isDragging)) {{
                        if (renderRafId) cancelAnimationFrame(renderRafId);
                        renderRafId = requestAnimationFrame(function() {{
                            renderMarkers();
                            renderAnnotations();
                            lastRenderTime = now;
                            renderRafId = null;
                        }});
                    }}
                    rafId = null;
                    if (pendingUpdate) {{
                        pendingUpdate = false;
                        updateMapTransform();
                    }}
                }});
            }}
            
            // resetMapView is already defined and exposed above
            
            // Mouse wheel zoom
            mapContainer.addEventListener('wheel', function(e) {{
                e.preventDefault();
                const rect = mapContainer.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;
                
                const delta = e.deltaY > 0 ? 0.9 : 1.1;
                const newScale = Math.max(0.5, Math.min(20, mapScale * delta)); // Increased max zoom to 2000%
                
                // Zoom towards mouse position
                const scaleChange = newScale / mapScale;
                const containerCenterX = rect.width / 2;
                const containerCenterY = rect.height / 2;
                
                mapX = (mouseX - containerCenterX) - (mouseX - containerCenterX - mapX) * scaleChange;
                mapY = (mouseY - containerCenterY) - (mouseY - containerCenterY - mapY) * scaleChange;
                
                mapScale = newScale;
                updateMapTransform();
            }});
            
            // Mouse drag to pan or add marker/annotation
            mapContainer.addEventListener('mousedown', function(e) {{
                if (e.button !== 0) return; // Only left mouse button
                e.stopPropagation(); // Prevent event bubbling
                
                if (markerMode) {{
                    addMarkerAt(e.clientX, e.clientY);
                    return;
                }}
                
                if (annotationMode) {{
                    startAnnotation(e.clientX, e.clientY);
                    return;
                }}
                
                // Normal pan mode
                isDragging = true;
                dragStartX = e.clientX;
                dragStartY = e.clientY;
                dragStartMapX = mapX;
                dragStartMapY = mapY;
                mapContainer.style.cursor = 'grabbing';
            }});
            
            document.addEventListener('mousemove', function(e) {{
                if (isDrawing && annotationMode) {{
                    addAnnotationPoint(e.clientX, e.clientY);
                    return;
                }}
                if (!isDragging) return;
                mapX = dragStartMapX + (e.clientX - dragStartX);
                mapY = dragStartMapY + (e.clientY - dragStartY);
                updateMapTransform();
            }});
            
            document.addEventListener('mouseup', function() {{
                if (isDrawing && annotationMode) {{
                    finishAnnotation();
                }}
                if (isDragging) {{
                    isDragging = false;
                    mapContainer.style.cursor = markerMode ? 'crosshair' : (annotationMode ? 'crosshair' : 'grab');
                    // Force render when dragging stops
                    if (svgLoaded) {{
                        renderMarkers();
                        renderAnnotations();
                    }}
                }}
            }});
            
            // Double-click to reset
            mapContainer.addEventListener('dblclick', function(e) {{
                e.preventDefault();
                resetMapView();
            }});
            
            // Touch event helper functions (touches variable already declared above)
            function getTouchDistance(touch1, touch2) {{
                const dx = touch1.clientX - touch2.clientX;
                const dy = touch1.clientY - touch2.clientY;
                return Math.sqrt(dx * dx + dy * dy);
            }}
            
            function getTouchCenter(touch1, touch2) {{
                return {{
                    x: (touch1.clientX + touch2.clientX) / 2,
                    y: (touch1.clientY + touch2.clientY) / 2
                }};
            }}
            
            mapContainer.addEventListener('touchstart', function(e) {{
                e.preventDefault();
                touches = Array.from(e.touches);
                touchStartTime = Date.now();
                
                if (touches.length === 1) {{
                    // Single touch - check if it's marker/annotation mode first
                    if (markerMode) {{
                        const rect = mapContainer.getBoundingClientRect();
                        addMarkerAt(touches[0].clientX, touches[0].clientY);
                        return;
                    }}
                    if (annotationMode) {{
                        const rect = mapContainer.getBoundingClientRect();
                        startAnnotation(touches[0].clientX, touches[0].clientY);
                        return;
                    }}
                    // Single touch - start pan
                    isDragging = true;
                    dragStartX = touches[0].clientX;
                    dragStartY = touches[0].clientY;
                    dragStartMapX = mapX;
                    dragStartMapY = mapY;
                    touchStartPos = {{ x: touches[0].clientX, y: touches[0].clientY }};
                }} else if (touches.length === 2) {{
                    // Two touches - prepare for pinch zoom or two-finger pan
                    isPinching = true;
                    lastTouchDistance = getTouchDistance(touches[0], touches[1]);
                    const center = getTouchCenter(touches[0], touches[1]);
                    const rect = mapContainer.getBoundingClientRect();
                    lastTouchCenterX = center.x - rect.left;
                    lastTouchCenterY = center.y - rect.top;
                    twoFingerPanStart = {{ x: mapX, y: mapY }};
                }}
            }}, {{ passive: false }});
            
            mapContainer.addEventListener('touchmove', function(e) {{
                e.preventDefault();
                touches = Array.from(e.touches);
                
                if (touches.length === 1 && isDragging && !isPinching) {{
                    // Single touch - pan
                    mapX = dragStartMapX + (touches[0].clientX - dragStartX);
                    mapY = dragStartMapY + (touches[0].clientY - dragStartY);
                    updateMapTransform();
                }} else if (touches.length === 2 && isPinching) {{
                    // Two touches - pinch zoom or two-finger pan
                    const currentDistance = getTouchDistance(touches[0], touches[1]);
                    const distanceChange = Math.abs(currentDistance - lastTouchDistance);
                    
                    // If fingers are moving apart/together significantly, it's a pinch zoom
                    if (distanceChange > 5) {{
                        const scaleChange = currentDistance / lastTouchDistance;
                        const newScale = Math.max(0.5, Math.min(20, mapScale * scaleChange));
                        
                        // Zoom towards touch center
                        const scaleRatio = newScale / mapScale;
                        const rect = mapContainer.getBoundingClientRect();
                        const containerCenterX = rect.width / 2;
                        const containerCenterY = rect.height / 2;
                        
                        mapX = lastTouchCenterX - containerCenterX - (lastTouchCenterX - containerCenterX - mapX) * scaleRatio;
                        mapY = lastTouchCenterY - containerCenterY - (lastTouchCenterY - containerCenterY - mapY) * scaleRatio;
                        
                        mapScale = newScale;
                        lastTouchDistance = currentDistance;
                        updateMapTransform();
                    }} else {{
                        // Two-finger pan: use the movement of the center point
                        const center = getTouchCenter(touches[0], touches[1]);
                        const rect = mapContainer.getBoundingClientRect();
                        const centerX = center.x - rect.left;
                        const centerY = center.y - rect.top;
                        const dx = centerX - lastTouchCenterX;
                        const dy = centerY - lastTouchCenterY;
                        mapX = twoFingerPanStart.x + dx;
                        mapY = twoFingerPanStart.y + dy;
                        lastTouchCenterX = centerX;
                        lastTouchCenterY = centerY;
                        updateMapTransform();
                    }}
                }}
            }}, {{ passive: false }});
            
            mapContainer.addEventListener('touchend', function(e) {{
                touches = Array.from(e.touches);
                if (touches.length === 0) {{
                    isDragging = false;
                    isPinching = false;
                    if (isDrawing && annotationMode) {{
                        finishAnnotation();
                    }}
                }} else if (touches.length === 1) {{
                    // One finger left, switch to single touch pan
                    isPinching = false;
                    isDragging = true;
                    dragStartX = touches[0].clientX;
                    dragStartY = touches[0].clientY;
                    dragStartMapX = mapX;
                    dragStartMapY = mapY;
                }}
            }});
            
            // Load markers and annotations from localStorage
            function loadMapData() {{
                try {{
                    const saved = localStorage.getItem('mapMarkers');
                    if (saved) markers = JSON.parse(saved);
                    const savedAnnot = localStorage.getItem('mapAnnotations');
                    if (savedAnnot) annotations = JSON.parse(savedAnnot);
                    // Initialize history with initial state (empty or loaded)
                    const initialState = {{
                        markers: JSON.parse(JSON.stringify(markers)),
                        annotations: JSON.parse(JSON.stringify(annotations))
                    }};
                    historyStack = [initialState];
                    historyIndex = 0; // Start at 0 so we can undo to the initial state
                    updateUndoRedoButtons();
                    renderMarkers();
                    renderAnnotations();
                    updateLocationList();
                }} catch(e) {{
                    console.error('Failed to load map data:', e);
                }}
            }}
            
            // Mini-map functions
            
            // Save markers and annotations to localStorage
            function saveMapData() {{
                try {{
                    localStorage.setItem('mapMarkers', JSON.stringify(markers));
                    localStorage.setItem('mapAnnotations', JSON.stringify(annotations));
                    // Save to history
                    saveToHistory();
                }} catch(e) {{
                    console.error('Failed to save map data:', e);
                }}
            }}
            
            // Undo/Redo functions
            function saveToHistory() {{
                const state = {{
                    markers: JSON.parse(JSON.stringify(markers)),
                    annotations: JSON.parse(JSON.stringify(annotations))
                }};
                // Remove any future history if we're not at the end
                if (historyIndex < historyStack.length - 1) {{
                    historyStack = historyStack.slice(0, historyIndex + 1);
                }}
                historyStack.push(state);
                if (historyStack.length > MAX_HISTORY) {{
                    historyStack.shift();
                }} else {{
                    historyIndex++;
                }}
                updateUndoRedoButtons();
            }}
            
            function undoMapAction() {{
                if (historyIndex > 0) {{
                    historyIndex--;
                    const state = historyStack[historyIndex];
                    markers = JSON.parse(JSON.stringify(state.markers));
                    annotations = JSON.parse(JSON.stringify(state.annotations));
                    renderMarkers();
                    renderAnnotations();
                    updateLocationList();
                    updateUndoRedoButtons();
                    // Save to localStorage
                    try {{
                        localStorage.setItem('mapMarkers', JSON.stringify(markers));
                        localStorage.setItem('mapAnnotations', JSON.stringify(annotations));
                    }} catch(e) {{
                        console.error('Failed to save:', e);
                    }}
                }} else if (historyIndex === 0 && historyStack.length > 1) {{
                    // Allow undoing the first change back to initial state
                    historyIndex = 0;
                    const state = historyStack[0];
                    markers = JSON.parse(JSON.stringify(state.markers));
                    annotations = JSON.parse(JSON.stringify(state.annotations));
                    renderMarkers();
                    renderAnnotations();
                    updateLocationList();
                    updateUndoRedoButtons();
                    // Save to localStorage
                    try {{
                        localStorage.setItem('mapMarkers', JSON.stringify(markers));
                        localStorage.setItem('mapAnnotations', JSON.stringify(annotations));
                    }} catch(e) {{
                        console.error('Failed to save:', e);
                    }}
                }}
            }}
            
            function redoMapAction() {{
                if (historyIndex < historyStack.length - 1) {{
                    historyIndex++;
                    const state = historyStack[historyIndex];
                    markers = JSON.parse(JSON.stringify(state.markers));
                    annotations = JSON.parse(JSON.stringify(state.annotations));
                    renderMarkers();
                    renderAnnotations();
                    updateLocationList();
                    updateUndoRedoButtons();
                    // Save to localStorage
                    try {{
                        localStorage.setItem('mapMarkers', JSON.stringify(markers));
                        localStorage.setItem('mapAnnotations', JSON.stringify(annotations));
                    }} catch(e) {{
                        console.error('Failed to save:', e);
                    }}
                }}
            }}
            
            function updateUndoRedoButtons() {{
                const undoBtn = document.getElementById('undoBtn');
                const redoBtn = document.getElementById('redoBtn');
                if (undoBtn) {{
                    // Can undo if we're not at the initial state (index 0) or if there are changes after initial state
                    const canUndo = historyIndex > 0 || (historyIndex === 0 && historyStack.length > 1);
                    undoBtn.disabled = !canUndo;
                    undoBtn.style.opacity = canUndo ? '1' : '0.5';
                }}
                if (redoBtn) {{
                    redoBtn.disabled = historyIndex >= historyStack.length - 1;
                    redoBtn.style.opacity = historyIndex >= historyStack.length - 1 ? '0.5' : '1';
                }}
            }}
            
            window.undoMapAction = undoMapAction;
            window.redoMapAction = redoMapAction;
            
            // Get map coordinates from screen coordinates
            function screenToMap(screenX, screenY) {{
                const rect = mapContainer.getBoundingClientRect();
                const containerX = screenX - rect.left;
                const containerY = screenY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const coordX = (containerX - centerX - mapX) / mapScale;
                const coordY = (containerY - centerY - mapY) / mapScale;
                return {{ x: coordX, y: coordY }};
            }}
            
            // Render markers on overlay with clustering
            function renderMarkers() {{
                if (!mapOverlay) return;
                // Remove all marker-related elements including cluster text
                const existingMarkers = mapOverlay.querySelectorAll('.map-marker, .map-marker-label, .map-cluster, .map-cluster-text');
                existingMarkers.forEach(m => m.remove());
                // Also remove any text elements that might be cluster numbers
                const allTexts = mapOverlay.querySelectorAll('text');
                allTexts.forEach(function(text) {{
                    // Check if this text is a cluster number (numeric content, positioned near a cluster)
                    const textContent = text.textContent;
                    if (textContent && /^\\d+$/.test(textContent.trim()) && text.getAttribute('fill') === '#000') {{
                        text.remove();
                    }}
                }});
                
                const rect = mapContainer.getBoundingClientRect();
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                // Clustering threshold: cluster markers when zoomed out (scale < 1.5)
                const clusterThreshold = mapScale < 1.5 ? 50 : Infinity;
                const clusters = [];
                let unclustered = [];
                
                if (clusterThreshold < Infinity) {{
                    // Group markers into clusters
                    markers.forEach(function(marker) {{
                        const screenX = centerX + marker.x * mapScale + mapX;
                        const screenY = centerY + marker.y * mapScale + mapY;
                        if (screenX < -100 || screenX > rect.width + 100 || screenY < -100 || screenY > rect.height + 100) return;
                        
                        let addedToCluster = false;
                        for (let i = 0; i < clusters.length; i++) {{
                            const cluster = clusters[i];
                            const dx = screenX - cluster.x;
                            const dy = screenY - cluster.y;
                            const dist = Math.sqrt(dx * dx + dy * dy);
                            if (dist < clusterThreshold) {{
                                cluster.markers.push(marker);
                                cluster.x = (cluster.x * (cluster.markers.length - 1) + screenX) / cluster.markers.length;
                                cluster.y = (cluster.y * (cluster.markers.length - 1) + screenY) / cluster.markers.length;
                                addedToCluster = true;
                                break;
                            }}
                        }}
                        if (!addedToCluster) {{
                            clusters.push({{ x: screenX, y: screenY, markers: [marker] }});
                        }}
                    }});
                    
                    // Render clusters
                    clusters.forEach(function(cluster) {{
                        if (cluster.markers.length === 1) {{
                            unclustered.push(cluster.markers[0]);
                        }} else {{
                            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                            circle.setAttribute('cx', cluster.x);
                            circle.setAttribute('cy', cluster.y);
                            circle.setAttribute('r', 12 + Math.min(cluster.markers.length * 2, 10));
                            circle.setAttribute('fill', '#FFD700');
                            circle.setAttribute('stroke', '#fff');
                            circle.setAttribute('stroke-width', 2);
                            circle.setAttribute('class', 'map-cluster');
                            circle.style.cursor = 'pointer';
                            circle.style.pointerEvents = 'all';
                            circle.onclick = function(e) {{
                                e.stopPropagation();
                                // Zoom in to show individual markers
                                mapScale = Math.min(3, mapScale * 1.5);
                                mapX = rect.width / 2 - (cluster.markers[0].x * mapScale);
                                mapY = rect.height / 2 - (cluster.markers[0].y * mapScale);
                                updateMapTransform();
                            }};
                            mapOverlay.appendChild(circle);
                            
                            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                            text.setAttribute('x', cluster.x);
                            text.setAttribute('y', cluster.y + 4);
                            text.setAttribute('fill', '#000');
                            text.setAttribute('font-size', '12px');
                            text.setAttribute('font-weight', 'bold');
                            text.setAttribute('text-anchor', 'middle');
                            text.setAttribute('class', 'map-cluster-text');
                            text.style.pointerEvents = 'none';
                            text.textContent = cluster.markers.length;
                            mapOverlay.appendChild(text);
                        }}
                    }});
                }} else {{
                    unclustered = markers;
                }}
                
                // Render individual markers
                unclustered.forEach(function(marker) {{
                    const screenX = centerX + marker.x * mapScale + mapX;
                    const screenY = centerY + marker.y * mapScale + mapY;
                    if (screenX < -50 || screenX > rect.width + 50 || screenY < -50 || screenY > rect.height + 50) return;
                    
                    const category = markerCategories[marker.category] || markerCategories['other'];
                    const markerColor = marker.color || category.color;
                    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                    circle.setAttribute('cx', screenX);
                    circle.setAttribute('cy', screenY);
                    circle.setAttribute('r', 8);
                    circle.setAttribute('fill', markerColor);
                    circle.setAttribute('stroke', '#fff');
                    circle.setAttribute('stroke-width', 2);
                    circle.setAttribute('class', 'map-marker');
                    circle.setAttribute('data-marker-id', marker.id);
                    circle.style.cursor = 'pointer';
                    circle.style.pointerEvents = 'all';
                    circle.onclick = function(e) {{
                        e.stopPropagation();
                        const markerObj = markers.find(m => m.id === marker.id);
                        if (markerObj) showMarkerInfo(markerObj);
                    }};
                    mapOverlay.appendChild(circle);
                    
                    if (marker.name && labelsVisible) {{
                        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                        text.setAttribute('x', screenX);
                        text.setAttribute('y', screenY - 15);
                        text.setAttribute('fill', '#fff');
                        text.setAttribute('font-size', '12px');
                        text.setAttribute('text-anchor', 'middle');
                        text.setAttribute('class', 'map-marker-label');
                        text.style.pointerEvents = 'none';
                        text.textContent = marker.name;
                        mapOverlay.appendChild(text);
                    }}
                }});
            }}
            
            // Render annotations on overlay
            function renderAnnotations() {{
                if (!mapOverlay) return;
                const existingPaths = mapOverlay.querySelectorAll('.map-annotation, .map-annotation-delete');
                existingPaths.forEach(p => p.remove());
                
                const rect = mapContainer.getBoundingClientRect();
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                annotations.forEach(function(annotation) {{
                    if (!annotation.points || annotation.points.length < 2) return;
                    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                    let pathData = 'M ';
                    annotation.points.forEach(function(point, idx) {{
                        const screenX = centerX + point.x * mapScale + mapX;
                        const screenY = centerY + point.y * mapScale + mapY;
                        pathData += (idx === 0 ? '' : ' L ') + screenX + ',' + screenY;
                    }});
                    path.setAttribute('d', pathData);
                    path.setAttribute('fill', 'none');
                    path.setAttribute('stroke', annotation.color || '#9C27B0');
                    path.setAttribute('stroke-width', Math.max(3, (annotation.width || 2) * mapScale)); // Make stroke wider for easier clicking
                    path.setAttribute('class', 'map-annotation');
                    path.setAttribute('data-annotation-id', annotation.id);
                    path.style.pointerEvents = 'all'; // Changed from 'stroke' to 'all' for better click detection
                    path.style.cursor = 'pointer';
                    path.onclick = function(e) {{
                        e.stopPropagation();
                        e.preventDefault();
                        if (confirm('Delete this drawing?')) {{
                            annotations = annotations.filter(a => a.id !== annotation.id);
                            saveMapData();
                            renderAnnotations();
                        }}
                    }};
                    mapOverlay.appendChild(path);
                    
                    // Add delete button at the end of the path
                    const lastPoint = annotation.points[annotation.points.length - 1];
                    const lastScreenX = centerX + lastPoint.x * mapScale + mapX;
                    const lastScreenY = centerY + lastPoint.y * mapScale + mapY;
                    const deleteBtn = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                    deleteBtn.setAttribute('cx', lastScreenX);
                    deleteBtn.setAttribute('cy', lastScreenY);
                    deleteBtn.setAttribute('r', Math.max(8, 6 * mapScale)); // Scale delete button with zoom
                    deleteBtn.setAttribute('fill', '#F44336');
                    deleteBtn.setAttribute('stroke', '#fff');
                    deleteBtn.setAttribute('stroke-width', 1);
                    deleteBtn.setAttribute('class', 'map-annotation-delete');
                    deleteBtn.style.cursor = 'pointer';
                    deleteBtn.style.pointerEvents = 'all';
                    deleteBtn.onclick = function(e) {{
                        e.stopPropagation();
                        e.preventDefault();
                        if (confirm('Delete this drawing?')) {{
                            annotations = annotations.filter(a => a.id !== annotation.id);
                            saveMapData();
                            renderAnnotations();
                        }}
                    }};
                    mapOverlay.appendChild(deleteBtn);
                }});
            }}
            
            // toggleMarkerMode, toggleAnnotationMode, toggleMapLabels are already defined and exposed above
            
            // Show marker dialog (for add or edit)
            function showMarkerDialog(mapCoords, callback, existingMarker) {{
                // Close any existing dialogs first
                const existingDialogs = document.querySelectorAll('[id^="markerDialog"]');
                existingDialogs.forEach(d => d.remove());
                
                const category = existingMarker ? (markerCategories[existingMarker.category] || markerCategories['other']) : markerCategories['other'];
                const currentColor = existingMarker && existingMarker.color ? existingMarker.color : category.color;
                const presetColors = ['#4CAF50', '#F44336', '#FF9800', '#2196F3', '#9C27B0', '#FFD700', '#00BCD4', '#FF5722', '#9E9E9E', '#795548'];
                
                const dialog = document.createElement('div');
                dialog.id = 'markerDialog';
                dialog.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.95); border: 2px solid #FFD700; border-radius: 10px; padding: 20px; z-index: 10000; min-width: 300px; color: #fff;';
                dialog.innerHTML = `
                    <h3 style="color: #FFD700; margin-top: 0;">${existingMarker ? 'Edit Marker' : 'Add Marker'}</h3>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; color: #aaa; margin-bottom: 5px;">Name:</label>
                        <input type="text" id="markerNameInput" style="width: 100%; padding: 8px; background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; color: #fff; font-size: 0.9em; box-sizing: border-box;" placeholder="Location name" value="${existingMarker ? (existingMarker.name || '').replace(/"/g, '&quot;') : ''}">
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; color: #aaa; margin-bottom: 5px;">Category:</label>
                        <select id="markerCategoryInput" onchange="updateMarkerColorFromCategory()" style="width: 100%; padding: 8px; background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; color: #fff; font-size: 0.9em; box-sizing: border-box;">
                            <option value="city" ${existingMarker && existingMarker.category === 'city' ? 'selected' : ''}>🏙️ City</option>
                            <option value="dungeon" ${existingMarker && existingMarker.category === 'dungeon' ? 'selected' : ''}>🏰 Dungeon</option>
                            <option value="landmark" ${existingMarker && existingMarker.category === 'landmark' ? 'selected' : ''}>🗿 Landmark</option>
                            <option value="other" ${existingMarker && existingMarker.category === 'other' ? 'selected' : (!existingMarker ? 'selected' : '')}>📍 Other</option>
                        </select>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; color: #aaa; margin-bottom: 5px;">Color:</label>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;">
                            ${presetColors.map(c => `<div onclick="selectMarkerColor('${c}')" style="width: 30px; height: 30px; background: ${c}; border: 2px solid ${c === currentColor ? '#fff' : 'transparent'}; border-radius: 50%; cursor: pointer; box-shadow: 0 0 0 ${c === currentColor ? '2px' : '0'} rgba(255,255,255,0.5);"></div>`).join('')}
                        </div>
                        <input type="color" id="markerColorInput" value="${currentColor}" onchange="selectMarkerColor(this.value)" style="width: 100%; height: 40px; padding: 0; background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; cursor: pointer; box-sizing: border-box;">
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; color: #aaa; margin-bottom: 5px;">Notes:</label>
                        <textarea id="markerNotesInput" style="width: 100%; padding: 8px; background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; color: #fff; font-size: 0.9em; min-height: 60px; resize: vertical; box-sizing: border-box;" placeholder="Additional notes...">${existingMarker ? (existingMarker.notes || '').replace(/</g, '&lt;').replace(/>/g, '&gt;') : ''}</textarea>
                    </div>
                    <div style="display: flex; gap: 10px; justify-content: flex-end;">
                        <button onclick="document.getElementById('markerDialog').remove(); delete window.confirmMarkerDialog; delete window.selectMarkerColor; delete window.updateMarkerColorFromCategory;" style="padding: 8px 16px; background: rgba(244,67,54,0.3); border: 1px solid #F44336; border-radius: 4px; color: #fff; cursor: pointer;">Cancel</button>
                        <button onclick="window.confirmMarkerDialog()" style="padding: 8px 16px; background: rgba(76,175,80,0.3); border: 1px solid #4CAF50; border-radius: 4px; color: #fff; cursor: pointer;">${existingMarker ? 'Save' : 'Add'}</button>
                    </div>
                `;
                document.body.appendChild(dialog);
                document.getElementById('markerNameInput').focus();
                
                let selectedColor = currentColor;
                window.selectMarkerColor = function(color) {{
                    selectedColor = color;
                    document.getElementById('markerColorInput').value = color;
                    const presetDivs = dialog.querySelectorAll('div[onclick^="selectMarkerColor"]');
                    presetDivs.forEach(div => {{
                        const divColor = div.style.background;
                        div.style.border = divColor === color ? '2px solid #fff' : '2px solid transparent';
                        div.style.boxShadow = divColor === color ? '0 0 0 2px rgba(255,255,255,0.5)' : '0 0 0 0';
                    }});
                }};
                
                window.updateMarkerColorFromCategory = function() {{
                    const category = document.getElementById('markerCategoryInput').value;
                    const catColor = markerCategories[category]?.color || markerCategories['other'].color;
                    window.selectMarkerColor(catColor);
                }};
                
                window.confirmMarkerDialog = function() {{
                    const name = document.getElementById('markerNameInput').value.trim();
                    if (!name) {{
                        alert('Please enter a name');
                        return;
                    }}
                    const category = document.getElementById('markerCategoryInput').value;
                    const notes = document.getElementById('markerNotesInput').value.trim();
                    const color = selectedColor;
                    const dialogEl = document.getElementById('markerDialog');
                    if (dialogEl) dialogEl.remove();
                    delete window.confirmMarkerDialog;
                    delete window.selectMarkerColor;
                    delete window.updateMarkerColorFromCategory;
                    callback(name, category, notes, color);
                }};
            }}
            
            // Add marker at click position
            function addMarkerAt(x, y) {{
                const mapCoords = screenToMap(x, y);
                showMarkerDialog(mapCoords, function(name, category, notes, color) {{
                    const marker = {{
                        id: Date.now(),
                        name: name,
                        category: category,
                        notes: notes || '',
                        color: color,
                        x: mapCoords.x,
                        y: mapCoords.y
                    }};
                    markers.push(marker);
                    saveMapData();
                    renderMarkers();
                    updateLocationList();
                }});
            }}
            
            // Edit existing marker
            function editMarker(marker) {{
                showMarkerDialog(null, function(name, category, notes, color) {{
                    marker.name = name;
                    marker.category = category;
                    marker.notes = notes || '';
                    marker.color = color;
                    saveMapData();
                    renderMarkers();
                    updateLocationList();
                }}, marker);
            }}
            
            // Update location list with search
            function updateLocationList() {{
                if (!locationList) return;
                const filter = document.getElementById('markerCategoryFilter')?.value || 'all';
                const searchTerm = (document.getElementById('markerSearchInput')?.value || '').toLowerCase().trim();
                
                let filtered = filter === 'all' ? markers : markers.filter(m => m.category === filter);
                if (searchTerm) {{
                    filtered = filtered.filter(m => 
                        m.name.toLowerCase().includes(searchTerm) || 
                        (m.notes && m.notes.toLowerCase().includes(searchTerm))
                    );
                }}
                
                if (filtered.length === 0) {{
                    locationList.innerHTML = '<p style="color: #666; font-size: 0.85em; font-style: italic;">No locations found.</p>';
                    return;
                }}
                locationList.innerHTML = '';
                filtered.forEach(function(marker) {{
                    const category = markerCategories[marker.category] || markerCategories['other'];
                    const markerColor = marker.color || category.color;
                    const item = document.createElement('div');
                    item.style.cssText = 'padding: 8px; background: rgba(0,0,0,0.3); border-radius: 4px; cursor: pointer; border-left: 3px solid ' + markerColor + '; margin-bottom: 5px;';
                    const hasNotes = marker.notes ? '📝' : '';
                    item.innerHTML = '<div style="display: flex; justify-content: space-between; align-items: center;"><div style="flex: 1;"><span style="font-size: 1.2em; margin-right: 5px;">' + category.icon + '</span><strong style="color: #fff; font-size: 0.9em;">' + marker.name + '</strong>' + (hasNotes ? ' <span style="color: #aaa; font-size: 0.8em;">' + hasNotes + '</span>' : '') + '</div><button onclick="event.stopPropagation(); deleteMarker(' + marker.id + ')" style="background: rgba(244,67,54,0.3); border: 1px solid #F44336; border-radius: 3px; color: #fff; padding: 2px 6px; font-size: 0.75em; cursor: pointer;">×</button></div>';
                    item.onclick = function(e) {{
                        if (!e.target.closest('button')) {{
                            zoomToMarker(marker);
                        }}
                    }};
                    locationList.appendChild(item);
                }});
            }}
            
            function filterMarkersByCategory() {{
                updateLocationList();
            }}
            
            function zoomToMarker(marker) {{
                const rect = mapContainer.getBoundingClientRect();
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                // Set zoom level first
                mapScale = Math.max(2, mapScale);
                // Center the marker: mapX/Y is offset from center, so we need to position the marker at center
                // The marker's world position * scale gives screen position, then we offset by mapX/Y
                // To center: centerX = marker.x * mapScale + mapX, so mapX = centerX - marker.x * mapScale
                mapX = centerX - (marker.x * mapScale);
                mapY = centerY - (marker.y * mapScale);
                updateMapTransform();
            }}
            
            // Show marker info dialog
            function showMarkerInfo(marker) {{
                // Close any existing dialogs first
                const existingDialogs = document.querySelectorAll('[id^="markerInfoDialog"]');
                existingDialogs.forEach(d => d.remove());
                
                const category = markerCategories[marker.category] || markerCategories['other'];
                const dialog = document.createElement('div');
                dialog.id = 'markerInfoDialog';
                dialog.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.95); border: 2px solid ' + category.color + '; border-radius: 10px; padding: 20px; z-index: 10000; min-width: 300px; max-width: 500px; color: #fff;';
                const notesHtml = marker.notes ? `<div style="margin-bottom: 10px;"><strong style="color: #aaa;">Notes:</strong><div style="color: #fff; margin-top: 5px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 4px; white-space: pre-wrap;">${marker.notes.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div></div>` : '';
                dialog.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="color: ${category.color}; margin: 0; display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 1.5em;">${category.icon}</span>
                            ${marker.name.replace(/</g, '&lt;').replace(/>/g, '&gt;')}
                        </h3>
                        <button onclick="document.getElementById('markerInfoDialog').remove()" style="background: transparent; border: none; color: #fff; font-size: 1.5em; cursor: pointer; padding: 0; width: 30px; height: 30px; line-height: 1;">×</button>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong style="color: #aaa;">Category:</strong> <span style="color: ${category.color};">${category.name}</span>
                    </div>
                    ${notesHtml}
                    <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 15px;">
                        <button onclick="editMarkerById(${marker.id}); document.getElementById('markerInfoDialog').remove();" style="padding: 6px 10px; background: rgba(255,152,0,0.3); border: 1px solid #FF9800; border-radius: 4px; color: #fff; cursor: pointer; font-size: 1.2em;" title="Edit">✏️</button>
                        <button onclick="deleteMarker(${marker.id}); document.getElementById('markerInfoDialog').remove();" style="padding: 6px 10px; background: rgba(244,67,54,0.3); border: 1px solid #F44336; border-radius: 4px; color: #fff; cursor: pointer; font-size: 1.2em;" title="Delete">🗑️</button>
                        <button onclick="zoomToMarkerById(${marker.id}); document.getElementById('markerInfoDialog').remove();" style="padding: 6px 10px; background: rgba(33,150,243,0.3); border: 1px solid #2196F3; border-radius: 4px; color: #fff; cursor: pointer; font-size: 1.2em;" title="Zoom To">🔍</button>
                        <button onclick="document.getElementById('markerInfoDialog').remove()" style="padding: 6px 10px; background: rgba(158,158,158,0.3); border: 1px solid #9E9E9E; border-radius: 4px; color: #fff; cursor: pointer; font-size: 1.2em;" title="Close">✕</button>
                    </div>
                `;
                document.body.appendChild(dialog);
            }}
            
            function editMarkerById(id) {{
                const marker = markers.find(m => m.id === id);
                if (marker) editMarker(marker);
            }}
            window.editMarkerById = editMarkerById;
            
            function zoomToMarkerById(id) {{
                const marker = markers.find(m => m.id === id);
                if (marker) zoomToMarker(marker);
            }}
            window.zoomToMarkerById = zoomToMarkerById;
            
            function deleteMarker(id) {{
                if (confirm('Delete this marker?')) {{
                    markers = markers.filter(m => m.id !== id);
                    saveMapData();
                    renderMarkers();
                    updateLocationList();
                }}
            }}
            
            // Annotation drawing
            function startAnnotation(x, y) {{
                if (!annotationMode) return;
                isDrawing = true;
                const mapCoords = screenToMap(x, y);
                currentPath = {{
                    id: Date.now(),
                    points: [mapCoords],
                    color: '#9C27B0',
                    width: 2
                }};
                annotations.push(currentPath);
            }}
            
            function addAnnotationPoint(x, y) {{
                if (!isDrawing || !currentPath) return;
                const mapCoords = screenToMap(x, y);
                currentPath.points.push(mapCoords);
                renderAnnotations();
            }}
            
            function finishAnnotation() {{
                if (isDrawing && currentPath && currentPath.points.length > 1) {{
                    saveMapData();
                }}
                isDrawing = false;
                currentPath = null;
            }}
            
            // Initialize
            loadMapData();
            updateUndoRedoButtons();
            updateMapTransform();
            
            // Expose remaining functions globally (toggleMarkerMode, toggleAnnotationMode, toggleMapLabels already exposed above)
            window.filterMarkersByCategory = filterMarkersByCategory;
            window.deleteMarker = deleteMarker;
            window.showMarkerInfo = showMarkerInfo;
            window.editMarker = editMarker;
        }})();
        </script>
        
        <div id="editorTab" class="tab-content">
            <div style="margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 10px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span id="autoSaveStatus" style="color: #4CAF50;">💾 Auto-saved</span>
                    <span id="unsavedChanges" style="color: #ff9800; display: none; margin-left: 15px;">⚠️ Unsaved changes</span>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button class="editor-btn" onclick="validateData()" style="background: #2196F3;">🔍 Validate Data</button>
                    <button class="editor-btn" onclick="showRelationshipIntelligence()" style="background: #9C27B0;">🧠 Relationship Intelligence</button>
                    <button class="editor-btn" onclick="exportToObsidian()" style="background: #607D8B;">📝 Export to Obsidian</button>
                </div>
            </div>
            
            <div class="editor-container">
                <div class="editor-sidebar">
                    <div style="margin-bottom: 15px;">
                        <h3 style="color: #FFD700; margin-top: 0; margin-bottom: 10px;">NPCs</h3>
                        <input type="text" id="editorSearch" placeholder="🔍 Search NPCs..." style="width: 100%; padding: 10px; margin-bottom: 10px; background: rgba(0,0,0,0.5); border: 2px solid rgba(255,255,255,0.3); border-radius: 6px; color: #fff;">
                        <div style="display: flex; gap: 5px; margin-bottom: 10px;">
                            <select id="editorFilterFaction" style="flex: 1; padding: 8px; background: rgba(0,0,0,0.5); border: 2px solid rgba(255,255,255,0.3); border-radius: 6px; color: #fff;">
                                <option value="">All Factions</option>
                            </select>
                            <select id="editorFilterStatus" style="flex: 1; padding: 8px; background: rgba(0,0,0,0.5); border: 2px solid rgba(255,255,255,0.3); border-radius: 6px; color: #fff;">
                                <option value="">All Status</option>
                                <option value="alive">Alive</option>
                                <option value="deceased">Deceased</option>
                                <option value="trapped">Trapped</option>
                            </select>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <input type="text" id="editorFilterTags" placeholder="Filter by tags..." style="width: 100%; padding: 8px; background: rgba(0,0,0,0.5); border: 2px solid rgba(255,255,255,0.3); border-radius: 6px; color: #fff;">
                        </div>
                        <div style="display: flex; gap: 5px; margin-bottom: 10px;">
                            <button class="editor-btn" onclick="addNewNPC()" style="flex: 1; background: #4CAF50; padding: 10px;">➕ Add</button>
                            <button class="editor-btn" onclick="showTemplates()" style="flex: 1; background: #FF9800; padding: 10px;">📋 Templates</button>
                        </div>
                        <div style="margin-bottom: 10px;">
                            <button class="editor-btn" onclick="toggleBulkMode()" style="width: 100%; background: #9C27B0; padding: 10px;">📦 Bulk Mode</button>
                        </div>
                        <div id="bulkActions" style="display: none; margin-bottom: 10px; padding: 10px; background: rgba(156,39,176,0.2); border-radius: 6px;">
                            <div style="margin-bottom: 5px; font-size: 0.9em; color: #ccc;">Selected: <span id="bulkCount">0</span></div>
                            <button class="editor-btn" onclick="bulkUpdateTags()" style="width: 100%; margin-bottom: 5px; padding: 8px; font-size: 0.9em;">🏷️ Update Tags</button>
                            <button class="editor-btn" onclick="bulkUpdateFaction()" style="width: 100%; margin-bottom: 5px; padding: 8px; font-size: 0.9em;">⚔️ Update Faction</button>
                            <button class="editor-btn" onclick="bulkUpdateStatus()" style="width: 100%; margin-bottom: 5px; padding: 8px; font-size: 0.9em;">💀 Update Status</button>
                            <button class="editor-btn" onclick="bulkDelete()" style="width: 100%; background: #f44336; padding: 8px; font-size: 0.9em;">🗑️ Delete Selected</button>
                        </div>
                    </div>
                    <div id="npcList" style="max-height: 60vh; overflow-y: auto;">
                        <!-- NPC list will be populated here -->
                    </div>
                </div>
                <div class="editor-main">
                    <div id="editorForm" style="display: none;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h2 id="editorTitle" style="color: #FFD700; margin: 0;">Edit NPC</h2>
                            <div>
                                <button class="editor-btn" onclick="copyNPC()" style="background: #607D8B; padding: 8px 16px; font-size: 0.9em;">📋 Copy NPC</button>
                                <button class="editor-btn" onclick="showRelationshipTemplates()" style="background: #FF9800; padding: 8px 16px; font-size: 0.9em;">🔗 Relationship Templates</button>
                            </div>
                        </div>
                        <form id="npcForm" onsubmit="saveNPC(event)">
                            <input type="hidden" id="npcId" />
                            
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                <div class="form-group">
                                    <label>Name *</label>
                                    <input type="text" id="npcName" required onchange="markUnsaved()" />
                                </div>
                                
                                <div class="form-group">
                                    <label>Faction</label>
                                    <input type="text" id="npcFaction" list="factionList" onchange="markUnsaved()" />
                                    <datalist id="factionList"></datalist>
                                </div>
                                
                                <div class="form-group">
                                    <label>Location</label>
                                    <input type="text" id="npcLocation" onchange="markUnsaved()" />
                                </div>
                                
                                <div class="form-group">
                                    <label>Status</label>
                                    <input type="text" id="npcStatus" list="statusList" onchange="markUnsaved()" />
                                    <datalist id="statusList">
                                        <option value="alive">alive</option>
                                        <option value="alive (trapped)">alive (trapped)</option>
                                        <option value="alive (transformed)">alive (transformed)</option>
                                        <option value="deceased">deceased</option>
                                        <option value="deceased (spirit bound)">deceased (spirit bound)</option>
                                        <option value="deceased (consciousness preserved)">deceased (consciousness preserved)</option>
                                        <option value="petrified (alive)">petrified (alive)</option>
                                    </datalist>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label>Portrait Path</label>
                                <div style="display: flex; gap: 10px;">
                                    <input type="text" id="npcPortrait" placeholder="../Images/filename.png" onchange="markUnsaved(); previewPortrait()" style="flex: 1;" />
                                    <div id="portraitPreview" style="width: 80px; height: 80px; border: 2px solid rgba(255,255,255,0.3); border-radius: 6px; background: rgba(0,0,0,0.3); display: none; background-size: cover; background-position: center;"></div>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label>Tags (comma-separated)</label>
                                <input type="text" id="npcTags" placeholder="noble, antagonist, archivist" list="tagSuggestions" onchange="markUnsaved()" />
                                <datalist id="tagSuggestions"></datalist>
                                <datalist id="npcNameList"></datalist>
                            </div>
                            
                            <div class="form-group">
                                <label>Notes</label>
                                <textarea id="npcNotes" rows="4" onchange="markUnsaved()"></textarea>
                            </div>
                            
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" id="npcSpoiler" onchange="markUnsaved()" /> Contains Spoilers
                                </label>
                            </div>
                            
                            <div class="form-group">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                    <h3 style="color: #FFD700; margin: 0;">Relationships</h3>
                                    <div>
                                        <button type="button" class="editor-btn" onclick="importRelationships()" style="background: #2196F3; padding: 8px 16px; font-size: 0.9em;">📥 Import</button>
                                        <button type="button" class="editor-btn" onclick="addRelationship()" style="background: #4CAF50; padding: 8px 16px; font-size: 0.9em;">➕ Add</button>
                                        <button type="button" class="editor-btn" onclick="toggleRelationshipCollapse()" style="background: #9E9E9E; padding: 8px 16px; font-size: 0.9em;" id="collapseBtn">📂 Collapse</button>
                                    </div>
                                </div>
                                <div id="relationshipsList" class="relationships-collapsible"></div>
                                <div id="relationshipValidation" style="margin-top: 10px; padding: 10px; background: rgba(244,67,54,0.2); border-radius: 6px; display: none;">
                                    <strong style="color: #f44336;">⚠️ Validation Errors:</strong>
                                    <ul id="relationshipErrors" style="margin: 5px 0; padding-left: 20px; color: #ffcdd2;"></ul>
                                </div>
                            </div>
                            
                            <div class="form-actions">
                                <button type="submit" class="editor-btn" style="background: #4CAF50;">💾 Save NPC</button>
                                <button type="button" class="editor-btn" onclick="cancelEdit()" style="background: #f44336;">❌ Cancel</button>
                                <button type="button" class="editor-btn" onclick="deleteNPC()" style="background: #ff9800;">🗑️ Delete NPC</button>
                            </div>
                        </form>
                    </div>
                    <div id="editorEmpty" style="text-align: center; padding: 50px; color: #ccc;">
                        <h3>Select an NPC to edit or create a new one</h3>
                        <p style="margin-top: 20px;">Use the search and filters in the sidebar to find NPCs quickly</p>
                    </div>
                </div>
            </div>
            <div style="margin-top: 20px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                <h3 style="color: #FFD700; margin-top: 0;">Export & Save</h3>
                <p style="color: #ccc; margin-bottom: 15px;">Export in different formats or regenerate the mind map.</p>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="editor-btn" onclick="exportJSON()" style="background: #2196F3;">📥 Export JSON</button>
                    <button class="editor-btn" onclick="exportCSV()" style="background: #4CAF50;">📊 Export CSV</button>
                    <button class="editor-btn" onclick="exportMarkdown()" style="background: #9C27B0;">📝 Export Markdown</button>
                    <button class="editor-btn" onclick="importFromFile()" style="background: #FF9800;">📤 Import JSON/CSV</button>
                    <button class="editor-btn" onclick="regenerateMindMap()" style="background: #607D8B;">🔄 Regenerate Mind Map</button>
                </div>
            </div>
        </div>
        
        <div id="inventoryTab" class="tab-content">
            <div style="padding: 20px;">
                <h2 style="color: #FFD700; margin-top: 0;">🎒 Inventory Tracker</h2>
                
                <!-- Party Gold -->
                <div style="margin-bottom: 30px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 10px; border: 2px solid rgba(255,255,255,0.2);">
                    <h3 style="color: #FFD700; margin-top: 0; display: flex; align-items: center; gap: 10px;">
                        💰 Party Gold
                        <input type="number" id="partyGold" value="0" min="0" step="0.01" 
                               style="margin-left: 10px; padding: 8px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.5); color: #fff; font-size: 1.2em; width: 150px;"
                               onchange="updatePartyGold()">
                        <span style="font-size: 0.8em; color: #ccc;">gp</span>
                    </h3>
                </div>
                
                <!-- Inventory Container - Tighter Layout with Items on Left -->
                <div style="display: grid; grid-template-columns: 300px 1fr; gap: 15px; margin-bottom: 15px;">
                    <!-- Left Column: Item Lookup Table (Compact) -->
                    <div style="padding: 10px; background: rgba(0,0,0,0.3); border-radius: 8px; border: 2px solid rgba(255,255,255,0.2);">
                        <h3 style="color: #FFD700; margin-top: 0; font-size: 1em; margin-bottom: 10px;">📚 Items</h3>
                        <div style="margin-bottom: 10px;">
                            <input type="text" id="itemSearch" placeholder="Search..." 
                                   style="width: 100%; padding: 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.5); color: #fff; font-size: 0.85em;"
                                   oninput="filterItems()">
                            <select id="itemCategory" onchange="filterItems()" 
                                    style="margin-top: 6px; width: 100%; padding: 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.5); color: #fff; font-size: 0.85em;">
                                <option value="">All Categories</option>
                                <option value="weapon">Weapons</option>
                                <option value="armor">Armor</option>
                                <option value="tool">Tools</option>
                                <option value="consumable">Consumables</option>
                                <option value="magic">Magic</option>
                                <option value="misc">Misc</option>
                            </select>
                            <select id="itemType" onchange="filterItems()" 
                                    style="margin-top: 6px; width: 100%; padding: 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.5); color: #fff; font-size: 0.85em;">
                                <option value="">All Types</option>
                                <option value="mundane">Mundane</option>
                                <option value="magic">Magic</option>
                            </select>
                            <select id="itemRarity" onchange="filterItems()" 
                                    style="margin-top: 6px; width: 100%; padding: 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.5); color: #fff; font-size: 0.85em;">
                                <option value="">All Rarities</option>
                                <option value="Common">Common</option>
                                <option value="Uncommon">Uncommon</option>
                                <option value="Rare">Rare</option>
                                <option value="Very Rare">Very Rare</option>
                                <option value="Legendary">Legendary</option>
                                <option value="Artifact">Artifact</option>
                            </select>
                            <select id="itemSort" onchange="filterItems()" 
                                    style="margin-top: 6px; width: 100%; padding: 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.5); color: #fff; font-size: 0.85em;">
                                <option value="name">Sort: Name</option>
                                <option value="weight">Sort: Weight</option>
                                <option value="cost">Sort: Cost</option>
                                <option value="rarity">Sort: Rarity</option>
                                <option value="category">Sort: Category</option>
                            </select>
                        </div>
                        <div id="itemLookup" style="max-height: calc(100vh - 400px); overflow-y: auto; -webkit-overflow-scrolling: touch; display: flex; flex-direction: column; gap: 4px; touch-action: pan-y;">
                            <!-- Items will be populated by JavaScript -->
                        </div>
                        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2);">
                            <button onclick="addSelectedItems()" id="addSelectedBtn" style="width: 100%; padding: 6px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em; opacity: 0.5;" disabled>Add Selected (<span id="selectedCount">0</span>)</button>
                        </div>
                    </div>
                    
                    <!-- Right Column: Player Inventories and Containers -->
                    <div style="display: flex; flex-direction: column; gap: 10px;">
                        <!-- Player Inventories -->
                        <div style="padding: 10px; background: rgba(0,0,0,0.3); border-radius: 8px; border: 2px solid rgba(255,255,255,0.2);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; cursor: pointer;" onclick="toggleSection('playersSection')">
                                <h3 style="color: #FFD700; margin: 0; font-size: 1em;">👥 Players <span id="playerCountBadge" style="background: rgba(76,175,80,0.3); color: #4caf50; padding: 2px 8px; border-radius: 10px; font-size: 0.7em; font-weight: bold; margin-left: 8px;"></span></h3>
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <span id="playersSectionToggle" style="font-size: 1.2em;">▼</span>
                                    <button onclick="event.stopPropagation(); addPlayer()" style="padding: 6px 12px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em;">➕ Add</button>
                                </div>
                            </div>
                            <div id="playersSection" style="display: block;">
                                <div id="playerInventories" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                                    <!-- Player inventories will be dynamically generated -->
                                </div>
                            </div>
                        </div>
                        
                        <!-- Special Containers -->
                        <div style="padding: 10px; background: rgba(0,0,0,0.3); border-radius: 8px; border: 2px solid rgba(255,255,255,0.2);">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; cursor: pointer;" onclick="toggleSection('bagSection')">
                                <h3 style="color: #FFD700; margin: 0; font-size: 1em;">📦 Bag of Holding</h3>
                                <span id="bagSectionToggle" style="font-size: 1.2em;">▼</span>
                            </div>
                            <div id="bagSection" style="display: block;">
                                <div style="font-size: 0.8em; color: #ccc; margin-bottom: 8px;">Weight: <span id="bagWeight">0</span> / 500 lbs</div>
                                <div id="bagOfHolding" class="inventory-container" 
                                     ondrop="drop(event, 'bagOfHolding')" 
                                     ondragover="allowDrop(event)"
                                     ontouchmove="if(event.touches.length === 1) handleTouchMove(event)"
                                     ontouchend="if(event.changedTouches.length === 1) handleTouchEnd(event)"
                                     style="min-height: 100px; max-height: 200px; overflow-y: auto; -webkit-overflow-scrolling: touch; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 5px; border: 2px dashed rgba(255,255,255,0.3); touch-action: pan-y;">
                                    <p style="color: #888; text-align: center; margin: 10px 0; font-size: 0.85em;">Drop items here</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Define switchTab immediately so it's available for onclick handlers
        function switchTab(tabName) {
            // Hide all tabs and content
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');
            tabs.forEach(function(t) { t.classList.remove('active'); });
            contents.forEach(function(t) {
                t.classList.remove('active');
                t.style.display = 'none';
            });
            
            // Show selected tab button
            let tabIndex = -1;
            if (tabName === 'cards') tabIndex = 0;
            else if (tabName === 'mindmap') tabIndex = 1;
            else if (tabName === 'editor') tabIndex = 2;
            else if (tabName === 'inventory') tabIndex = 3;
            
            if (tabIndex >= 0 && tabs[tabIndex]) {
                tabs[tabIndex].classList.add('active');
            }
            
            // Show selected content
            const contentId = tabName + 'Tab';
            const content = document.getElementById(contentId);
            if (content) {
                content.classList.add('active');
                content.style.display = 'block';
                
                // Initialize tab-specific functionality (will be defined later)
                if (typeof window.initTabContent === 'function') {
                    window.initTabContent(tabName);
                }
            }
        }
        
        // Make switchTab available globally immediately
        window.switchTab = switchTab;
        
        // NPC Data
        const npcData = """ + json.dumps(npcs, ensure_ascii=False).replace('</script>', '<\\/script>') + """;
        const factionColors = """ + json.dumps(faction_colors, ensure_ascii=False).replace('</script>', '<\\/script>') + """;
        const relationshipTypes = """ + json.dumps(relationship_types, ensure_ascii=False).replace('</script>', '<\\/script>') + """;
        const factionsList = """ + json.dumps(factions, ensure_ascii=False).replace('</script>', '<\\/script>') + """;
        
        // Simple helper for optional elements (localStorage, external libs)
        function getEl(id) {
            return document.getElementById(id);
        }
        
        // Card View Functions - elements cached at initialization
        let npcCards = [];
        let factionFilter, statusFilter, searchBox;
        
        function updateStats() {
            const statsEl = getEl('stats');
            if (statsEl) {
                const visible = document.querySelectorAll('.npc-card:not(.hidden)').length;
                statsEl.textContent = 'Showing ' + visible + ' of ' + npcCards.length + ' NPCs';
            }
        }
        
        function filterNPCs() {
            // Refresh cards if DOM changed
            npcCards = Array.from(document.querySelectorAll('.npc-card'));
            
            const factionValue = factionFilter ? factionFilter.value : '';
            const statusValue = statusFilter ? statusFilter.value : '';
            const searchValue = searchBox ? searchBox.value.toLowerCase() : '';
            const groupBy = getEl('groupBy') ? getEl('groupBy').value : '';
            const sortBy = getEl('sortBy') ? getEl('sortBy').value : '';
            const spoilerFree = getEl('spoilerFreeMode') ? getEl('spoilerFreeMode').checked : false;
            
            const container = getEl('npcContainer');
            if (!container) return;
            
            // Filter cards
            npcCards.forEach(function(card) {
                const faction = card.dataset.faction;
                const status = card.dataset.status;
                const name = card.dataset.name;
                const location = card.dataset.location || '';
                const tags = card.dataset.tags || '';
                const isSpoiler = card.dataset.spoiler === 'true';
                
                let show = true;
                
                if (factionValue && faction !== factionValue) show = false;
                if (statusValue && status !== statusValue) show = false;
                if (searchValue && name.indexOf(searchValue) === -1 && location.indexOf(searchValue) === -1 && tags.indexOf(searchValue) === -1) show = false;
                if (spoilerFree && isSpoiler) show = false;
                
                if (show) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
            
            // Sort cards
            const visibleCards = Array.from(npcCards).filter(function(card) {
                return !card.classList.contains('hidden');
            });
            
            visibleCards.sort(function(a, b) {
                if (sortBy === 'name') {
                    return (a.dataset.name || '').localeCompare(b.dataset.name || '');
                } else if (sortBy === 'name-desc') {
                    return (b.dataset.name || '').localeCompare(a.dataset.name || '');
                } else if (sortBy === 'faction') {
                    const factionCompare = (a.dataset.faction || '').localeCompare(b.dataset.faction || '');
                    return factionCompare !== 0 ? factionCompare : (a.dataset.name || '').localeCompare(b.dataset.name || '');
                } else if (sortBy === 'location') {
                    const locCompare = (a.dataset.location || '').localeCompare(b.dataset.location || '');
                    return locCompare !== 0 ? locCompare : (a.dataset.name || '').localeCompare(b.dataset.name || '');
                } else if (sortBy === 'status') {
                    const statusCompare = (a.dataset.status || '').localeCompare(b.dataset.status || '');
                    return statusCompare !== 0 ? statusCompare : (a.dataset.name || '').localeCompare(b.dataset.name || '');
                }
                return 0;
            });
            
            // Group by location/faction/status
            if (groupBy === 'location') {
                groupByLocation(visibleCards);
            } else if (groupBy === 'faction') {
                groupByFaction(visibleCards);
            } else if (groupBy === 'status') {
                groupByStatus(visibleCards);
            } else {
                // No grouping - just sort
                container.innerHTML = '<div class="npc-grid" id="npcGrid"></div>';
                const newGrid = getEl('npcGrid');
                visibleCards.forEach(function(card) {
                    if (newGrid && card) newGrid.appendChild(card);
                });
            }
            
            updateStats();
        }
        
        function groupByLocation(cards) {
            const groups = {};
            cards.forEach(function(card) {
                const location = card.dataset.location || 'Unknown';
                if (!groups[location]) groups[location] = [];
                groups[location].push(card);
            });
            
            const container = getEl('npcContainer');
            if (!container) return;
            container.innerHTML = '';
            
            Object.keys(groups).sort().forEach(function(location) {
                const groupDiv = document.createElement('div');
                groupDiv.className = 'location-group';
                groupDiv.innerHTML = '<div class="location-group-title">📍 ' + location + '</div><div class="npc-grid"></div>';
                const groupGrid = groupDiv.querySelector('.npc-grid');
                groups[location].forEach(function(card) {
                    if (groupGrid && card) groupGrid.appendChild(card);
                });
                container.appendChild(groupDiv);
            });
        }
        
        function groupByFaction(cards) {
            const groups = {};
            cards.forEach(function(card) {
                const faction = card.dataset.faction || 'Unknown';
                if (!groups[faction]) groups[faction] = [];
                groups[faction].push(card);
            });
            
            const container = getEl('npcContainer');
            if (!container) return;
            container.innerHTML = '';
            
            Object.keys(groups).sort().forEach(function(faction) {
                const groupDiv = document.createElement('div');
                groupDiv.className = 'location-group';
                groupDiv.innerHTML = '<div class="location-group-title">🏛️ ' + faction + '</div><div class="npc-grid"></div>';
                const groupGrid = groupDiv.querySelector('.npc-grid');
                groups[faction].forEach(function(card) {
                    if (groupGrid && card) groupGrid.appendChild(card);
                });
                container.appendChild(groupDiv);
            });
        }
        
        function groupByStatus(cards) {
            const groups = {};
            cards.forEach(function(card) {
                const status = card.dataset.status || 'unknown';
                if (!groups[status]) groups[status] = [];
                groups[status].push(card);
            });
            
            const container = getEl('npcContainer');
            if (!container) return;
            container.innerHTML = '';
            
            const statusOrder = ['alive', 'alive (trapped)', 'alive (transformed)', 'deceased', 'deceased (spirit bound)', 'deceased (consciousness preserved)', 'petrified (alive)', 'trapped', 'unknown'];
            const sortedStatuses = Object.keys(groups).sort(function(a, b) {
                const aIndex = statusOrder.indexOf(a);
                const bIndex = statusOrder.indexOf(b);
                if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
                if (aIndex !== -1) return -1;
                if (bIndex !== -1) return 1;
                return a.localeCompare(b);
            });
            
            sortedStatuses.forEach(function(status) {
                const groupDiv = document.createElement('div');
                groupDiv.className = 'location-group';
                groupDiv.innerHTML = '<div class="location-group-title">⚡ ' + status.charAt(0).toUpperCase() + status.slice(1) + '</div><div class="npc-grid"></div>';
                
                const groupGrid = groupDiv.querySelector('.npc-grid');
                if (groupGrid) {
                    groups[status].forEach(function(card) {
                        if (card) groupGrid.appendChild(card);
                    });
                }
                
                container.appendChild(groupDiv);
            });
        }
        
        function exportToImage() {
            const container = getEl('npcContainer');
            if (!container) {
                alert('Cannot export: container not found');
                return;
            }
            
            if (typeof html2canvas === 'undefined') {
                alert('html2canvas library not loaded. Please refresh the page.');
                return;
            }
            
            html2canvas(container, {
                backgroundColor: '#0f2027',
                scale: 2,
                logging: false,
                useCORS: true,
                allowTaint: true
            }).then(function(canvas) {
                const link = document.createElement('a');
                link.download = 'npc_mindmap_' + new Date().getTime() + '.png';
                link.href = canvas.toDataURL('image/png');
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }).catch(function(error) {
                console.error('Export failed:', error);
                alert('Export failed: ' + (error.message || 'Unknown error'));
            });
        }
        
        function highlightNPC(npcName) {
            if (!npcName) return;
            // Refresh cards in case DOM changed
            npcCards = Array.from(document.querySelectorAll('.npc-card'));
            npcCards.forEach(function(card) { 
                if (card) card.style.border = ''; 
            });
            
            let found = false;
            npcCards.forEach(function(card) {
                const nameEl = card ? card.querySelector('.npc-name') : null;
                if (nameEl && nameEl.textContent === npcName) {
                    card.style.border = '3px solid #FFD700';
                    try {
                        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    } catch(e) {
                        card.scrollIntoView(); // Fallback for older browsers
                    }
                    found = true;
                }
            });
            if (!found) {
                console.warn('NPC not found for highlighting:', npcName);
            }
        }
        
        
        // Mind Map Functions
        function initMindMap() {
            if (typeof npcData === 'undefined' || !npcData || Object.keys(npcData).length === 0) {
                console.error('npcData is not available or empty');
                return;
            }
            
            console.log('Initializing mind map with', Object.keys(npcData).length, 'NPCs');
            const nodes = [];
            const edges = [];
            const nodeMap = {};
            
            let nodeId = 0;
            for (const npcId in npcData) {
                if (!npcData.hasOwnProperty(npcId)) continue;
                const npc = npcData[npcId];
                if (!npc || typeof npc !== 'object') {
                    console.warn('Skipping invalid NPC:', npcId);
                    continue;
                }
                const faction = npc.faction || 'Unknown';
                const status = npc.status || 'unknown';
                const color = factionColors[faction] || '#808080';
                
                nodes.push({
                    id: nodeId,
                    label: npc.name || npcId,
                    title: (npc.name || npcId) + '\\nFaction: ' + faction + '\\nStatus: ' + status + '\\nLocation: ' + (npc.location || 'Unknown'),
                    color: {
                        background: color,
                        border: '#FFFFFF',
                        highlight: {
                            background: color,
                            border: '#FFD700'
                        }
                    },
                    font: {
                        size: 20,
                        face: 'Arial',
                        color: '#FFFFFF'
                    },
                    borderWidth: 3,
                    shape: 'box',
                    size: 35,  // Slightly larger nodes for better spacing
                    margin: 10  // Add margin around nodes to prevent overlap
                });
                
                nodeMap[npcId] = nodeId;
                nodeId++;
            }
            
            let edgeId = 0;
            for (const npcId in npcData) {
                if (!npcData.hasOwnProperty(npcId)) continue;
                const npc = npcData[npcId];
                const relationships = npc.relationships || {};
                const sourceNodeId = nodeMap[npcId];
                
                for (const relType in relationships) {
                    if (!relationships.hasOwnProperty(relType)) continue;
                    const targets = relationships[relType];
                    const targetList = Array.isArray(targets) ? targets : [targets];
                    
                    for (let i = 0; i < targetList.length; i++) {
                        const targetId = targetList[i];
                        if (nodeMap.hasOwnProperty(targetId)) {
                            const targetNodeId = nodeMap[targetId];
                            
                            let edgeColor = '#9E9E9E';
                            let width = 2;
                            
                            if (relType.indexOf('enemy') !== -1 || relType.indexOf('feeds_on') !== -1) {
                                edgeColor = '#f44336';
                                width = 3;
                            } else if (relType.indexOf('ally') !== -1 || relType.indexOf('works_with') !== -1) {
                                edgeColor = '#4CAF50';
                                width = 3;
                            } else if (relType.indexOf('controls') !== -1 || relType.indexOf('serves') !== -1 || relType.indexOf('trapped_by') !== -1) {
                                edgeColor = '#FF9800';
                                width = 3;
                            }
                            
                            edges.push({
                                id: edgeId,
                                from: sourceNodeId,
                                to: targetNodeId,
                                label: relType.replace(/_/g, ' '),
                                color: {
                                    color: edgeColor,
                                    highlight: '#FFD700'
                                },
                                width: width,
                                font: {
                                    size: 16,
                                    color: '#FFFFFF',
                                    strokeWidth: 3,
                                    strokeColor: '#000000',
                                    align: 'middle'
                                },
                                arrows: {
                                    to: {
                                        enabled: true,
                                        scaleFactor: 1.0,  // Halved from 2.0 for better readability
                                        type: 'arrow'
                                    }
                                },
                                smooth: {
                                    type: 'curvedCW',
                                    roundness: 0.3
                                }
                            });
                            
                            edgeId++;
                        }
                    }
                }
            }
            
            const container = getEl('mindmapContainer');
            if (!container || typeof vis === 'undefined' || !vis.Network) {
                console.error('Mind map container or vis.js not available');
                return;
            }
            
            const networkData = { nodes: nodes, edges: edges };
            
            // Performance optimization: adjust settings based on graph size
            const totalNodes = nodes.length;
            const totalEdges = edges.length;
            const isLargeGraph = totalNodes > 50 || totalEdges > 100;
            const isVeryLargeGraph = totalNodes > 100 || totalEdges > 200;
            
            // Optimize physics for large graphs - much more aggressive settings
            let physicsConfig = {
                enabled: true,
                stabilization: { 
                    enabled: true, 
                    iterations: isVeryLargeGraph ? 20 : (isLargeGraph ? 30 : 200),  // Much fewer iterations
                    fit: true,
                    updateInterval: isVeryLargeGraph ? 50 : (isLargeGraph ? 30 : 5),  // Much less frequent updates
                    onlyDynamicEdges: isVeryLargeGraph  // Only stabilize dynamic edges for very large graphs
                },
                barnesHut: { 
                    gravitationalConstant: isVeryLargeGraph ? -20000 : (isLargeGraph ? -15000 : -8000),  // Even stronger repulsion to spread nodes
                    centralGravity: isVeryLargeGraph ? 0.005 : (isLargeGraph ? 0.01 : 0.03),  // Minimal central gravity to prevent clustering
                    springLength: isVeryLargeGraph ? 200 : (isLargeGraph ? 250 : 300),  // Much longer springs for more spacing
                    springConstant: isVeryLargeGraph ? 0.002 : (isLargeGraph ? 0.003 : 0.015),  // Much weaker springs for more flexibility
                    damping: isVeryLargeGraph ? 0.35 : (isLargeGraph ? 0.3 : 0.1),  // More damping
                    avoidOverlap: 1.0  // Strong overlap avoidance
                }
            };
            
            // Optimize visual settings for large graphs
            const showEdgeLabels = !isLargeGraph;  // Hide labels on large graphs for performance
            const useSmoothEdges = !isLargeGraph;  // Use straight edges for large graphs
            const showShadows = !isLargeGraph;  // Disable shadows for large graphs
            
            const options = {
                nodes: {
                    shape: 'box',
                    font: { size: isLargeGraph ? 16 : 20, face: 'Arial', color: '#FFFFFF' },
                    borderWidth: 3,
                    shadow: showShadows ? { enabled: true, color: 'rgba(0,0,0,0.5)', size: 10, x: 5, y: 5 } : { enabled: false },
                    margin: 15,  // Increased margin to prevent overlap
                    chosen: {
                        node: function(values, id, selected, hovering) {
                            if (hovering) {
                                values.size = 40;
                            }
                        }
                    }
                },
                edges: {
                    arrows: { 
                        to: { 
                            enabled: true, 
                            scaleFactor: 1.0,  // Halved from 2.0 for better readability
                            type: 'arrow'
                        } 
                    },
                    font: showEdgeLabels ? { size: 16, color: '#FFFFFF', strokeWidth: 3, strokeColor: '#000000', align: 'middle' } : { size: 0 },
                    label: showEdgeLabels ? undefined : '',  // Hide labels for performance
                    smooth: useSmoothEdges ? { type: 'curvedCW', roundness: 0.3 } : false,  // Straight edges for performance
                    shadow: showShadows ? { enabled: true, color: 'rgba(0,0,0,0.3)', size: 5 } : { enabled: false },
                    width: 2  // Base width that will scale
                },
                physics: physicsConfig,
                interaction: { 
                    hover: !isVeryLargeGraph,  // Disable hover for very large graphs
                    tooltipDelay: isVeryLargeGraph ? 300 : 100, 
                    zoomView: true, 
                    dragView: true,
                    selectConnectedEdges: !isVeryLargeGraph,  // Disable for very large graphs
                    hideEdgesOnDrag: isVeryLargeGraph,  // Hide edges while dragging for performance
                    hideEdgesOnZoom: isVeryLargeGraph  // Hide edges while zooming for performance
                },
                layout: { improvedLayout: true, hierarchical: { enabled: false } }
            };
            
            window.network = new vis.Network(container, networkData, options);
            
            // Store original options for toggling
            window.mindMapOptions = options;
            window.mindMapData = networkData;
            window.showEdgeLabelsState = showEdgeLabels;
            window.physicsEnabled = true;
            
            // Performance: Show loading message during stabilization
            if (isLargeGraph) {
                const loadingMsg = document.createElement('div');
                loadingMsg.id = 'mindmapLoading';
                loadingMsg.style.cssText = 'position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.8); color: #FFD700; padding: 20px; border-radius: 10px; z-index: 2000; font-size: 1.2em; text-align: center;';
                loadingMsg.innerHTML = 'Rendering mind map...<br><small>Optimizing for ' + totalNodes + ' nodes and ' + totalEdges + ' connections</small>';
                container.style.position = 'relative';
                container.appendChild(loadingMsg);
                
                let stabilizationTimeout;
                let progressUpdate;
                let iterationCount = 0;
                
                // Update progress during stabilization
                window.network.on('stabilizationProgress', function(params) {
                    iterationCount = params.iterations;
                    if (loadingMsg && iterationCount % 10 === 0) {
                        const progress = Math.min(100, Math.round((iterationCount / physicsConfig.stabilization.iterations) * 100));
                        loadingMsg.innerHTML = 'Rendering mind map... ' + progress + '%<br><small>Iteration ' + iterationCount + ' of ' + physicsConfig.stabilization.iterations + '</small>';
                    }
                });
                
                // Remove loading message after stabilization
                window.network.on('stabilizationEnd', function() {
                    const loading = getEl('mindmapLoading');
                    if (loading) {
                        loading.innerHTML = 'Rendering complete!<br><small>Physics paused for better performance</small>';
                        setTimeout(function() {
                            if (loading && loading.parentNode) loading.remove();
                        }, 1500);
                    }
                    if (stabilizationTimeout) clearTimeout(stabilizationTimeout);
                    
                    // Auto-disable physics for very large graphs after stabilization
                    if (autoDisablePhysics && window.network) {
                        window.network.setOptions({{ physics: {{ enabled: false }} }});
                        window.physicsEnabled = false;
                        const btn = getEl('togglePhysics');
                        if (btn) btn.textContent = 'Resume Physics';
                    }
                });
                
                // Safety timeout: remove loading message and disable physics after 15 seconds
                stabilizationTimeout = setTimeout(function() {
                    const loading = getEl('mindmapLoading');
                    if (loading) {
                        loading.innerHTML = 'Rendering complete (using optimized layout)<br><small>Physics paused for better performance</small>';
                        setTimeout(function() {
                            if (loading && loading.parentNode) loading.remove();
                        }, 2000);
                    }
                    // Force disable physics if still running
                    if (window.network && window.physicsEnabled) {
                        window.network.setOptions({{ physics: {{ enabled: false }} }});
                        window.physicsEnabled = false;
                        const btn = getEl('togglePhysics');
                        if (btn) btn.textContent = 'Resume Physics';
                    }
                }, 15000);  // 15 second timeout (reduced from 30)
            }
            
            if (nodes.length === 0) {
                console.warn('No nodes to display in mind map');
                return;
            }
            
            // Add helper functions for performance controls
            window.toggleEdgeLabels = function() {
                if (!window.network) return;
                window.showEdgeLabelsState = !window.showEdgeLabelsState;
                const update = {
                    edges: {
                        font: window.showEdgeLabelsState ? { size: 16, color: '#FFFFFF', strokeWidth: 3, strokeColor: '#000000', align: 'middle' } : { size: 0 },
                        label: window.showEdgeLabelsState ? undefined : ''
                    }
                };
                window.network.setOptions(update);
                const btn = getEl('toggleEdgeLabels');
                if (btn) btn.textContent = window.showEdgeLabelsState ? 'Hide Edge Labels' : 'Show Edge Labels';
            };
            
            window.togglePhysics = function() {
                if (!window.network) return;
                window.physicsEnabled = !window.physicsEnabled;
                window.network.setOptions({{ physics: {{ enabled: window.physicsEnabled }} }});
                const btn = getEl('togglePhysics');
                if (btn) btn.textContent = window.physicsEnabled ? 'Pause Physics' : 'Resume Physics';
            };
            
            window.fitNetwork = function() {
                if (!window.network) return;
                window.network.fit({ animation: { duration: 500, easingFunction: 'easeInOutQuad' } });
            };
            
            window.spreadNodes = function() {
                if (!window.network) return;
                // Temporarily enable physics with very strong repulsion to spread nodes
                window.network.setOptions({
                    physics: {
                        enabled: true,
                        barnesHut: {
                            gravitationalConstant: -25000,  // Very strong repulsion
                            centralGravity: 0.001,  // Almost no central gravity
                            springLength: 350,  // Very long springs
                            springConstant: 0.001,  // Very weak springs
                            damping: 0.4,
                            avoidOverlap: 1.2  // Strong overlap avoidance
                        },
                        stabilization: {
                            enabled: true,
                            iterations: 30,
                            fit: true
                        }
                    }
                });
                
                // Auto-disable after spreading (respect user's physics preference)
                setTimeout(function() {
                    if (window.network && !window.physicsEnabled) {
                        window.network.setOptions({ physics: { enabled: false } });
                    }
                }, 5000);  // Disable after 5 seconds
            };
            
            // Make arrows and edge widths scale with zoom level for better readability
            let lastZoomLevel = 1.0;
            let updateTimeout = null;
            
            window.network.on('zoom', function(params) {
                if (!params || params.scale === undefined) return;
                const zoomLevel = params.scale;
                
                // Debounce updates to avoid excessive redraws
                if (updateTimeout) clearTimeout(updateTimeout);
                updateTimeout = setTimeout(function() {
                    // Calculate arrow scale factor based on zoom (inverse relationship)
                    // Base scale is 1.0 (halved): at zoom 1.0, use 1.0; at zoom 2.0, use 0.5; at zoom 0.5, use 2.0
                    const baseScale = 1.0;
                    const arrowScale = Math.max(0.4, Math.min(2.5, baseScale / zoomLevel));
                    
                    // Also scale edge width inversely with zoom for better visibility
                    const baseWidth = 2;
                    const edgeWidth = Math.max(1, Math.min(5, baseWidth / zoomLevel));
                    
                    // Update arrow scale and edge width for all edges
                    // Force a redraw by updating options
                    try {
                        window.network.setOptions({
                            edges: {
                                arrows: {
                                    to: {
                                        enabled: true,
                                        scaleFactor: arrowScale,
                                        type: 'arrow'
                                    }
                                },
                                width: edgeWidth
                            }
                        });
                        // Force a redraw
                        window.network.redraw();
                    } catch (e) {
                        console.error('Error updating arrow scale:', e);
                    }
                    
                    lastZoomLevel = zoomLevel;
                }, 50);  // Debounce: update 50ms after zoom stops
            });
            
            window.network.on('click', function(params) {
                if (params && params.nodes && params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    // Use for loop instead of find for better compatibility
                    let node = null;
                    for (let i = 0; i < nodes.length; i++) {
                        if (nodes[i].id === nodeId) {
                            node = nodes[i];
                            break;
                        }
                    }
                    if (node && node.label) {
                        highlightNPC(node.label);
                    }
                }
            });
            
            console.log('Mind map initialized with', nodes.length, 'nodes and', edges.length, 'edges');
        }
        
        // Tab content initializer (called by switchTab)
        window.initTabContent = function(tabName) {
            if (tabName === 'cards') {
                if (typeof initCardView === 'function' && (npcCards.length === 0 || !factionFilter)) {
                    initCardView();
                }
            } else if (tabName === 'mindmap') {
                if (typeof window.network === 'undefined') {
                    if (typeof vis !== 'undefined' && vis.Network) {
                        setTimeout(function() { initMindMap(); }, 100);
                    } else {
                        setTimeout(function() { switchTab('mindmap'); }, 500);
                    }
                } else {
                    window.network.redraw();
                }
            } else if (tabName === 'editor') {
                if (typeof initEditor === 'function') {
                    initEditor();
                }
            } else if (tabName === 'inventory') {
                if (typeof initInventory === 'function') {
                    initInventory();
                }
            }
        };
        
        // Initialize card view when DOM is ready
        let cardViewInitialized = false;
        function initCardView() {
            if (cardViewInitialized) return;
            cardViewInitialized = true;
            
            npcCards = Array.from(document.querySelectorAll('.npc-card'));
            factionFilter = getEl('factionFilter');
            statusFilter = getEl('statusFilter');
            searchBox = getEl('searchBox');
            
            if (factionFilter) {
                factionFilter.addEventListener('change', filterNPCs);
            }
            if (statusFilter) {
                statusFilter.addEventListener('change', filterNPCs);
            }
            if (searchBox) {
                searchBox.addEventListener('input', filterNPCs);
                searchBox.addEventListener('keyup', filterNPCs);
            }
            
            const groupByEl = getEl('groupBy');
            const sortByEl = getEl('sortBy');
            const spoilerEl = getEl('spoilerFreeMode');
            if (groupByEl) groupByEl.addEventListener('change', filterNPCs);
            if (sortByEl) sortByEl.addEventListener('change', filterNPCs);
            if (spoilerEl) spoilerEl.addEventListener('change', filterNPCs);
            
            updateStats();
        }
        
        // Initialize card view when cards tab is first shown
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                // Only init if cards tab is active
                if (getEl('cardsTab') && getEl('cardsTab').classList.contains('active')) {
                    initCardView();
                }
            });
        } else {
            if (getEl('cardsTab') && getEl('cardsTab').classList.contains('active')) {
                initCardView();
            }
        }
        
        // Editor Functions
        let currentEditingNPC = null;
        let editorNPCData = {};
        if (typeof npcData !== 'undefined' && npcData && Object.keys(npcData).length > 0) {
            editorNPCData = JSON.parse(JSON.stringify(npcData)); // Working copy
            console.log('Editor initialized with', Object.keys(editorNPCData).length, 'NPCs');
            // Debug: Check if party members are in editorNPCData
            const partyMembers = ['Olpha', 'Felwin', 'Julior', 'Cooker', 'Thenn', 'Amok', 'Wren', 'Primevera'];
            partyMembers.forEach(function(name) {
                if (editorNPCData[name]) {
                    console.log('Party member found in editorNPCData:', name, editorNPCData[name]);
                } else {
                    console.warn('Party member NOT found in editorNPCData:', name);
                }
            });
        } else {
            console.error('npcData is not available for editor initialization');
        }
        let hasUnsavedChanges = false;
        let bulkMode = false;
        let selectedNPCs = new Set();
        let autoSaveInterval = null;
        let relationshipCollapsed = false;
        
        // Auto-save functionality
        function startAutoSave() {
            if (autoSaveInterval) clearInterval(autoSaveInterval);
            autoSaveInterval = setInterval(function() {
                if (hasUnsavedChanges) {
                    saveToLocalStorage();
                    updateAutoSaveStatus();
                }
            }, 30000); // Every 30 seconds
        }
        
        function saveToLocalStorage() {
            try {
                if (typeof localStorage === 'undefined') {
                    console.warn('localStorage not available');
                    return;
                }
                localStorage.setItem('npc_relationships_backup', JSON.stringify({
                    data: editorNPCData,
                    timestamp: new Date().toISOString()
                }));
            } catch(e) {
                console.error('Failed to save to localStorage:', e);
                // Handle quota exceeded error
                if (e.name === 'QuotaExceededError') {
                    console.warn('localStorage quota exceeded, clearing old backup');
                    try {
                        localStorage.removeItem('npc_relationships_backup');
                        localStorage.setItem('npc_relationships_backup', JSON.stringify({
                            data: editorNPCData,
                            timestamp: new Date().toISOString()
                        }));
                    } catch(clearErr) {
                        console.error('Failed to save after clearing:', clearErr);
                    }
                }
            }
        }
        
        function loadFromLocalStorage() {
            try {
                if (typeof localStorage === 'undefined') {
                    console.warn('localStorage not available');
                    return false;
                }
                const backup = localStorage.getItem('npc_relationships_backup');
                if (backup) {
                    const parsed = JSON.parse(backup);
                    if (parsed && parsed.data && typeof parsed.data === 'object' && Object.keys(parsed.data).length > 0) {
                        const backupNPCCount = Object.keys(parsed.data).length;
                        const currentNPCCount = Object.keys(editorNPCData).length;
                        
                        // Don't load backup if it has fewer NPCs than current data (likely outdated)
                        if (backupNPCCount < currentNPCCount) {
                            console.log('Backup has fewer NPCs (' + backupNPCCount + ') than current data (' + currentNPCCount + '), skipping outdated backup');
                            // Clear the outdated backup
                            try {
                                localStorage.removeItem('npc_relationships_backup');
                            } catch(clearErr) {
                                console.error('Failed to clear outdated backup:', clearErr);
                            }
                            return false;
                        }
                        
                        // Check if backup is different from current data
                        const currentDataStr = JSON.stringify(editorNPCData);
                        const backupDataStr = JSON.stringify(parsed.data);
                        const isDifferent = currentDataStr !== backupDataStr;
                        
                        // Only prompt if backup is different from current data
                        if (isDifferent) {
                            const timestamp = parsed.timestamp ? new Date(parsed.timestamp).toLocaleString() : 'unknown time';
                            if (confirm('Found backup from ' + timestamp + ' that differs from current data. Load it?')) {
                                editorNPCData = parsed.data;
                                console.log('Loaded backup with', Object.keys(editorNPCData).length, 'NPCs');
                                populateNPCList();
                                populateFactionList();
                                populateTagSuggestions();
                                populateNPCDatalist();
                                setupEditorFilters();
                                markUnsaved();
                                return true; // Indicate backup was loaded
                            }
                        } else {
                            // Backup matches current data, no need to prompt
                            console.log('Backup matches current data, skipping prompt');
                        }
                    }
                }
                return false; // No backup loaded
            } catch(e) {
                console.error('Failed to load from localStorage:', e);
                // Clear corrupted data
                try {
                    if (typeof localStorage !== 'undefined') {
                        localStorage.removeItem('npc_relationships_backup');
                    }
                } catch(clearErr) {
                    console.error('Failed to clear corrupted localStorage:', clearErr);
                }
                return false;
            }
        }
        
        function markUnsaved() {
            hasUnsavedChanges = true;
            const unsavedEl = getEl('unsavedChanges');
            const savedEl = getEl('autoSaveStatus');
            if (unsavedEl) unsavedEl.style.display = 'inline';
            if (savedEl) savedEl.style.display = 'none';
        }
        
        function markSaved() {
            hasUnsavedChanges = false;
            const unsavedEl = getEl('unsavedChanges');
            const savedEl = getEl('autoSaveStatus');
            if (unsavedEl) unsavedEl.style.display = 'none';
            if (savedEl) savedEl.style.display = 'inline';
            saveToLocalStorage();
        }
        
        function updateAutoSaveStatus() {
            const status = getEl('autoSaveStatus');
            if (status) status.textContent = '💾 Auto-saved ' + new Date().toLocaleTimeString();
        }
        
        // Warn before closing with unsaved changes
        window.addEventListener('beforeunload', function(e) {
            if (hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
        
        let editorInitialized = false;
        let backupPromptShown = false; // Track if backup prompt has been shown this session
        
        function initEditor() {
            if (editorInitialized) return; // Prevent duplicate initialization
            editorInitialized = true;
            
            // Only check for backup on first load, not every time tab is opened
            if (!backupPromptShown) {
                const backupLoaded = loadFromLocalStorage();
                backupPromptShown = true;
                // If backup was loaded, it already called populateNPCList, so return early
                if (backupLoaded) {
                    populateFactionList();
                    populateTagSuggestions();
                    setupEditorFilters();
                    startAutoSave();
                    return;
                }
            }
            
            populateNPCList();
            populateFactionList();
            populateTagSuggestions();
            setupEditorFilters();
            startAutoSave();
            
            // Setup search filters
            const searchEl = getEl('editorSearch');
            const factionEl = getEl('editorFilterFaction');
            const statusEl = getEl('editorFilterStatus');
            const tagsEl = getEl('editorFilterTags');
            if (searchEl) searchEl.addEventListener('input', filterNPCList);
            if (factionEl) factionEl.addEventListener('change', filterNPCList);
            if (statusEl) statusEl.addEventListener('change', filterNPCList);
            if (tagsEl) tagsEl.addEventListener('input', filterNPCList);
        }
        
        function populateNPCList() {
            const list = getEl('npcList');
            if (!list) return; // Editor tab not active
            list.innerHTML = '';
            
            const sortedNPCs = Object.keys(editorNPCData).sort();
            console.log('populateNPCList: Total NPCs in editorNPCData:', sortedNPCs.length);
            console.log('Party members check:', {
                'Olpha': sortedNPCs.indexOf('Olpha') >= 0,
                'Felwin': sortedNPCs.indexOf('Felwin') >= 0,
                'Julior': sortedNPCs.indexOf('Julior') >= 0,
                'Cooker': sortedNPCs.indexOf('Cooker') >= 0,
                'Thenn': sortedNPCs.indexOf('Thenn') >= 0,
                'Amok': sortedNPCs.indexOf('Amok') >= 0,
                'Wren': sortedNPCs.indexOf('Wren') >= 0
            });
            
            sortedNPCs.forEach(function(npcId) {
                const npc = editorNPCData[npcId];
                // Skip null/undefined NPCs
                if (!npc || typeof npc !== 'object') {
                    console.warn('Skipping invalid NPC:', npcId);
                    return;
                }
                
                const item = document.createElement('div');
                item.className = 'npc-list-item';
                item.dataset.npcId = npcId;
                item.style.cursor = 'pointer';
                
                if (bulkMode) {
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.checked = selectedNPCs.has(npcId);
                    checkbox.onchange = function(e) {
                        e.stopPropagation(); // Prevent item click
                        if (checkbox.checked) {
                            selectedNPCs.add(npcId);
                        } else {
                            selectedNPCs.delete(npcId);
                        }
                        updateBulkCount();
                    };
                    item.appendChild(checkbox);
                }
                
                const nameSpan = document.createElement('span');
                nameSpan.textContent = npc.name || npcId;
                item.appendChild(nameSpan);
                
                // Make entire item clickable (not just the span)
                item.onclick = function(e) {
                    // Don't trigger if clicking checkbox
                    if (e.target.type === 'checkbox') return;
                    if (!bulkMode) {
                        editNPC(npcId);
                    } else if (checkbox) {
                        checkbox.checked = !checkbox.checked;
                        checkbox.onchange();
                    }
                };
                
                // Add color coding for status/faction
                const status = (npc.status || 'unknown').toString();
                if (status.indexOf('deceased') !== -1) {
                    item.style.opacity = '0.7';
                }
                
                list.appendChild(item);
            });
            filterNPCList();
        }
        
        function filterNPCList() {
            const searchEl = getEl('editorSearch');
            const factionEl = getEl('editorFilterFaction');
            const statusEl = getEl('editorFilterStatus');
            const tagsEl = getEl('editorFilterTags');
            if (!searchEl || !factionEl || !statusEl || !tagsEl) return; // Editor tab not active
            
            const search = searchEl.value.toLowerCase();
            const factionFilter = factionEl.value;
            const statusFilter = statusEl.value;
            const tagsFilter = tagsEl.value.toLowerCase();
            
            document.querySelectorAll('.npc-list-item').forEach(function(item) {
                const npcId = item.dataset.npcId;
                if (!npcId || !editorNPCData[npcId]) {
                    item.style.display = 'none';
                    return;
                }
                const npc = editorNPCData[npcId];
                const name = (npc.name || npcId || '').toLowerCase();
                const faction = (npc.faction || '').toLowerCase();
                const status = (npc.status || '').toLowerCase();
                const tags = (npc.tags || []).join(' ').toLowerCase();
                
                let show = true;
                if (search && name && name.indexOf(search) === -1) show = false;
                if (factionFilter && faction !== factionFilter.toLowerCase()) show = false;
                if (statusFilter && status && status.indexOf(statusFilter.toLowerCase()) === -1) show = false;
                if (tagsFilter && tags && tags.indexOf(tagsFilter) === -1) show = false;
                
                item.style.display = show ? 'block' : 'none';
            });
        }
        
        function setupEditorFilters() {
            const factionSelect = getEl('editorFilterFaction');
            if (!factionSelect) return; // Editor tab not active
            factionSelect.innerHTML = '<option value="">All Factions</option>';
            const factionSet = new Set();
            for (const npcId in editorNPCData) {
                if (editorNPCData[npcId].faction) {
                    factionSet.add(editorNPCData[npcId].faction);
                }
            }
            Array.from(factionSet).sort().forEach(function(faction) {
                const option = document.createElement('option');
                option.value = faction;
                option.textContent = faction;
                factionSelect.appendChild(option);
            });
        }
        
        function populateTagSuggestions() {
            const tagSet = new Set();
            for (const npcId in editorNPCData) {
                const tags = editorNPCData[npcId].tags || [];
                tags.forEach(function(tag) { tagSet.add(tag); });
            }
            const datalist = getEl('tagSuggestions');
            if (!datalist) return; // Editor tab not active
            datalist.innerHTML = '';
            Array.from(tagSet).sort().forEach(function(tag) {
                const option = document.createElement('option');
                option.value = tag;
                datalist.appendChild(option);
            });
        }
        
        function populateFactionList() {
            const factionSet = new Set();
            for (const npcId in editorNPCData) {
                if (editorNPCData[npcId].faction) {
                    factionSet.add(editorNPCData[npcId].faction);
                }
            }
            const datalist = getEl('factionList');
            if (!datalist) return; // Editor tab not active
            datalist.innerHTML = '';
            Array.from(factionSet).sort().forEach(function(faction) {
                const option = document.createElement('option');
                option.value = faction;
                datalist.appendChild(option);
            });
        }
        
        function addNewNPC() {
            const titleEl = getEl('editorTitle');
            const formEl = getEl('npcForm');
            const idEl = getEl('npcId');
            const relListEl = getEl('relationshipsList');
            const formDiv = getEl('editorForm');
            const emptyDiv = getEl('editorEmpty');
            
            if (!titleEl || !formEl || !idEl || !relListEl || !formDiv || !emptyDiv) {
                alert('Editor not ready. Please wait for the editor to load.');
                return;
            }
            
            currentEditingNPC = null;
            titleEl.textContent = 'Add New NPC';
            formEl.reset();
            idEl.value = '';
            relListEl.innerHTML = '';
            formDiv.style.display = 'block';
            emptyDiv.style.display = 'none';
            document.querySelectorAll('.npc-list-item').forEach(function(item) {
                item.classList.remove('active');
            });
            const validationDiv = getEl('relationshipValidation');
            if (validationDiv) validationDiv.style.display = 'none';
        }
        
        function editNPC(npcId) {
            if (!editorNPCData[npcId]) {
                console.error('NPC not found:', npcId);
                return;
            }
            
            currentEditingNPC = npcId;
            const npc = editorNPCData[npcId];
            
            const titleEl = getEl('editorTitle');
            const idEl = getEl('npcId');
            const nameEl = getEl('npcName');
            const factionEl = getEl('npcFaction');
            const locationEl = getEl('npcLocation');
            const statusEl = getEl('npcStatus');
            const portraitEl = getEl('npcPortrait');
            const tagsEl = getEl('npcTags');
            const notesEl = getEl('npcNotes');
            const spoilerEl = getEl('npcSpoiler');
            
            if (!titleEl || !idEl || !nameEl) {
                alert('Editor not ready. Please wait for the editor to load.');
                return;
            }
            
            titleEl.textContent = 'Edit NPC: ' + (npc.name || npcId);
            idEl.value = npcId;
            nameEl.value = npc.name || '';
            if (factionEl) factionEl.value = npc.faction || '';
            if (locationEl) locationEl.value = npc.location || '';
            if (statusEl) statusEl.value = npc.status || '';
            if (portraitEl) portraitEl.value = npc.portrait || '';
            if (tagsEl) tagsEl.value = (npc.tags || []).join(', ');
            if (notesEl) notesEl.value = npc.notes || '';
            if (spoilerEl) spoilerEl.checked = npc.spoiler === true;
            
            // Populate relationships
            const relationshipsList = getEl('relationshipsList');
            if (relationshipsList) {
                relationshipsList.innerHTML = '';
                if (npc.relationships) {
                    for (const relType in npc.relationships) {
                        if (!npc.relationships.hasOwnProperty(relType)) continue;
                        npc.relationships[relType].forEach(function(target) {
                            addRelationshipRow(relType, target);
                        });
                    }
                }
            }
            
            const formDiv = getEl('editorForm');
            const emptyDiv = getEl('editorEmpty');
            if (formDiv) formDiv.style.display = 'block';
            if (emptyDiv) emptyDiv.style.display = 'none';
            
            // Highlight in list
            document.querySelectorAll('.npc-list-item').forEach(function(item) {
                item.classList.remove('active');
                if (item.dataset.npcId === npcId) {
                    item.classList.add('active');
                }
            });
            
            // Preview portrait and validate relationships
            setTimeout(function() {
                previewPortrait();
                validateRelationships();
            }, 100);
        }
        
        function addRelationship() {
            addRelationshipRow('', '');
        }
        
        function addRelationshipRow(relType, target) {
            const relationshipsList = getEl('relationshipsList');
            if (!relationshipsList) return; // Editor tab not active
            const item = document.createElement('div');
            item.className = 'relationship-item';
            
            const relTypeSelect = document.createElement('select');
            relTypeSelect.className = 'rel-type';
            relTypeSelect.onchange = function() { validateRelationships(); markUnsaved(); };
            const relTypes = relationshipTypes && relationshipTypes.length > 0 ? relationshipTypes : ['ally', 'enemy', 'serves', 'controls', 'works_with', 'related_to', 'uses', 'trapped_by', 'feeds_on', 'captured_by', 'created', 'member_of', 'leads', 'guides', 'connected_to', 'wants_freedom_from', 'twin_of', 'stole_bride_from', 'stolen_from', 'controlled_by', 'friend_of', 'tends_to', 'interested_in', 'hosts', 'loved', 'made_pact_for', 'bound_to', 'mentor_was', 'mentor_of', 'tried_to_save', 'survivor_of', 'works_at', 'knows_about', 'runs', 'sister_in', 'seeks', 'interested_in_by', 'enslaved_by', 'wants_revenge_on', 'from', 'mother_of', 'son_of', 'captive_of', 'tracking', 'seeks_understanding_of', 'contains', 'used_by', 'used', 'wielded'];
            relTypes.forEach(function(type) {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type.replace(/_/g, ' ');
                if (type === relType) option.selected = true;
                relTypeSelect.appendChild(option);
            });
            
            const targetInput = document.createElement('input');
            targetInput.type = 'text';
            targetInput.className = 'rel-target';
            targetInput.value = target;
            targetInput.placeholder = 'Target NPC name';
            targetInput.setAttribute('list', 'npcNameList');
            targetInput.onchange = function() { validateRelationships(); markUnsaved(); };
            targetInput.onblur = function() { validateRelationships(); };
            
            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = '🗑️';
            deleteBtn.onclick = function() { item.remove(); validateRelationships(); markUnsaved(); };
            
            item.appendChild(relTypeSelect);
            item.appendChild(targetInput);
            item.appendChild(deleteBtn);
            relationshipsList.appendChild(item);
            
            // Validate after adding
            setTimeout(validateRelationships, 100);
        }
        
        function saveNPC(event) {
            event.preventDefault();
            
            const idEl = getEl('npcId');
            const nameEl = getEl('npcName');
            const factionEl = getEl('npcFaction');
            const locationEl = getEl('npcLocation');
            const statusEl = getEl('npcStatus');
            const portraitEl = getEl('npcPortrait');
            const tagsEl = getEl('npcTags');
            const notesEl = getEl('npcNotes');
            const spoilerEl = getEl('npcSpoiler');
            
            if (!nameEl) {
                alert('Editor form not ready');
                return;
            }
            
            const npcId = (idEl && idEl.value) || nameEl.value;
            const name = nameEl.value;
            if (!name || name.trim() === '') {
                alert('NPC name is required');
                return;
            }
            
            const faction = factionEl ? factionEl.value : '';
            const location = locationEl ? locationEl.value : '';
            const status = statusEl ? statusEl.value : 'alive';
            const portrait = portraitEl ? portraitEl.value : '';
            const tagsStr = tagsEl ? tagsEl.value : '';
            const notes = notesEl ? notesEl.value : '';
            const spoiler = spoilerEl ? spoilerEl.checked : false;
            
            const tags = tagsStr ? tagsStr.split(',').map(function(t) { return t.trim(); }).filter(function(t) { return t; }) : [];
            
            // Collect relationships
            const relationships = {};
            document.querySelectorAll('.relationship-item').forEach(function(item) {
                const relTypeEl = item.querySelector('.rel-type');
                const targetEl = item.querySelector('.rel-target');
                if (!relTypeEl || !targetEl) return;
                const relType = relTypeEl.value;
                const target = targetEl.value.trim();
                if (relType && target) {
                    if (!relationships[relType]) {
                        relationships[relType] = [];
                    }
                    if (relationships[relType].indexOf(target) === -1) {
                        relationships[relType].push(target);
                    }
                }
            });
            
            // Create or update NPC
            editorNPCData[npcId] = {
                name: name,
                faction: faction || undefined,
                location: location || undefined,
                status: status || 'alive',
                portrait: portrait || undefined,
                tags: tags.length > 0 ? tags : undefined,
                notes: notes || undefined,
                spoiler: spoiler || undefined,
                relationships: Object.keys(relationships).length > 0 ? relationships : undefined
            };
            
            // If ID changed, remove old entry
            if (currentEditingNPC && currentEditingNPC !== npcId) {
                delete editorNPCData[currentEditingNPC];
            }
            
            populateNPCList();
            populateFactionList();
            populateTagSuggestions();
            populateNPCDatalist();
            markSaved();
            alert('NPC saved! Remember to export the JSON and regenerate the mind map.');
        }
        
        function cancelEdit() {
            const formDiv = getEl('editorForm');
            const emptyDiv = getEl('editorEmpty');
            if (formDiv) formDiv.style.display = 'none';
            if (emptyDiv) emptyDiv.style.display = 'block';
            currentEditingNPC = null;
            document.querySelectorAll('.npc-list-item').forEach(function(item) {
                item.classList.remove('active');
            });
            const validationDiv = getEl('relationshipValidation');
            if (validationDiv) validationDiv.style.display = 'none';
        }
        
        function deleteNPC() {
            if (!currentEditingNPC) return;
            if (!confirm('Are you sure you want to delete this NPC?')) return;
            
            delete editorNPCData[currentEditingNPC];
            markUnsaved();
            populateNPCList();
            populateFactionList();
            populateTagSuggestions();
            populateNPCDatalist();
            cancelEdit();
            alert('NPC deleted! Remember to export the JSON and regenerate the mind map.');
        }
        
        function exportJSON() {
            try {
                // Clean up undefined values before export
                const cleanedData = {};
                for (const npcId in editorNPCData) {
                    if (!editorNPCData.hasOwnProperty(npcId)) continue;
                    const npc = editorNPCData[npcId];
                    if (!npc) continue;
                    const cleaned = {};
                    if (npc.name) cleaned.name = npc.name;
                    if (npc.faction) cleaned.faction = npc.faction;
                    if (npc.location) cleaned.location = npc.location;
                    cleaned.status = npc.status || 'alive';
                    if (npc.portrait) cleaned.portrait = npc.portrait;
                    if (npc.tags && Array.isArray(npc.tags) && npc.tags.length > 0) cleaned.tags = npc.tags;
                    if (npc.notes) cleaned.notes = npc.notes;
                    if (npc.spoiler) cleaned.spoiler = npc.spoiler;
                    if (npc.relationships && Object.keys(npc.relationships).length > 0) cleaned.relationships = npc.relationships;
                    cleanedData[npcId] = cleaned;
                }
                
                const exportData = {
                    npcs: cleanedData,
                    relationship_types: relationshipTypes,
                    factions: factionsList
                };
                
                const jsonStr = JSON.stringify(exportData, null, 2);
                const blob = new Blob([jsonStr], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'npc_relationships.json';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                markSaved(); // Mark as saved after export
            } catch(err) {
                alert('Export failed: ' + err.message);
                console.error('JSON export error:', err);
            }
        }
        
        // Populate NPC name datalist for relationship targets
        function populateNPCDatalist() {
            let datalist = getEl('npcNameList');
            if (!datalist) {
                datalist = document.createElement('datalist');
                datalist.id = 'npcNameList';
                document.body.appendChild(datalist);
            }
            datalist.innerHTML = '';
            for (const npcId in editorNPCData) {
                const option = document.createElement('option');
                option.value = editorNPCData[npcId].name || npcId;
                datalist.appendChild(option);
            }
        }
        
        // Bulk Operations
        function toggleBulkMode() {
            bulkMode = !bulkMode;
            selectedNPCs.clear();
            populateNPCList();
            const bulkActionsEl = getEl('bulkActions');
            if (bulkActionsEl) bulkActionsEl.style.display = bulkMode ? 'block' : 'none';
            updateBulkCount();
        }
        
        function updateBulkCount() {
            const countEl = getEl('bulkCount');
            if (countEl) countEl.textContent = selectedNPCs.size;
        }
        
        function bulkUpdateTags() {
            if (selectedNPCs.size === 0) {
                alert('No NPCs selected. Use Bulk Mode to select NPCs first.');
                return;
            }
            const tags = prompt('Enter tags (comma-separated) to add to selected NPCs:');
            if (!tags || tags.trim() === '') return;
            const tagArray = tags.split(',').map(function(t) { return t.trim(); }).filter(function(t) { return t; });
            if (tagArray.length === 0) return;
            
            selectedNPCs.forEach(function(npcId) {
                if (!editorNPCData[npcId]) return;
                const npc = editorNPCData[npcId];
                if (!npc.tags) npc.tags = [];
                if (!Array.isArray(npc.tags)) npc.tags = [];
                tagArray.forEach(function(tag) {
                    if (npc.tags.indexOf(tag) === -1) {
                        npc.tags.push(tag);
                    }
                });
            });
            markUnsaved();
            populateNPCList();
            populateTagSuggestions();
            populateNPCDatalist();
        }
        
        function bulkUpdateFaction() {
            if (selectedNPCs.size === 0) {
                alert('No NPCs selected. Use Bulk Mode to select NPCs first.');
                return;
            }
            const faction = prompt('Enter faction for selected NPCs:');
            if (faction === null) return; // User cancelled
            selectedNPCs.forEach(function(npcId) {
                if (editorNPCData[npcId]) {
                    editorNPCData[npcId].faction = faction.trim() || undefined;
                }
            });
            markUnsaved();
            populateNPCList();
            setupEditorFilters();
            populateNPCDatalist();
        }
        
        function bulkUpdateStatus() {
            if (selectedNPCs.size === 0) {
                alert('No NPCs selected. Use Bulk Mode to select NPCs first.');
                return;
            }
            const status = prompt('Enter status for selected NPCs:');
            if (status === null) return; // User cancelled
            selectedNPCs.forEach(function(npcId) {
                if (editorNPCData[npcId]) {
                    editorNPCData[npcId].status = status.trim() || 'alive';
                }
            });
            markUnsaved();
            populateNPCList();
            populateNPCDatalist();
        }
        
        function bulkDelete() {
            if (selectedNPCs.size === 0) {
                alert('No NPCs selected. Use Bulk Mode to select NPCs first.');
                return;
            }
            if (!confirm('Delete ' + selectedNPCs.size + ' selected NPCs?')) return;
            const npcIdsToDelete = Array.from(selectedNPCs);
            npcIdsToDelete.forEach(function(npcId) {
                delete editorNPCData[npcId];
            });
            selectedNPCs.clear();
            markUnsaved();
            populateNPCList();
            populateNPCDatalist();
            updateBulkCount();
        }
        
        // Relationship Templates
        const relationshipTemplates = {
            'Enemy': { type: 'enemy', bidirectional: true },
            'Ally': { type: 'ally', bidirectional: true },
            'Serves': { type: 'serves', bidirectional: 'served_by' },
            'Controls': { type: 'controls', bidirectional: 'controlled_by' },
            'Works With': { type: 'works_with', bidirectional: true },
            'Related To': { type: 'related_to', bidirectional: true }
        };
        
        function showRelationshipTemplates() {
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.id = 'relationshipTemplateModal';
            modal.innerHTML = '<div class="modal-content"><span class="close-modal" onclick="this.parentElement.parentElement.remove()">&times;</span><h2 style="color: #FFD700;">Relationship Templates</h2><div id="templateButtons"></div></div>';
            document.body.appendChild(modal);
            modal.style.display = 'block';
            
            // Close modal when clicking outside
            modal.onclick = function(e) {
                if (e.target === modal) {
                    modal.remove();
                }
            };
            
            const buttonsDiv = getEl('templateButtons');
            if (!buttonsDiv) return;
            for (const name in relationshipTemplates) {
                const btn = document.createElement('button');
                btn.className = 'relationship-template-btn';
                btn.textContent = name;
                btn.onclick = function() {
                    const template = relationshipTemplates[name];
                    const target = prompt('Enter target NPC name:');
                    if (target) {
                        addRelationshipWithTemplate(template.type, target, template.bidirectional);
                        modal.remove();
                    }
                };
                buttonsDiv.appendChild(btn);
            }
        }
        
        function addRelationshipWithTemplate(relType, target, bidirectional) {
            if (!target || target.trim() === '') {
                alert('Please enter a target NPC name');
                return;
            }
            
            addRelationshipRow(relType, target);
            markUnsaved();
            
            // Get current NPC name/ID for bidirectional relationship
            const nameEl = getEl('npcName');
            const currentNPCName = (nameEl && nameEl.value) ? nameEl.value : (currentEditingNPC || '');
            if (!currentNPCName) {
                console.warn('Cannot create bidirectional relationship: no current NPC name');
                return;
            }
            
            if (bidirectional === true) {
                // Find reverse relationship type
                const reverseMap = {
                    'enemy': 'enemy',
                    'ally': 'ally',
                    'works_with': 'works_with',
                    'related_to': 'related_to'
                };
                const reverseType = reverseMap[relType] || relType;
                // Add to target NPC if exists
                const targetNPC = findNPCByName(target);
                if (targetNPC) {
                    if (!targetNPC.relationships) targetNPC.relationships = {};
                    if (!targetNPC.relationships[reverseType]) targetNPC.relationships[reverseType] = [];
                    if (targetNPC.relationships[reverseType].indexOf(currentNPCName) === -1) {
                        targetNPC.relationships[reverseType].push(currentNPCName);
                    }
                } else {
                    console.warn('Target NPC not found for bidirectional relationship:', target);
                }
            } else if (bidirectional && typeof bidirectional === 'string') {
                const targetNPC = findNPCByName(target);
                if (targetNPC) {
                    if (!targetNPC.relationships) targetNPC.relationships = {};
                    if (!targetNPC.relationships[bidirectional]) targetNPC.relationships[bidirectional] = [];
                    if (targetNPC.relationships[bidirectional].indexOf(currentNPCName) === -1) {
                        targetNPC.relationships[bidirectional].push(currentNPCName);
                    }
                } else {
                    console.warn('Target NPC not found for bidirectional relationship:', target);
                }
            }
        }
        
        function findNPCByName(name) {
            for (const npcId in editorNPCData) {
                if (editorNPCData[npcId].name === name || npcId === name) {
                    return editorNPCData[npcId];
                }
            }
            return null;
        }
        
        // Relationship Validation
        function validateRelationships() {
            const errors = [];
            const relationshipsList = getEl('relationshipsList');
            if (!relationshipsList) return true; // Editor tab not active
            const items = relationshipsList.querySelectorAll('.relationship-item');
            
            items.forEach(function(item, index) {
                const relTypeEl = item.querySelector('.rel-type');
                const targetEl = item.querySelector('.rel-target');
                if (!relTypeEl || !targetEl) return;
                const relType = relTypeEl.value;
                const target = targetEl.value.trim();
                
                if (relType && target) {
                    const targetNPC = findNPCByName(target);
                    if (!targetNPC) {
                        errors.push('Relationship ' + (index + 1) + ': Target NPC "' + target + '" does not exist');
                        item.style.border = '2px solid #f44336';
                    } else {
                        item.style.border = '';
                    }
                }
            });
            
            const validationDiv = getEl('relationshipValidation');
            const errorsList = getEl('relationshipErrors');
            if (errors.length > 0 && validationDiv && errorsList) {
                validationDiv.style.display = 'block';
                errorsList.innerHTML = '';
                errors.forEach(function(error) {
                    const li = document.createElement('li');
                    li.textContent = error;
                    errorsList.appendChild(li);
                });
            } else if (validationDiv) {
                validationDiv.style.display = 'none';
            }
            
            return errors.length === 0;
        }
        
        
        // Collapsible Relationships
        function toggleRelationshipCollapse() {
            relationshipCollapsed = !relationshipCollapsed;
            const list = getEl('relationshipsList');
            const btn = getEl('collapseBtn');
            if (!list || !btn) return;
            
            if (relationshipCollapsed) {
                list.classList.add('collapsed');
                btn.textContent = '📁 Expand';
            } else {
                list.classList.remove('collapsed');
                btn.textContent = '📂 Collapse';
            }
        }
        
        // Portrait Preview
        function previewPortrait() {
            const portraitEl = getEl('npcPortrait');
            const preview = getEl('portraitPreview');
            if (!portraitEl || !preview) return;
            
            const path = portraitEl.value;
            if (path && path.trim() !== '') {
                preview.style.display = 'block';
                preview.style.backgroundImage = 'url(' + path + ')';
            } else {
                preview.style.display = 'none';
            }
        }
        
        // Copy NPC
        function copyNPC() {
            if (!currentEditingNPC) {
                alert('No NPC selected to copy');
                return;
            }
            if (!editorNPCData[currentEditingNPC]) {
                alert('NPC not found');
                return;
            }
            const original = editorNPCData[currentEditingNPC];
            const newId = 'Copy of ' + currentEditingNPC;
            editorNPCData[newId] = JSON.parse(JSON.stringify(original));
            editorNPCData[newId].name = 'Copy of ' + (original.name || currentEditingNPC);
            markUnsaved();
            populateNPCList();
            populateNPCDatalist();
            editNPC(newId);
        }
        
        // NPC Templates
        const npcTemplates = {
            'Merchant': { faction: 'Civilians / Merchants', tags: ['merchant'], status: 'alive' },
            'Guard': { faction: 'City Guard', tags: ['guard', 'law-enforcement'], status: 'alive' },
            'Scholar': { faction: 'Independent / Scholar', tags: ['scholar'], status: 'alive' },
            'Noble': { faction: 'Light Ring', tags: ['noble'], status: 'alive' },
            'Archivist': { faction: 'Fey Palace Archive', tags: ['archivist'], status: 'alive' }
        };
        
        function showTemplates() {
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.id = 'templateModal';
            modal.innerHTML = '<div class="modal-content"><span class="close-modal" onclick="this.parentElement.parentElement.remove()">&times;</span><h2 style="color: #FFD700;">NPC Templates</h2><div id="templateNPCButtons"></div></div>';
            document.body.appendChild(modal);
            modal.style.display = 'block';
            
            // Close modal when clicking outside
            modal.onclick = function(e) {
                if (e.target === modal) {
                    modal.remove();
                }
            };
            
            const buttonsDiv = getEl('templateNPCButtons');
            if (!buttonsDiv) return;
            for (const name in npcTemplates) {
                const btn = document.createElement('button');
                btn.className = 'editor-btn';
                btn.textContent = name;
                btn.style.width = '100%';
                btn.style.marginBottom = '10px';
                btn.onclick = function() {
                    const template = npcTemplates[name];
                    addNewNPC();
                    const factionEl = getEl('npcFaction');
                    const statusEl = getEl('npcStatus');
                    const tagsEl = getEl('npcTags');
                    if (factionEl) factionEl.value = template.faction || '';
                    if (statusEl) statusEl.value = template.status || 'alive';
                    if (tagsEl && template.tags && Array.isArray(template.tags)) {
                        tagsEl.value = template.tags.join(', ');
                    }
                    modal.remove();
                };
                buttonsDiv.appendChild(btn);
            }
        }
        
        // Data Validation
        function validateData() {
            const errors = [];
            const warnings = [];
            const npcNames = new Set();
            const duplicateNames = [];
            const orphanNPCs = [];
            
            // Check for duplicate names/IDs
            for (const npcId in editorNPCData) {
                if (!editorNPCData.hasOwnProperty(npcId)) continue;
                const npc = editorNPCData[npcId];
                if (!npc) {
                    warnings.push('Null NPC entry found: ' + npcId);
                    continue;
                }
                const name = npc.name || npcId;
                if (npcNames.has(name)) {
                    duplicateNames.push(name);
                }
                npcNames.add(name);
                
                // Check for NPCs with no relationships
                if (!npc.relationships || Object.keys(npc.relationships).length === 0) {
                    orphanNPCs.push(name);
                }
            }
            
            if (duplicateNames.length > 0) {
                warnings.push('Duplicate NPC names found: ' + duplicateNames.join(', '));
            }
            
            if (orphanNPCs.length > 0 && orphanNPCs.length < Object.keys(editorNPCData).length) {
                warnings.push(orphanNPCs.length + ' NPCs have no relationships: ' + orphanNPCs.slice(0, 5).join(', ') + (orphanNPCs.length > 5 ? '...' : ''));
            }
            
            // Check relationships
            for (const npcId in editorNPCData) {
                if (!editorNPCData.hasOwnProperty(npcId)) continue;
                const npc = editorNPCData[npcId];
                if (!npc) continue;
                if (npc.relationships) {
                    for (const relType in npc.relationships) {
                        if (!npc.relationships.hasOwnProperty(relType)) continue;
                        const targets = npc.relationships[relType];
                        if (!Array.isArray(targets)) {
                            errors.push(npcId + ' has invalid relationship format for ' + relType + ' (expected array)');
                            continue;
                        }
                        targets.forEach(function(target) {
                            if (!target || typeof target !== 'string') {
                                errors.push(npcId + ' has invalid relationship target in ' + relType);
                            } else if (!findNPCByName(target)) {
                                errors.push(npcId + ' has relationship to non-existent NPC: ' + target);
                            }
                        });
                    }
                }
            }
            
            // Show results
            let message = '';
            if (errors.length > 0) {
                message += 'ERRORS (' + errors.length + '):\\n' + errors.slice(0, 10).join('\\n');
                if (errors.length > 10) message += '\\n... and ' + (errors.length - 10) + ' more';
                message += '\\n\\n';
            }
            if (warnings.length > 0) {
                message += 'WARNINGS (' + warnings.length + '):\\n' + warnings.join('\\n') + '\\n\\n';
            }
            if (message === '') {
                message = '✓ No errors found! All ' + Object.keys(editorNPCData).length + ' NPCs are valid.';
            }
            alert(message);
            return errors.length === 0;
        }
        
        // Relationship Intelligence
        function showRelationshipIntelligence() {
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.id = 'intelligenceModal';
            modal.innerHTML = '<div class="modal-content" style="max-width: 900px;"><span class="close-modal" onclick="this.parentElement.parentElement.remove()">&times;</span><h2 style="color: #FFD700;">Relationship Intelligence</h2><div id="intelligenceContent"></div></div>';
            document.body.appendChild(modal);
            modal.style.display = 'block';
            
            // Close modal when clicking outside
            modal.onclick = function(e) {
                if (e.target === modal) {
                    modal.remove();
                }
            };
            
            const content = getEl('intelligenceContent');
            if (!content) return;
            
            // Statistics
            let totalRelationships = 0;
            const relationshipTypeCounts = {};
            const npcConnectionCounts = {};
            
            for (const npcId in editorNPCData) {
                const npc = editorNPCData[npcId];
                npcConnectionCounts[npcId] = 0;
                if (npc.relationships) {
                    for (const relType in npc.relationships) {
                        const count = npc.relationships[relType].length;
                        totalRelationships += count;
                        npcConnectionCounts[npcId] += count;
                        relationshipTypeCounts[relType] = (relationshipTypeCounts[relType] || 0) + count;
                    }
                }
            }
            
            // Most connected NPCs
            const sortedNPCs = Object.keys(npcConnectionCounts).sort(function(a, b) {
                return npcConnectionCounts[b] - npcConnectionCounts[a];
            });
            
            let html = '<div class="stat-box"><div class="stat-label">Total Relationships</div><div class="stat-value">' + totalRelationships + '</div></div>';
            html += '<div class="stat-box"><div class="stat-label">Total NPCs</div><div class="stat-value">' + Object.keys(editorNPCData).length + '</div></div>';
            
            html += '<h3 style="color: #FFD700; margin-top: 20px;">Most Connected NPCs</h3><ul>';
            sortedNPCs.slice(0, 10).forEach(function(npcId) {
                const npc = editorNPCData[npcId];
                html += '<li>' + (npc.name || npcId) + ': ' + npcConnectionCounts[npcId] + ' relationships</li>';
            });
            html += '</ul>';
            
            html += '<h3 style="color: #FFD700; margin-top: 20px;">Relationship Types</h3><ul>';
            const sortedTypes = Object.keys(relationshipTypeCounts).sort(function(a, b) {
                return relationshipTypeCounts[b] - relationshipTypeCounts[a];
            });
            sortedTypes.forEach(function(type) {
                html += '<li>' + type.replace(/_/g, ' ') + ': ' + relationshipTypeCounts[type] + '</li>';
            });
            html += '</ul>';
            
            // Missing relationship suggestions
            html += '<h3 style="color: #FFD700; margin-top: 20px;">Missing Relationship Suggestions</h3>';
            const suggestions = findMissingRelationships();
            if (suggestions.length > 0) {
                html += '<ul>';
                suggestions.slice(0, 10).forEach(function(suggestion) {
                    html += '<li>' + suggestion + '</li>';
                });
                html += '</ul>';
            } else {
                html += '<p>No obvious missing relationships detected.</p>';
            }
            
            content.innerHTML = html;
        }
        
        function findMissingRelationships() {
            const suggestions = [];
            for (const npcId in editorNPCData) {
                const npc = editorNPCData[npcId];
                if (npc.relationships) {
                    // Check for enemy relationships that might need reverse
                    if (npc.relationships.enemy) {
                        npc.relationships.enemy.forEach(function(targetName) {
                            const targetNPC = findNPCByName(targetName);
                            if (targetNPC && targetNPC.relationships) {
                                if (!targetNPC.relationships.enemy || targetNPC.relationships.enemy.indexOf(npc.name || npcId) === -1) {
                                    suggestions.push(targetName + ' might be enemy of ' + (npc.name || npcId));
                                }
                            }
                        });
                    }
                }
            }
            return suggestions;
        }
        
        // Import/Export Functions
        function exportCSV() {
            try {
                let csv = 'Name,Faction,Location,Status,Tags,Notes\\n';
                for (const npcId in editorNPCData) {
                    if (!editorNPCData.hasOwnProperty(npcId)) continue;
                    const npc = editorNPCData[npcId];
                    if (!npc) continue;
                    const name = String(npc.name || npcId || '').replace(/"/g, '""');
                    const faction = String(npc.faction || '').replace(/"/g, '""');
                    const location = String(npc.location || '').replace(/"/g, '""');
                    const status = String(npc.status || '').replace(/"/g, '""');
                    const tags = Array.isArray(npc.tags) ? npc.tags.join(';') : String(npc.tags || '');
                    const tagsEscaped = tags.replace(/"/g, '""');
                    const notes = String(npc.notes || '').replace(/"/g, '""').replace(/\\n/g, ' ');
                    csv += '"' + name + '","' + faction + '","' + location + '","' + status + '","' + tagsEscaped + '","' + notes + '"\\n';
                }
                downloadFile(csv, 'npc_relationships.csv', 'text/csv');
            } catch(err) {
                alert('Export failed: ' + err.message);
                console.error('CSV export error:', err);
            }
        }
        
        function exportMarkdown() {
            let md = '# NPC Relationship List\\n\\n';
            for (const npcId in editorNPCData) {
                const npc = editorNPCData[npcId];
                md += '## ' + (npc.name || npcId) + '\\n\\n';
                md += '- **Faction**: ' + (npc.faction || 'Unknown') + '\\n';
                md += '- **Location**: ' + (npc.location || 'Unknown') + '\\n';
                md += '- **Status**: ' + (npc.status || 'Unknown') + '\\n';
                if (npc.tags && npc.tags.length > 0) {
                    md += '- **Tags**: ' + npc.tags.join(', ') + '\\n';
                }
                if (npc.notes) {
                    md += '- **Notes**: ' + npc.notes + '\\n';
                }
                md += '\\n';
            }
            downloadFile(md, 'npc_relationships.md', 'text/markdown');
        }
        
        function importFromFile() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json,.csv';
            input.onchange = function(e) {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = function(event) {
                    try {
                        if (file.name.endsWith('.json')) {
                            const data = JSON.parse(event.target.result);
                            if (data.npcs) {
                                editorNPCData = data.npcs;
                                markUnsaved();
                                populateNPCList();
                                populateFactionList();
                                populateTagSuggestions();
                                populateNPCDatalist();
                                setupEditorFilters();
                                alert('Import successful!');
                            }
                        } else if (file.name.endsWith('.csv')) {
                            // Basic CSV import - expects: Name,Faction,Location,Status,Tags,Notes
                            const text = event.target.result;
                            const lines = text.split(/\\r?\\n/).filter(function(line) { return line.trim(); });
                            if (lines.length < 2) {
                                alert('CSV file appears to be empty or invalid');
                                return;
                            }
                            // Skip header row
                            for (let i = 1; i < lines.length; i++) {
                                const line = lines[i];
                                // Simple CSV parsing - handles quoted values
                                const values = [];
                                let current = '';
                                let inQuotes = false;
                                for (let j = 0; j < line.length; j++) {
                                    const char = line[j];
                                    if (char === '"') {
                                        inQuotes = !inQuotes;
                                    } else if (char === ',' && !inQuotes) {
                                        values.push(current.trim());
                                        current = '';
                                    } else {
                                        current += char;
                                    }
                                }
                                values.push(current.trim());
                                
                                if (values.length < 1 || !values[0]) continue;
                                const name = values[0].replace(/^"|"$/g, '');
                                if (!name) continue;
                                
                                const npc = { name: name };
                                if (values[1]) npc.faction = values[1].replace(/^"|"$/g, '') || undefined;
                                if (values[2]) npc.location = values[2].replace(/^"|"$/g, '') || undefined;
                                if (values[3]) npc.status = values[3].replace(/^"|"$/g, '') || 'alive';
                                if (values[4]) {
                                    const tags = values[4].replace(/^"|"$/g, '').split(';').map(function(t) { return t.trim(); }).filter(function(t) { return t; });
                                    if (tags.length > 0) npc.tags = tags;
                                }
                                if (values[5]) npc.notes = values[5].replace(/^"|"$/g, '') || undefined;
                                editorNPCData[name] = npc;
                            }
                            markUnsaved();
                            populateNPCList();
                            populateFactionList();
                            populateTagSuggestions();
                            populateNPCDatalist();
                            setupEditorFilters();
                            alert('CSV import successful!');
                        } else {
                            alert('Unsupported file type. Please use .json or .csv');
                        }
                    } catch(err) {
                        alert('Import failed: ' + err.message);
                    }
                };
                reader.readAsText(file);
            };
            input.click();
        }
        
        function importRelationships() {
            if (!currentEditingNPC) {
                alert('Please select or create an NPC first to import relationships for.');
                return;
            }
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = function(e) {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onerror = function() {
                    alert('Error reading file');
                };
                reader.onload = function(event) {
                    try {
                        const data = JSON.parse(event.target.result);
                        if (Array.isArray(data)) {
                            let imported = 0;
                            data.forEach(function(rel) {
                                if (rel.type && rel.target) {
                                    addRelationshipRow(rel.type, rel.target);
                                    imported++;
                                }
                            });
                            markUnsaved();
                            validateRelationships();
                            alert('Imported ' + imported + ' relationships');
                        } else {
                            alert('Invalid format. Expected an array of relationship objects.');
                        }
                    } catch(err) {
                        alert('Import failed: ' + err.message);
                    }
                };
                reader.readAsText(file);
            };
            input.click();
        }
        
        function downloadFile(content, filename, mimeType) {
            const blob = new Blob([content], { type: mimeType });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        function exportToObsidian() {
            let md = '# NPCs\\n\\n';
            for (const npcId in editorNPCData) {
                const npc = editorNPCData[npcId];
                const name = npc.name || npcId;
                md += '## ' + name + '\\n\\n';
                md += '**ID**: `' + npcId + '`\\n\\n';
                if (npc.faction) md += '**Faction**: ' + npc.faction + '\\n\\n';
                if (npc.location) md += '**Location**: ' + npc.location + '\\n\\n';
                if (npc.status) md += '**Status**: ' + npc.status + '\\n\\n';
                if (npc.tags && npc.tags.length > 0) {
                    md += '**Tags**: ' + npc.tags.map(function(t) { return '`' + t + '`'; }).join(', ') + '\\n\\n';
                }
                if (npc.notes) md += npc.notes + '\\n\\n';
                if (npc.relationships) {
                    md += '### Relationships\\n\\n';
                    for (const relType in npc.relationships) {
                        md += '- **' + relType.replace(/_/g, ' ') + '**: ' + npc.relationships[relType].join(', ') + '\\n';
                    }
                    md += '\\n';
                }
                md += '---\\n\\n';
            }
            downloadFile(md, 'NPCs_Obsidian.md', 'text/markdown');
        }
        
        function regenerateMindMap() {
            if (!validateData()) {
                if (!confirm('Validation found errors. Continue anyway?')) return;
            }
            exportJSON();
            alert('JSON exported! Now run: python generate_mindmap.py');
        }
        
        // Wrap saveNPC to include validation - will be called from form onsubmit
        const originalSaveNPCFunc = saveNPC;
        saveNPC = function(event) {
            event.preventDefault();
            if (!validateRelationships()) {
                if (!confirm('Some relationships have validation errors. Save anyway?')) return;
            }
            originalSaveNPCFunc(event);
            // markSaved() is already called in originalSaveNPCFunc, no need to call twice
        };
        
        // Initialize datalist when editor is first opened
        setTimeout(function() {
            populateNPCDatalist();
            if (currentEditingNPC) {
                previewPortrait();
            }
        }, 100);
        // Simple logger utility (can be disabled by setting DEBUG_MODE to false)
        const DEBUG_MODE = false; // Set to true to enable debug logging
        const logger = {{
            log: function(...args) {{
                if (DEBUG_MODE) console.log(...args);
            }},
            error: function(...args) {{
                if (DEBUG_MODE) console.error(...args);
            }},
            warn: function(...args) {{
                if (DEBUG_MODE) console.warn(...args);
            }}
        }};
        
        // Inventory Tracker Functions
        let inventoryData = {{
            partyGold: 0,
            players: [],
            bagOfHolding: []
        }};
        
        // Helper functions for rarity colors and item management
        function getRarityColor(rarity) {
            if (!rarity) return '#9e9e9e'; // Gray for no rarity
            const rarityLower = rarity.toLowerCase();
            if (rarityLower.includes('common')) return '#9e9e9e';
            if (rarityLower.includes('uncommon')) return '#4caf50';
            if (rarityLower.includes('rare')) return '#2196f3';
            if (rarityLower.includes('very rare')) return '#9c27b0';
            if (rarityLower.includes('legendary')) return '#ff9800';
            if (rarityLower.includes('artifact')) return '#f44336';
            return '#9e9e9e';
        }}
        
        // Check if item is stackable
        function isStackable(item) {{
            const stackableCategories = ['consumable', 'misc'];
            const stackableNames = ['arrow', 'bolt', 'ration', 'coin', 'potion', 'scroll', 'ammunition'];
            const nameLower = (item.name || '').toLowerCase();
            return stackableCategories.includes(item.category) || 
                   stackableNames.some(s => nameLower.includes(s));
        }}
        
        // Calculate total weight including quantities
        function calculateTotalWeight(items) {{
            return items.reduce(function(sum, item) {{
                const weight = parseFloat(item.weight) || 0;
                const quantity = parseInt(item.quantity) || 1;
                return sum + (weight * quantity);
            }}, 0);
        }}
        
        // 5e D&D Item Database
        const dndItems = {dnd_items_js};
        
        function initInventory() {
            loadInventoryData();
            renderPlayers();
            renderItemLookup();
            updateBagWeight();
        }
        
        function loadInventoryData() {
            try {
                if (typeof localStorage !== 'undefined') {
                    const saved = localStorage.getItem('inventory_data');
                    if (saved) {
                        inventoryData = JSON.parse(saved);
                    }
                }
            } catch(e) {
                console.error('Failed to load inventory data:', e);
            }
            
            // Initialize default players if none exist
            if (inventoryData.players.length === 0) {
                const defaultPlayers = ['Olpha', 'Felwin', 'Julior', 'Cooker', 'Thenn', 'Amok', 'Wren', 'Primevera'];
                inventoryData.players = defaultPlayers.map(name => ({
                    name: name,
                    gold: 0,
                    items: []
                }));
            }
            
            // Set party gold
            const partyGoldEl = getEl('partyGold');
            if (partyGoldEl) {
                partyGoldEl.value = inventoryData.partyGold || 0;
            }
        }
        
        function saveInventoryData() {
            try {
                if (typeof localStorage !== 'undefined') {
                    localStorage.setItem('inventory_data', JSON.stringify(inventoryData));
                }
            } catch(e) {
                console.error('Failed to save inventory data:', e);
            }
        }
        
        // Multi-select state
        let selectedItems = new Set();
        let multiSelectMode = false;
        
        function toggleMultiSelect() {
            multiSelectMode = !multiSelectMode;
            selectedItems.clear();
            updateSelectedCount();
            renderItemLookup();
        }
        
        function toggleItemSelection(itemName) {
            if (selectedItems.has(itemName)) {
                selectedItems.delete(itemName);
            } else {
                selectedItems.add(itemName);
            }
            updateSelectedCount();
            renderItemLookup();
        }
        
        function updateSelectedCount() {
            const countEl = getEl('selectedCount');
            const btnEl = getEl('addSelectedBtn');
            if (countEl) countEl.textContent = selectedItems.size;
            if (btnEl) {
                btnEl.disabled = selectedItems.size === 0;
                btnEl.style.opacity = selectedItems.size === 0 ? '0.5' : '1';
            }
        }
        
        function addSelectedItems() {
            if (selectedItems.size === 0) return;
            
            const container = prompt('Add to:\\n1. Bag of Holding (enter "bag")\\n2. Player name (enter player name)\\n\\nEnter choice:');
            if (!container) return;
            
            const itemsToAdd = Array.from(selectedItems).map(function(itemName) {
                return dndItems.find(function(item) { return item.name === itemName; });
            }).filter(function(item) { return item; });
            
            itemsToAdd.forEach(function(item) {{
                const itemCopy = JSON.parse(JSON.stringify(item));
                if (container.toLowerCase() === 'bag') {{
                    // Auto-stack if item already exists
                    const existingIndex = inventoryData.bagOfHolding.findIndex(function(existing) {{
                        return existing.name === itemCopy.name && 
                               (existing.rarity || '') === (itemCopy.rarity || '') &&
                               isStackable(itemCopy);
                    }});
                    
                    if (existingIndex >= 0 && isStackable(itemCopy)) {{
                        const existing = inventoryData.bagOfHolding[existingIndex];
                        existing.quantity = (parseInt(existing.quantity) || 1) + 1;
                    }} else {{
                        if (isStackable(itemCopy)) {{
                            itemCopy.quantity = 1;
                        }}
                        inventoryData.bagOfHolding.push(itemCopy);
                    }}
                }} else {{
                    const playerIndex = inventoryData.players.findIndex(function(p) {{
                        return p.name.toLowerCase() === container.toLowerCase();
                    }});
                    if (playerIndex >= 0) {{
                        // Auto-stack if item already exists
                        const existingIndex = inventoryData.players[playerIndex].items.findIndex(function(existing) {{
                            return existing.name === itemCopy.name && 
                                   (existing.rarity || '') === (itemCopy.rarity || '') &&
                                   isStackable(itemCopy);
                        }});
                        
                        if (existingIndex >= 0 && isStackable(itemCopy)) {{
                            const existing = inventoryData.players[playerIndex].items[existingIndex];
                            existing.quantity = (parseInt(existing.quantity) || 1) + 1;
                        }} else {{
                            if (isStackable(itemCopy)) {{
                                itemCopy.quantity = 1;
                            }}
                            inventoryData.players[playerIndex].items.push(itemCopy);
                        }}
                    }}
                }}
            }});
            
            if (container.toLowerCase() === 'bag') {
                updateBagWeight();
            } else {
                const playerIndex = inventoryData.players.findIndex(function(p) {
                    return p.name.toLowerCase() === container.toLowerCase();
                });
                if (playerIndex >= 0) {
                    renderPlayers();
                }
            }
            
            selectedItems.clear();
            updateSelectedCount();
            saveInventoryData();
            renderPlayers();
            renderBagOfHolding();
        }
        
        function renderPlayers() {{
            const container = getEl('playerInventories');
            if (!container) return;
            
            container.innerHTML = '';
            
            // Update player count badge
            const countBadge = getEl('playerCountBadge');
            if (countBadge) {{
                const totalItems = inventoryData.players.reduce(function(sum, player) {{
                    return sum + player.items.reduce(function(itemSum, item) {{
                        return itemSum + (parseInt(item.quantity) || 1);
                    }}, 0);
                }}, 0);
                countBadge.textContent = inventoryData.players.length + ' players, ' + totalItems + ' items';
            }}
            
            // Sort players alphabetically
            const sortedPlayers = inventoryData.players.slice().sort(function(a, b) {{
                return (a.name || '').localeCompare(b.name || '');
            }});
            
            sortedPlayers.forEach(function(player) {
                // Find original index for gold updates
                const index = inventoryData.players.findIndex(function(p) { return p.name === player.name; });
                const playerDiv = document.createElement('div');
                playerDiv.className = 'player-inventory';
                playerDiv.style.cssText = 'padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px; border: 1px solid rgba(255,255,255,0.2); margin-bottom: 8px;';
                
                const totalWeight = calculateTotalWeight(player.items);
                const itemCount = player.items.reduce(function(sum, item) {{
                    return sum + (parseInt(item.quantity) || 1);
                }}, 0);
                
                playerDiv.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div style="display: flex; align-items: center; gap: 8px; flex: 1;">
                            <span style="color: #FFD700; font-weight: bold; font-size: 0.9em;">${{player.name}}</span>
                            <span style="background: rgba(76,175,80,0.3); color: #4caf50; padding: 2px 6px; border-radius: 10px; font-size: 0.7em; font-weight: bold;">${{itemCount}} items</span>
                            <input type="number" value="${{player.gold || 0}}" min="0" step="0.01" 
                                   onchange="updatePlayerGold(${{index}}, this.value)"
                                   style="padding: 4px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.5); color: #fff; width: 70px; font-size: 0.85em;">
                            <span style="font-size: 0.75em; color: #ccc;">gp</span>
                            <span style="font-size: 0.75em; color: ${{totalWeight > 150 ? '#f44336' : totalWeight > 100 ? '#ff9800' : '#888'}}; margin-left: auto;">${{totalWeight.toFixed(1)}} lbs</span>
                        </div>
                        <button onclick="removePlayer(${{index}})" style="padding: 4px 8px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.8em;">🗑️</button>
                    </div>
                    <div class="inventory-container" 
                         id="player_${index}_container"
                         data-container-id="player_${index}"
                         ondrop="drop(event, 'player_${index}')" 
                         ondragover="allowDrop(event)"
                         ontouchmove="if(event.touches.length === 1) handleTouchMove(event)"
                         ontouchend="if(event.changedTouches.length === 1) handleTouchEnd(event)"
                         style="min-height: 60px; max-height: 150px; overflow-y: auto; -webkit-overflow-scrolling: touch; padding: 6px; background: rgba(0,0,0,0.2); border-radius: 4px; border: 2px dashed rgba(255,255,255,0.3); touch-action: pan-y;">
                        ${player.items.length === 0 ? '<p style="color: #888; text-align: center; margin: 5px 0; font-size: 0.8em;">Drop items here</p>' : ''}
                        ${player.items.map(function(item, itemIndex) {
                            // Use the original player's items array to get correct index
                            const originalPlayer = inventoryData.players[index];
                            const originalItemIndex = originalPlayer ? originalPlayer.items.indexOf(item) : itemIndex;
                            return renderItem(item, 'player_' + index, originalItemIndex >= 0 ? originalItemIndex : itemIndex);
                        }).join('')}
                    </div>
                `;
                
                container.appendChild(playerDiv);
            });
        }
        
        function renderItem(item, containerId, index) {{
            const itemId = containerId + '_' + index;
            const containerIdEscaped = (containerId || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
            const itemNameEscaped = (item.name || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
            const itemJsonEscaped = JSON.stringify(item).replace(/'/g, "\\'").replace(/"/g, '&quot;');
            const quantity = parseInt(item.quantity) || 1;
            const rarityColor = getRarityColor(item.rarity);
            const isStackableItem = isStackable(item);
            
            // Build properties display
            let propertiesHtml = '';
            if (item.damage) propertiesHtml += `<span style="color: #ff6b6b;">⚔ ${{item.damage}}</span> `;
            if (item.ac) propertiesHtml += `<span style="color: #4ecdc4;">🛡 AC ${{item.ac}}</span> `;
            if (item.properties && item.properties.length > 0) {{
                propertiesHtml += `<span style="color: #95e1d3;">${{item.properties.slice(0, 2).join(', ')}}</span> `;
            }}
            if (item.attunement) propertiesHtml += `<span style="color: #f38181;">🔗 Attuned</span> `;
            
            // Prepare item data for touch events
            const itemForTouch = JSON.stringify(item).replace(/'/g, "\\'").replace(/"/g, '&quot;');
            
            // Use base64 encoding to avoid all quote/special character issues
            const itemJsonBase64 = btoa(JSON.stringify(item));
            
            return `
                <div class="inventory-item" 
                     draggable="true" 
                     ondragstart="drag(event, '${{itemId}}', '${{containerIdEscaped}}')"
                     onclick="if(!event.target.closest('button')) { try { const itemJson = atob(this.dataset.itemJsonBase64 || ''); if(itemJson) showItemDescription(JSON.parse(itemJson)); } catch(e) { console.error('Error showing item description:', e); } }"
                     ontouchstart="if(event.touches.length === 1 && !event.target.closest('button')) { handleTouchStart(event, JSON.parse('${{itemForTouch}}'), '${{containerIdEscaped}}'); }"
                     ontouchmove="if(event.touches.length === 1 && !event.target.closest('button')) { handleTouchMove(event); }"
                     ontouchend="if(event.changedTouches.length === 1 && !event.target.closest('button')) { handleTouchEnd(event); }"
                     data-item-id="${{itemId}}"
                     data-container="${{containerIdEscaped}}"
                     data-item-index="${{index}}"
                     data-item-json-base64="${{itemJsonBase64}}"
                     style="padding: 6px; margin: 3px 0; background: rgba(255,255,255,0.1); border-radius: 4px; border-left: 3px solid ${{rarityColor}}; font-size: 0.85em; touch-action: pan-y;">
                    <div style="flex: 1; min-width: 0;">
                        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                            <strong style="color: #fff; font-size: 0.9em;">${{item.name}}</strong>
                            ${{item.rarity ? `<span style="color: ${{rarityColor}}; font-size: 0.7em; font-weight: bold;">${{item.rarity}}</span>` : ''}}
                            ${{item.type === 'magic' ? '<span style="color: #9C27B0;">✨</span>' : ''}}
                        </div>
                        <div style="font-size: 0.75em; color: #ccc; margin-bottom: 2px;">
                            ${{item.category}} • ${{(parseFloat(item.weight) * quantity).toFixed(2)}} lbs
                        </div>
                        ${{propertiesHtml ? `<div style="font-size: 0.7em; color: #aaa; margin-top: 2px;">${{propertiesHtml}}</div>` : ''}}
                    </div>
                    <div style="display: flex; align-items: center; gap: 4px;">
                        ${{isStackableItem ? `
                            <button onclick="event.stopPropagation(); event.preventDefault(); changeQuantity('${{containerIdEscaped}}', ${{index}}, -1); return false;" 
                                    ontouchstart="event.stopPropagation(); event.preventDefault(); changeQuantity('${{containerIdEscaped}}', ${{index}}, -1); return false;"
                                    style="padding: 2px 6px; background: #666; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 0.7em; touch-action: manipulation; -webkit-tap-highlight-color: rgba(102, 102, 102, 0.3); min-width: 44px; min-height: 44px; display: flex; align-items: center; justify-content: center;">−</button>
                            <span style="min-width: 30px; text-align: center; font-weight: bold; color: #fff;">${{quantity}}</span>
                            <button onclick="event.stopPropagation(); event.preventDefault(); changeQuantity('${{containerIdEscaped}}', ${{index}}, 1); return false;" 
                                    ontouchstart="event.stopPropagation(); event.preventDefault(); changeQuantity('${{containerIdEscaped}}', ${{index}}, 1); return false;"
                                    style="padding: 2px 6px; background: #666; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 0.7em; touch-action: manipulation; -webkit-tap-highlight-color: rgba(102, 102, 102, 0.3); min-width: 44px; min-height: 44px; display: flex; align-items: center; justify-content: center;">+</button>
                        ` : ''}}
                        <button onclick="event.stopPropagation(); event.preventDefault(); removeItem('${{containerIdEscaped}}', ${{index}}); return false;" 
                                ontouchstart="event.stopPropagation(); event.preventDefault(); removeItem('${{containerIdEscaped}}', ${{index}}); return false;"
                                style="padding: 3px 6px; background: #f44336; color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 0.75em; margin-left: 5px; touch-action: manipulation; -webkit-tap-highlight-color: rgba(244, 67, 54, 0.3); min-width: 44px; min-height: 44px; display: flex; align-items: center; justify-content: center;">✕</button>
                    </div>
                </div>
            `;
        }}
        
        function showItemDescription(itemJson) {
            try {
                let item = typeof itemJson === 'string' ? JSON.parse(itemJson.replace(/\\'/g, "'").replace(/&quot;/g, '"')) : itemJson;
                
                // If item doesn't have a description, try to find the full item data from dndItems
                if (!item.description && !item.notes && !item.entries && typeof dndItems !== 'undefined') {
                    const fullItem = dndItems.find(function(dndItem) {
                        return dndItem.name === item.name;
                    });
                    if (fullItem) {
                        // Merge full item data with current item (preserve any custom properties)
                        item = Object.assign({}, fullItem, item);
                    }
                }
                
                const description = item.description || item.notes || item.entries || 'No description available.';
                const modal = document.createElement('div');
                modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; display: flex; align-items: center; justify-content: center;';
                modal.onclick = function(e) {
                    if (e.target === modal) {
                        document.body.removeChild(modal);
                    }
                };
                
                let detailsHtml = '<div style="margin-bottom: 10px;">';
                detailsHtml += '<strong>Category:</strong> ' + (item.category || 'N/A') + '<br>';
                detailsHtml += '<strong>Weight:</strong> ' + (item.weight || 0) + ' lbs<br>';
                detailsHtml += '<strong>Cost:</strong> ' + (item.cost || 'N/A') + '<br>';
                detailsHtml += '<strong>Type:</strong> ' + (item.type || 'mundane') + '<br>';
                
                // Weapon properties
                if (item.damage) detailsHtml += '<strong>Damage:</strong> ' + item.damage + '<br>';
                if (item.damageType) detailsHtml += '<strong>Damage Type:</strong> ' + item.damageType + '<br>';
                if (item.properties && item.properties.length > 0) {
                    detailsHtml += '<strong>Properties:</strong> ' + item.properties.join(', ') + '<br>';
                }
                if (item.range) detailsHtml += '<strong>Range:</strong> ' + item.range + '<br>';
                
                // Armor properties
                if (item.ac) detailsHtml += '<strong>Armor Class:</strong> ' + item.ac + '<br>';
                if (item.armorType) detailsHtml += '<strong>Armor Type:</strong> ' + item.armorType + '<br>';
                if (item.stealth !== undefined) {
                    detailsHtml += '<strong>Stealth:</strong> ' + (item.stealth ? 'Disadvantage' : 'No disadvantage') + '<br>';
                }
                
                // Magic item properties
                if (item.rarity) detailsHtml += '<strong>Rarity:</strong> ' + item.rarity + '<br>';
                if (item.attunement) detailsHtml += '<strong>Attunement:</strong> Required<br>';
                if (item.attunement === false) detailsHtml += '<strong>Attunement:</strong> Not required<br>';
                
                // Source
                if (item.source) detailsHtml += '<strong>Source:</strong> ' + item.source + '<br>';
                
                detailsHtml += '</div>';
                
                modal.innerHTML = `
                    <div style="background: rgba(20,20,30,0.95); border: 2px solid #FFD700; border-radius: 10px; padding: 20px; max-width: 600px; max-height: 80vh; overflow-y: auto; color: #fff;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <h2 style="color: #FFD700; margin: 0;">${item.name}</h2>
                            <button onclick="this.closest('div[style*=\\'position: fixed\\']').remove()" style="background: #f44336; color: white; border: none; border-radius: 5px; padding: 5px 10px; cursor: pointer; font-size: 1.2em;">✕</button>
                        </div>
                        ${detailsHtml}
                        <div style="border-top: 1px solid rgba(255,255,255,0.3); padding-top: 10px; margin-top: 10px;">
                            <strong>Description:</strong>
                            <div style="margin-top: 5px; line-height: 1.5; white-space: pre-wrap;">${typeof description === 'string' ? description : (Array.isArray(description) ? description.join('\\n\\n') : JSON.stringify(description))}</div>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
            } catch(e) {
                console.error('Error showing item description:', e);
                alert('Error displaying item description: ' + e.message);
            }
        }
        
        function renderItemLookup() {
            const container = getEl('itemLookup');
            if (!container) return;
            
            container.innerHTML = '';
            
            // Add multi-select toggle button at top
            const toggleBtn = document.createElement('button');
            toggleBtn.textContent = multiSelectMode ? '✓ Multi-Select ON' : 'Multi-Select OFF';
            toggleBtn.onclick = toggleMultiSelect;
            toggleBtn.style.cssText = 'width: 100%; padding: 6px; margin-bottom: 8px; background: ' + (multiSelectMode ? '#4CAF50' : '#666') + '; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85em;';
            container.appendChild(toggleBtn);
            
            dndItems.forEach(function(item) {{
                const itemDiv = document.createElement('div');
                itemDiv.className = 'lookup-item';
                itemDiv.dataset.category = item.category || '';
                itemDiv.dataset.name = item.name.toLowerCase();
                itemDiv.dataset.itemName = item.name;
                itemDiv.dataset.type = item.type || '';
                itemDiv.dataset.rarity = item.rarity || '';
                itemDiv.dataset.weight = item.weight || 0;
                itemDiv.dataset.cost = item.cost || '';
                
                const isSelected = selectedItems.has(item.name);
                itemDiv.style.cssText = 'padding: 6px; background: ' + (isSelected ? 'rgba(76,175,80,0.3)' : 'rgba(255,255,255,0.1)') + '; border-radius: 4px; cursor: pointer; border: 1px solid ' + (isSelected ? 'rgba(76,175,80,0.8)' : 'rgba(255,255,255,0.2)') + '; transition: all 0.2s; font-size: 0.8em;';
                
                itemDiv.onmouseover = function() { 
                    if (!isSelected) this.style.background = 'rgba(255,255,255,0.2)'; 
                };
                itemDiv.onmouseout = function() { 
                    if (!isSelected) this.style.background = 'rgba(255,255,255,0.1)'; 
                };
                
                if (multiSelectMode) {
                    itemDiv.onclick = function(e) { 
                        e.stopPropagation();
                        toggleItemSelection(item.name);
                    };
                } else {
                    // Mobile: Add touch support with proper scroll handling
                    let touchStartTime = 0;
                    let itemTouchStartX = 0;
                    let itemTouchStartY = 0;
                    let itemTouchMoved = false;
                    
                    itemDiv.ontouchstart = function(e) {
                        touchStartTime = Date.now();
                        itemTouchStartX = e.touches[0].clientX;
                        itemTouchStartY = e.touches[0].clientY;
                        itemTouchMoved = false;
                        handleTouchStart(e, item, 'lookup');
                    };
                    
                    itemDiv.ontouchmove = function(e) {
                        if (!e.touches || !e.touches[0]) return;
                        
                        const touch = e.touches[0];
                        const deltaY = Math.abs(touch.clientY - itemTouchStartY);
                        const deltaX = Math.abs(touch.clientX - itemTouchStartX);
                        
                        // Only mark as moved if significant movement
                        if (deltaY > 10 || deltaX > 10) {
                            itemTouchMoved = true;
                        }
                        
                        // Only prevent default if clearly dragging (horizontal movement)
                        // Allow vertical scrolling
                        if (deltaX > deltaY && deltaX > 15) {
                            e.preventDefault();
                        }
                        
                        handleTouchMove(e);
                    };
                    
                    itemDiv.ontouchend = function(e) {
                        if (!e.changedTouches || !e.changedTouches[0]) {
                            // Reset touch state
                            touchStartItem = null;
                            touchStartContainer = null;
                            touchStartItemData = null;
                            itemTouchMoved = false;
                            return;
                        }
                        
                        const touchDuration = Date.now() - touchStartTime;
                        const touchEndY = e.changedTouches[0].clientY;
                        const touchEndX = e.changedTouches[0].clientX;
                        const touchDistanceY = Math.abs(touchEndY - itemTouchStartY);
                        const touchDistanceX = Math.abs(touchEndX - itemTouchStartX);
                        
                        // If quick tap (not a drag, not scrolled), show description
                        if (!itemTouchMoved && touchDuration < 300 && touchDistanceY < 10 && touchDistanceX < 10) {
                            e.preventDefault();
                            e.stopPropagation();
                            showItemDescription(item);
                            // Reset touch state
                            touchStartItem = null;
                            touchStartContainer = null;
                            touchStartItemData = null;
                            touchMoved = false;
                        } else if (itemTouchMoved || touchDistanceX > 20 || touchDistanceY > 20) {
                            // Handle as potential drag - let handleTouchEnd find the target
                            handleTouchEnd(e, null);
                        } else {
                            // Reset touch state if no action
                            touchStartItem = null;
                            touchStartContainer = null;
                            touchStartItemData = null;
                            touchMoved = false;
                        }
                        
                        itemTouchMoved = false;
                    };
                    
                    // Desktop: Click to show description, double-click to add
                    itemDiv.onclick = function(e) { 
                        // Only handle click if not a touch device
                        if (!('ontouchstart' in window)) {
                            e.stopPropagation();
                            showItemDescription(item);
                        }
                    };
                    itemDiv.ondblclick = function(e) {
                        if (!('ontouchstart' in window)) {
                            e.stopPropagation();
                            addItemFromLookup(item);
                        }
                    };
                    itemDiv.draggable = true;
                    itemDiv.ondragstart = function(e) {
                        e.dataTransfer.setData('item', JSON.stringify(item));
                        e.dataTransfer.setData('source', 'lookup');
                    };
                    
                    // Ensure item can be scrolled over
                    itemDiv.style.touchAction = 'pan-y';
                }
                
                const itemNameEscaped = item.name.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                const checkboxHtml = multiSelectMode ? '<input type="checkbox" ' + (isSelected ? 'checked' : '') + ' style="margin-right: 6px;" onclick="event.stopPropagation(); toggleItemSelection(\\'' + itemNameEscaped + '\\');">' : '';
                const rarityColor = getRarityColor(item.rarity);
                itemDiv.innerHTML = `
                    ${{checkboxHtml}}
                    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 2px;">
                        <div style="font-weight: bold; color: #fff; font-size: 0.9em;">${{item.name}}</div>
                        ${{item.rarity ? `<span style="color: ${{rarityColor}}; font-size: 0.7em; font-weight: bold;">${{item.rarity}}</span>` : ''}}
                        ${{item.type === 'magic' ? ' <span style="color: #9C27B0;">✨</span>' : ''}}
                    </div>
                    <div style="font-size: 0.75em; color: #ccc;">
                        ${{item.category}} • ${{item.weight}} lbs
                        ${{item.cost ? ' • ' + item.cost : ''}}
                    </div>
                `;
                
                container.appendChild(itemDiv);
            });
        }
        
        function filterItems() {{
            const search = (getEl('itemSearch')?.value || '').toLowerCase();
            const category = getEl('itemCategory')?.value || '';
            const type = getEl('itemType')?.value || '';
            const rarity = getEl('itemRarity')?.value || '';
            const sortBy = getEl('itemSort')?.value || 'name';
            
            const items = Array.from(document.querySelectorAll('.lookup-item'));
            const visibleItems = [];
            
            items.forEach(function(itemEl) {{
                const itemName = itemEl.dataset.name || '';
                const itemCategory = itemEl.dataset.category || '';
                const itemType = itemEl.dataset.type || '';
                const itemRarity = itemEl.dataset.rarity || '';
                
                const matchesSearch = !search || itemName.indexOf(search) !== -1;
                const matchesCategory = !category || itemCategory === category;
                const matchesType = !type || itemType === type;
                const matchesRarity = !rarity || itemRarity.toLowerCase().includes(rarity.toLowerCase());
                
                if (matchesSearch && matchesCategory && matchesType && matchesRarity) {{
                    itemEl.style.display = 'block';
                    visibleItems.push(itemEl);
                }} else {{
                    itemEl.style.display = 'none';
                }}
            }});
            
            // Sort visible items
            if (sortBy !== 'name') {{
                const container = getEl('itemLookup');
                if (container) {{
                    visibleItems.sort(function(a, b) {{
                        let aVal, bVal;
                        if (sortBy === 'weight') {{
                            aVal = parseFloat(a.dataset.weight) || 0;
                            bVal = parseFloat(b.dataset.weight) || 0;
                        }} else if (sortBy === 'cost') {{
                            aVal = (a.dataset.cost || '').toLowerCase();
                            bVal = (b.dataset.cost || '').toLowerCase();
                        }} else if (sortBy === 'rarity') {{
                            const rarityOrder = {{'common': 1, 'uncommon': 2, 'rare': 3, 'very rare': 4, 'legendary': 5, 'artifact': 6}};
                            aVal = rarityOrder[(a.dataset.rarity || '').toLowerCase()] || 0;
                            bVal = rarityOrder[(b.dataset.rarity || '').toLowerCase()] || 0;
                        }} else if (sortBy === 'category') {{
                            aVal = (a.dataset.category || '').toLowerCase();
                            bVal = (b.dataset.category || '').toLowerCase();
                        }}
                        
                        if (typeof aVal === 'number') {{
                            return aVal - bVal;
                        }}
                        return aVal.localeCompare(bVal);
                    }});
                    
                    // Reorder in DOM
                    visibleItems.forEach(function(itemEl) {{
                        container.appendChild(itemEl);
                    }});
                }}
            }}
        }}
        
        function addItemFromLookup(item) {
            // Show dialog to select container
            const container = prompt('Add to:\\n1. Bag of Holding (enter "bag")\\n2. Player name (enter player name)\\n\\nEnter choice:');
            
            if (!container) return;
            
            const itemCopy = JSON.parse(JSON.stringify(item));
            
            if (container.toLowerCase() === 'bag') {{
                // Auto-stack if item already exists
                const existingIndex = inventoryData.bagOfHolding.findIndex(function(existing) {{
                    return existing.name === itemCopy.name && 
                           (existing.rarity || '') === (itemCopy.rarity || '') &&
                           isStackable(itemCopy);
                }});
                
                if (existingIndex >= 0 && isStackable(itemCopy)) {{
                    const existing = inventoryData.bagOfHolding[existingIndex];
                    existing.quantity = (parseInt(existing.quantity) || 1) + 1;
                }} else {{
                    if (isStackable(itemCopy)) {{
                        itemCopy.quantity = 1;
                    }}
                    inventoryData.bagOfHolding.push(itemCopy);
                }}
                updateBagWeight();
            }} else {{
                const playerIndex = inventoryData.players.findIndex(function(p) {{
                    return p.name.toLowerCase() === container.toLowerCase();
                }});
                if (playerIndex >= 0) {{
                    // Auto-stack if item already exists
                    const existingIndex = inventoryData.players[playerIndex].items.findIndex(function(existing) {{
                        return existing.name === itemCopy.name && 
                               (existing.rarity || '') === (itemCopy.rarity || '') &&
                               isStackable(itemCopy);
                    }});
                    
                    if (existingIndex >= 0 && isStackable(itemCopy)) {{
                        const existing = inventoryData.players[playerIndex].items[existingIndex];
                        existing.quantity = (parseInt(existing.quantity) || 1) + 1;
                    }} else {{
                        if (isStackable(itemCopy)) {{
                            itemCopy.quantity = 1;
                        }}
                        inventoryData.players[playerIndex].items.push(itemCopy);
                    }}
                }} else {{
                    alert('Player not found. Please enter exact player name.');
                    return;
                }}
            }}
            
            saveInventoryData();
            renderPlayers();
            renderBagOfHolding();
        }
        
        function renderBagOfHolding() {
            const container = getEl('bagOfHolding');
            if (!container) return;
            
            container.innerHTML = '';
            
            if (inventoryData.bagOfHolding.length === 0) {
                container.innerHTML = '<p style="color: #888; text-align: center; margin: 10px 0; font-size: 0.8em;">Drop items here</p>';
                return;
            }
            
            inventoryData.bagOfHolding.forEach(function(item, index) {
                const itemDiv = document.createElement('div');
                itemDiv.innerHTML = renderItem(item, 'bagOfHolding', index);
                container.appendChild(itemDiv);
            });
        }
        
        function updateBagWeight() {{
            const totalWeight = calculateTotalWeight(inventoryData.bagOfHolding);
            
            const weightEl = getEl('bagWeight');
            const weightContainer = weightEl ? weightEl.parentElement : null;
            if (weightEl && weightContainer) {{
                if (totalWeight > 500) {{
                    weightContainer.innerHTML = `Weight: <span id="bagWeight" style="color: #f44336; font-weight: bold;">${{totalWeight.toFixed(1)}}</span> / 500 lbs <span style="color: #f44336;">⚠ OVER CAPACITY!</span>`;
                }} else if (totalWeight > 400) {{
                    weightContainer.innerHTML = `Weight: <span id="bagWeight" style="color: #ff9800; font-weight: bold;">${{totalWeight.toFixed(1)}}</span> / 500 lbs <span style="color: #ff9800;">⚠ Warning</span>`;
                }} else {{
                    weightContainer.innerHTML = `Weight: <span id="bagWeight" style="color: #ccc;">${{totalWeight.toFixed(1)}}</span> / 500 lbs`;
                }}
            }}
            
            renderBagOfHolding();
        }
        
        function toggleSection(sectionId) {{
            const section = getEl(sectionId);
            const toggle = getEl(sectionId + 'Toggle');
            if (section && toggle) {{
                if (section.style.display === 'none') {{
                    section.style.display = 'block';
                    toggle.textContent = '▼';
                }} else {{
                    section.style.display = 'none';
                    toggle.textContent = '▶';
                }}
            }}
        }}
        
        function changeQuantity(containerId, index, delta) {{
            let items;
            if (containerId === 'bagOfHolding') {{
                items = inventoryData.bagOfHolding;
            }} else if (containerId.startsWith('player_')) {{
                const playerIndex = parseInt(containerId.replace('player_', ''));
                items = inventoryData.players[playerIndex].items;
            }} else {{
                return;
            }}
            
            if (index < 0 || index >= items.length) return;
            
            const item = items[index];
            const currentQty = parseInt(item.quantity) || 1;
            const newQty = Math.max(1, currentQty + delta);
            
            if (newQty === 1) {{
                delete item.quantity;
            }} else {{
                item.quantity = newQty;
            }}
            
            saveInventoryData();
            if (containerId === 'bagOfHolding') {{
                updateBagWeight();
                renderBagOfHolding();
            }} else {{
                renderPlayers();
            }}
        }}
        
        function updatePartyGold() {{
            const goldEl = getEl('partyGold');
            if (goldEl) {{
                inventoryData.partyGold = parseFloat(goldEl.value) || 0;
                saveInventoryData();
            }
        }
        
        function updatePlayerGold(playerIndex, gold) {
            if (inventoryData.players[playerIndex]) {
                inventoryData.players[playerIndex].gold = parseFloat(gold) || 0;
                saveInventoryData();
            }
        }
        
        function addPlayer() {
            const name = prompt('Enter player name:');
            if (name) {
                inventoryData.players.push({
                    name: name,
                    gold: 0,
                    items: []
                });
                saveInventoryData();
                renderPlayers();
            }
        }
        
        function removePlayer(index) {
            if (confirm('Remove this player and all their items?')) {
                inventoryData.players.splice(index, 1);
                saveInventoryData();
                renderPlayers();
            }
        }
        
        function removeItem(containerId, index) {
            // Ensure index is a number
            index = parseInt(index);
            if (isNaN(index) || index < 0) {
                console.error('Invalid index for removeItem:', index);
                return;
            }
            
            if (containerId === 'bagOfHolding') {
                if (index >= 0 && index < inventoryData.bagOfHolding.length) {
                    inventoryData.bagOfHolding.splice(index, 1);
                    updateBagWeight();
                    saveInventoryData();
                }
            } else if (containerId.startsWith('player_')) {
                const playerIndex = parseInt(containerId.split('_')[1]);
                if (inventoryData.players[playerIndex] && index >= 0 && index < inventoryData.players[playerIndex].items.length) {
                    inventoryData.players[playerIndex].items.splice(index, 1);
                    renderPlayers();
                    saveInventoryData();
                }
            }
        }
        
        // Drag and Drop Functions
        // Mobile: Touch support for drag and drop
        function allowDrop(ev) {
            ev.preventDefault();
        }
        
        // Mobile: Global touch state (more reliable than element properties)
        let activeTouchElement = null;
        let activeTouchData = null;
        
        function drag(ev, itemId, sourceContainer) {
            // Get the item data from the DOM element
            const itemElement = ev.target.closest('.inventory-item');
            if (itemElement) {
                const itemIndex = parseInt(itemElement.dataset.itemIndex || '-1');
                let item = null;
                
                // Get item from the correct container
                if (sourceContainer === 'bagOfHolding') {
                    item = inventoryData.bagOfHolding[itemIndex];
                } else if (sourceContainer.startsWith('player_')) {
                    const playerIndex = parseInt(sourceContainer.split('_')[1]);
                    if (inventoryData.players[playerIndex]) {
                        item = inventoryData.players[playerIndex].items[itemIndex];
                    }
                }
                
                // Set item data for lookup table compatibility
                if (item) {
                    ev.dataTransfer.setData('item', JSON.stringify(item));
                    ev.dataTransfer.setData('source', sourceContainer);
                }
            }
            
            // Also set the original data
            ev.dataTransfer.setData('itemId', itemId);
            ev.dataTransfer.setData('sourceContainer', sourceContainer);
        }
        
        // Mobile: Simplified touch handling - use global state
        function handleTouchStart(ev, item, source) {
            try {
                if (!ev || !ev.touches || !ev.touches[0]) return;
                
                // Find the inventory item element (might be nested inside buttons/spans)
                let element = ev.target;
                while (element && !element.classList.contains('inventory-item')) {
                    element = element.parentElement;
                }
                if (!element) element = ev.currentTarget || ev.target;
                
                let itemObj = item;
                if (typeof item === 'string') {
                    try {
                        itemObj = JSON.parse(item);
                    } catch(e) {
                        console.error('Failed to parse item:', e);
                        return;
                    }
                }
                
                // Store globally for reliability across touch events
                activeTouchElement = element;
                activeTouchData = {
                    item: itemObj,
                    source: source || 'lookup',
                    itemData: JSON.stringify(itemObj),
                    startX: ev.touches[0].clientX,
                    startY: ev.touches[0].clientY,
                    moved: false
                };
                
                // Visual feedback
                element.style.opacity = '0.7';
                element.style.transform = 'scale(0.95)';
            } catch(e) {
                console.error('handleTouchStart error:', e);
            }
        }
        
        // Mobile: Track movement
        function handleTouchMove(ev) {
            try {
                if (!activeTouchData || !ev.touches || !ev.touches[0]) return;
                
                const touch = ev.touches[0];
                const deltaX = Math.abs(touch.clientX - activeTouchData.startX);
                const deltaY = Math.abs(touch.clientY - activeTouchData.startY);
                
                if (deltaX > 3 || deltaY > 3) {
                    activeTouchData.moved = true;
                    if (deltaX > 5) {
                        ev.preventDefault();
                    }
                }
            } catch(e) {
                console.error('handleTouchMove error:', e);
            }
        }
        
        // Mobile: Handle drop - use global state
        function handleTouchEnd(ev) {
            try {
                if (!activeTouchData || !ev.changedTouches || !ev.changedTouches[0]) {
                    // Cleanup
                    if (activeTouchElement) {
                        activeTouchElement.style.opacity = '';
                        activeTouchElement.style.transform = '';
                    }
                    activeTouchElement = null;
                    activeTouchData = null;
                    return;
                }
                
                const touch = ev.changedTouches[0];
                const deltaX = Math.abs(touch.clientX - activeTouchData.startX);
                const deltaY = Math.abs(touch.clientY - activeTouchData.startY);
                
                // Restore visual
                if (activeTouchElement) {
                    activeTouchElement.style.opacity = '';
                    activeTouchElement.style.transform = '';
                }
                
                // If moved, treat as drag
                if (activeTouchData.moved || deltaX > 3 || deltaY > 3) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    
                    // Find drop target - try multiple coordinates for reliability
                    let containerId = null;
                    const offsets = [[0, 0], [-10, -10], [10, 10], [-10, 10], [10, -10]];
                    
                    for (let i = 0; i < offsets.length && !containerId; i++) {
                        const targetElement = document.elementFromPoint(
                            touch.clientX + offsets[i][0],
                            touch.clientY + offsets[i][1]
                        );
                        
                        if (targetElement) {
                            // Try to find container
                            const container = targetElement.closest('.inventory-container') || 
                                             targetElement.closest('#bagOfHolding') ||
                                             (targetElement.id === 'bagOfHolding' ? targetElement : null);
                            
                            if (container) {
                                if (container.dataset && container.dataset.containerId) {
                                    containerId = container.dataset.containerId;
                                }} else if (container.id === 'bagOfHolding') {{
                                    containerId = 'bagOfHolding';
                                }} else if (container.id && container.id.endsWith('_container')) {{
                                    containerId = container.id.replace('_container', '');
                                }} else if (container.id && container.id.startsWith('player_')) {{
                                    containerId = container.id;
                                }}
                            }}
                        }}
                    }}
                    
                    if (containerId) {
                        // Create fake drop event
                        const fakeEvent = {{
                            preventDefault: function() {{}},
                            stopPropagation: function() {{}},
                            dataTransfer: {{
                                getData: function(key) {{
                                    if (key === 'item') return activeTouchData.itemData;
                                    if (key === 'source') return activeTouchData.source || 'lookup';
                                    if (key === 'itemId') return '';
                                    if (key === 'sourceContainer') return activeTouchData.source || '';
                                    return '';
                                }}
                            }}
                        }};
                        
                        // Call drop function
                        try {
                            drop(fakeEvent, containerId);
                            // Force UI update
                            setTimeout(function() {{
                                if (containerId === 'bagOfHolding') {{
                                    renderBagOfHolding();
                                }} else if (containerId.startsWith('player_')) {{
                                    renderPlayers();
                                }}
                            }}, 100);
                        }} catch(e) {{
                            console.error('Drop error:', e);
                            alert('Error dropping item: ' + (e.message || 'Unknown error'));
                        }}
                    }}
                }} else {{
                    // Quick tap - show description
                    try {
                        let itemData = activeTouchData.item;
                        if (!itemData && activeTouchElement && activeTouchElement.dataset && activeTouchElement.dataset.itemJsonBase64) {
                            try {
                                const itemJson = atob(activeTouchElement.dataset.itemJsonBase64);
                                itemData = JSON.parse(itemJson);
                            } catch(e) {
                                console.error('Failed to parse item data from dataset:', e);
                            }
                        }
                        if (!itemData && activeTouchData.itemData) {
                            try {
                                itemData = typeof activeTouchData.itemData === 'string' ? JSON.parse(activeTouchData.itemData) : activeTouchData.itemData;
                            } catch(e) {
                                console.error('Failed to parse item data:', e);
                            }
                        }
                        if (itemData) {
                            showItemDescription(itemData);
                        }
                    } catch(e) {
                        console.error('Show description error:', e);
                    }
                }
                
                // Cleanup
                activeTouchElement = null;
                activeTouchData = null;
            } catch(e) {
                console.error('handleTouchEnd error:', e);
                // Ensure cleanup
                if (activeTouchElement) {
                    activeTouchElement.style.opacity = '';
                    activeTouchElement.style.transform = '';
                }
                activeTouchElement = null;
                activeTouchData = null;
            }
        }
        
        function drop(ev, targetContainer) {
            ev.preventDefault();
            
            // Check if dragging from lookup table or inventory
            const itemData = ev.dataTransfer.getData('item');
            const source = ev.dataTransfer.getData('source');
            const sourceContainer = ev.dataTransfer.getData('sourceContainer');
            let itemId = ev.dataTransfer.getData('itemId');
            
            // Handle drag from lookup table or inventory with item data
            if (itemData && (source === 'lookup' || !sourceContainer)) {{
                // Dragging from lookup table
                logger.log('Processing drop from lookup table');
                const item = JSON.parse(itemData);
                const itemCopy = JSON.parse(JSON.stringify(item));
                logger.log('Item to add:', itemCopy.name);
                
                if (targetContainer === 'bagOfHolding') {{
                    // Auto-stack if item already exists
                    const existingIndex = inventoryData.bagOfHolding.findIndex(function(existing) {{
                        return existing.name === itemCopy.name && 
                               (existing.rarity || '') === (itemCopy.rarity || '') &&
                               isStackable(itemCopy);
                    }});
                    
                    if (existingIndex >= 0 && isStackable(itemCopy)) {{
                        const existing = inventoryData.bagOfHolding[existingIndex];
                        existing.quantity = (parseInt(existing.quantity) || 1) + 1;
                    }} else {{
                        if (isStackable(itemCopy)) {{
                            itemCopy.quantity = 1;
                        }}
                        inventoryData.bagOfHolding.push(itemCopy);
                    }}
                    updateBagWeight();
                }} else if (targetContainer && typeof targetContainer === 'string' && targetContainer.startsWith('player_')) {{
                    const playerIndex = parseInt(targetContainer.split('_')[1]);
                    logger.log('Adding item to player index', playerIndex, 'container:', targetContainer);
                    logger.log('Total players:', inventoryData.players ? inventoryData.players.length : 0);
                    if (inventoryData.players && inventoryData.players[playerIndex]) {{
                        // Auto-stack if item already exists
                        const existingIndex = inventoryData.players[playerIndex].items.findIndex(function(existing) {{
                            return existing.name === itemCopy.name && 
                                   (existing.rarity || '') === (itemCopy.rarity || '') &&
                                   isStackable(itemCopy);
                        }});
                        
                        if (existingIndex >= 0 && isStackable(itemCopy)) {{
                            const existing = inventoryData.players[playerIndex].items[existingIndex];
                            existing.quantity = (parseInt(existing.quantity) || 1) + 1;
                            logger.log('Stacked item, new quantity:', existing.quantity);
                        }} else {{
                            if (isStackable(itemCopy)) {{
                                itemCopy.quantity = 1;
                            }}
                            inventoryData.players[playerIndex].items.push(itemCopy);
                            logger.log('Added new item to player inventory. Total items:', inventoryData.players[playerIndex].items.length);
                        }}
                        renderPlayers();
                        renderBagOfHolding();
                    }} else {{
                        logger.error('Player index', playerIndex, 'not found in inventoryData.players');
                    }}
                }} else {{
                    logger.warn('Invalid targetContainer:', targetContainer, 'type:', typeof targetContainer);
                }}
                saveInventoryData();
                logger.log('Inventory data saved');
                return;
            }}
            
            // Existing drag from inventory containers (itemId and sourceContainer already declared above)
            if (!itemId || !sourceContainer) return;
            
            // Parse item info from itemId (reuse the itemId variable declared above)
            const parts = itemId.split('_');
            if (parts.length < 3) return;
            
            const containerType = parts[0] + '_' + parts[1];
            const itemIndex = parseInt(parts[2]);
            
            let item = null;
            
            // Get item from source
            if (sourceContainer === 'bagOfHolding') {
                item = inventoryData.bagOfHolding[itemIndex];
                if (item) {
                    inventoryData.bagOfHolding.splice(itemIndex, 1);
                }
            } else if (sourceContainer.startsWith('player_')) {
                const playerIndex = parseInt(sourceContainer.split('_')[1]);
                if (inventoryData.players[playerIndex]) {
                    item = inventoryData.players[playerIndex].items[itemIndex];
                    if (item) {
                        inventoryData.players[playerIndex].items.splice(itemIndex, 1);
                    }
                }
            }
            
            if (!item) return;
            
            // Add to target
            if (targetContainer === 'bagOfHolding') {
                inventoryData.bagOfHolding.push(item);
                updateBagWeight();
            } else if (targetContainer.startsWith('player_')) {
                const playerIndex = parseInt(targetContainer.split('_')[1]);
                if (inventoryData.players[playerIndex]) {
                    inventoryData.players[playerIndex].items.push(item);
                    renderPlayers();
                }
            }
            
            saveInventoryData();
        }
    </script>
</body>
</html>"""
        
        # Replace the placeholder with actual items JavaScript
        html = html.replace('{dnd_items_js}', dnd_items_js)
        
        # Fix double braces in JavaScript code (f-string escaping issue)
        # Only replace {{ with { and }} with } in function code, NOT in JSON data
        import re
        
        # Strategy: Process line by line, skipping JSON data lines
        lines = html.split('\n')
        json_vars = ['npcData', 'factionColors', 'relationshipTypes', 'factionsList', 'dndItems']
        fixed_lines = []
        
        for line in lines:
            # Check if this line contains a JSON data assignment
            is_json_line = any(f'const {var} =' in line for var in json_vars)
            
            if is_json_line:
                # Don't modify JSON data lines - they should already have correct braces from json.dumps()
                fixed_lines.append(line)
            else:
                # Convert ${{...}} to ${...} (JavaScript template literals)
                # These are Python f-string escaped braces that should become single braces in JS
                # Need to handle nested cases, so process recursively
                def convert_template_literals(text):
                    result = text
                    # Keep processing until no more ${{...}} patterns are found
                    max_iterations = 100  # Safety limit
                    iteration = 0
                    while iteration < max_iterations:
                        iteration += 1
                        changed = False
                        i = 0
                        while i < len(result):
                            if result[i:i+3] == '${{':
                                # Find the matching }}
                                start = i
                                brace_depth = 1  # We're already inside one {{
                                j = i + 3
                                while j < len(result) and brace_depth > 0:
                                    if result[j:j+2] == '{{':
                                        brace_depth += 1
                                        j += 1
                                    elif result[j:j+2] == '}}':
                                        brace_depth -= 1
                                        if brace_depth == 0:
                                            # Found matching }}, convert ${{...}} to ${...}
                                            end = j + 2
                                            # Extract the content between the braces
                                            content = result[start+3:end-2]  # Skip ${{ and }}
                                            # Replace ${{...}} with ${...}
                                            result = result[:start] + '${' + content + '}' + result[end:]
                                            i = start + len('${' + content + '}')
                                            changed = True
                                            break
                                        j += 1
                                    else:
                                        j += 1
                                else:
                                    # No matching }}, skip this ${
                                    i += 1
                            else:
                                i += 1
                        if not changed:
                            break
                    return result
                
                # Convert ${{...}} to ${...} first (process multiple times for nested cases)
                line = convert_template_literals(line)
                
                # Now fix remaining double braces (but not in ${...} which we just created)
                # Protect ${...} patterns temporarily
                js_template_protected = {}
                js_template_counter = [0]
                
                def protect_js_template(m):
                    placeholder = f'__JS_TEMPLATE_{js_template_counter[0]}__'
                    js_template_counter[0] += 1
                    js_template_protected[placeholder] = m.group(0)
                    return placeholder
                
                # Protect ${...} patterns
                line = re.sub(r'\$\{[^}]*\}', protect_js_template, line)
                
                # Fix double braces
                line = line.replace('{{', '{').replace('}}', '}')
                
                # Restore ${...} patterns
                for placeholder, original in js_template_protected.items():
                    line = line.replace(placeholder, original)
                
                fixed_lines.append(line)
        
        html = '\n'.join(fixed_lines)
        
        # Replace SVG placeholder with actual content
        html = html.replace('PLACEHOLDER_SVG_CONTENT', svg_js_content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"HTML viewer saved to {output_file}")


def main():
    script_dir = Path(__file__).parent
    # Look for npc_relationships.json in the script directory first (mindmap_viewer folder)
    json_file = script_dir / "npc_relationships.json"
    if not json_file.exists():
        # Fallback to parent directory (NPCs folder) for backward compatibility
        json_file = script_dir.parent / "npc_relationships.json"
    
    mapper = NPCRelationshipMapper(str(json_file))
    
    # Generate text-based map
    mapper.export_to_markdown()
    
    # Generate HTML viewer for players
    html_output = script_dir / "npc_mindmap_viewer.html"
    mapper.generate_html_viewer(str(html_output))
    
    # Generate visual map if possible
    if HAS_VISUALIZATION:
        visual_output = script_dir / "npc_mindmap.png"
        mapper.generate_visual_map(str(visual_output))
    else:
        print("\nTo generate a visual mind map, install dependencies:")
        print("  pip install networkx matplotlib")
    
    print("\nTo edit relationships, edit npc_relationships.json")
    print("Then run this script again to regenerate the mind map.")
    print("\nShare npc_mindmap_viewer.html with your players!")


if __name__ == "__main__":
    main()

