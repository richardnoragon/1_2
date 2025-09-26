#!/usr/bin/env python3
"""
Reset RFU configuration to test startup dialog.

This script resets the interface configuration to force the startup dialog to appear.
"""

import json
import sys
from pathlib import Path


def reset_interface_config():
    """Reset interface configuration to force startup dialog."""
    try:
        # Path to configuration file
        config_path = Path("config/rfu_config.json")
        
        if not config_path.exists():
            print("Configuration file not found - startup dialog will appear by default")
            return True
        
        # Load current configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Reset interface configuration
        if 'interface_mode' in config:
            config['interface_mode']['show_startup_dialog'] = True
            config['interface_mode']['remember_choice'] = False
            config['interface_mode']['current_mode'] = 'dialog_hub'
            print("Reset interface configuration:")
            print(f"  - show_startup_dialog: {config['interface_mode']['show_startup_dialog']}")
            print(f"  - remember_choice: {config['interface_mode']['remember_choice']}")
            print(f"  - current_mode: {config['interface_mode']['current_mode']}")
        else:
            config['interface_mode'] = {
                'show_startup_dialog': True,
                'remember_choice': False,
                'current_mode': 'dialog_hub'
            }
            print("Created new interface configuration section")
        
        # Save updated configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"Configuration updated successfully: {config_path}")
        print("Now run 'python main.py' to see the startup dialog")
        return True
        
    except Exception as e:
        print(f"Error resetting configuration: {e}")
        return False

def main():
    """Main entry point."""
    print("RFU Configuration Reset Tool")
    print("=" * 40)
    
    if reset_interface_config():
        print("\n✅ Configuration reset successfully!")
        print("The startup dialog will appear on next application launch.")
    else:
        print("\n❌ Failed to reset configuration.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())