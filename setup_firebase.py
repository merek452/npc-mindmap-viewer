#!/usr/bin/env python3
"""
Firebase Configuration Setup Script
Run this script to configure Firebase in your generated HTML file.
"""

import re
from pathlib import Path

def setup_firebase_config():
    """Interactive script to set up Firebase configuration"""
    html_file = Path(__file__).parent / "npc_mindmap_viewer.html"
    
    if not html_file.exists():
        print(f"Error: {html_file} not found!")
        print("Please run generate_mindmap.py first to create the HTML file.")
        return
    
    print("=" * 60)
    print("Firebase Configuration Setup")
    print("=" * 60)
    print("\nTo get your Firebase config values:")
    print("1. Go to https://console.firebase.google.com")
    print("2. Select your project")
    print("3. Click the gear icon ⚙️ → Project settings")
    print("4. Scroll to 'Your apps' → Click </> (Web icon)")
    print("5. Copy the firebaseConfig values\n")
    
    config = {}
    config['apiKey'] = input("Enter apiKey: ").strip()
    config['authDomain'] = input("Enter authDomain: ").strip()
    config['databaseURL'] = input("Enter databaseURL: ").strip()
    config['projectId'] = input("Enter projectId: ").strip()
    config['storageBucket'] = input("Enter storageBucket: ").strip()
    config['messagingSenderId'] = input("Enter messagingSenderId: ").strip()
    config['appId'] = input("Enter appId: ").strip()
    
    campaign_id = input("\nEnter Campaign ID (default: 'genia'): ").strip() or "genia"
    access_code = input("Enter Access Code (optional, press Enter to skip): ").strip()
    
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace Firebase config
    firebase_config_pattern = r'const FIREBASE_CONFIG = \{.*?\};'
    firebase_config_replacement = f"""const FIREBASE_CONFIG = {{
            apiKey: "{config['apiKey']}",
            authDomain: "{config['authDomain']}",
            databaseURL: "{config['databaseURL']}",
            projectId: "{config['projectId']}",
            storageBucket: "{config['storageBucket']}",
            messagingSenderId: "{config['messagingSenderId']}",
            appId: "{config['appId']}"
        }};"""
    
    content = re.sub(firebase_config_pattern, firebase_config_replacement, content, flags=re.DOTALL)
    
    # Replace campaign ID
    content = re.sub(r"const CAMPAIGN_ID = \".*?\";", f'const CAMPAIGN_ID = "{campaign_id}";', content)
    
    # Replace access code
    if access_code:
        content = re.sub(r'const CAMPAIGN_ACCESS_CODE = ".*?";', f'const CAMPAIGN_ACCESS_CODE = "{access_code}";', content)
    
    # Write back
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # index.html is now a redirect to npc_mindmap_viewer.html; Firebase lives only in the viewer.
    # Only patch index.html if it still contains FIREBASE_CONFIG (legacy full copy).
    index_file = Path(__file__).parent / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            index_content = f.read()
        if "FIREBASE_CONFIG" in index_content:
            index_content = re.sub(firebase_config_pattern, firebase_config_replacement, index_content, flags=re.DOTALL)
            index_content = re.sub(r"const CAMPAIGN_ID = \".*?\";", f'const CAMPAIGN_ID = "{campaign_id}";', index_content)
            if access_code:
                index_content = re.sub(r'const CAMPAIGN_ACCESS_CODE = ".*?";', f'const CAMPAIGN_ACCESS_CODE = "{access_code}";', index_content)
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_content)
    
    print("\n✅ Firebase configuration updated successfully!")
    print(f"   Campaign ID: {campaign_id}")
    if access_code:
        print(f"   Access Code: {access_code}")
    print("\nNext steps:")
    print("1. Make sure Realtime Database is enabled in Firebase Console")
    print("2. Set up security rules (see FIREBASE_SETUP.md)")
    print("3. Test the app - data should now sync across all users!")

if __name__ == "__main__":
    setup_firebase_config()
