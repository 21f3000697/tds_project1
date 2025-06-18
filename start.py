#!/usr/bin/env python3
"""
Startup script for TDS Virtual TA API
Automatically chooses between lightweight and full versions based on available memory
"""

import psutil
import os
import sys

def get_available_memory():
    """Get available system memory in MB"""
    memory = psutil.virtual_memory()
    return memory.available / 1024 / 1024

def main():
    """Main startup function"""
    print("🚀 Starting TDS Virtual TA API...")
    
    # Check available memory
    available_memory = get_available_memory()
    print(f"📊 Available memory: {available_memory:.1f} MB")
    
    # Choose version based on available memory
    if available_memory < 600:  # Less than 600MB available
        print("💡 Using lightweight version (memory-efficient)")
        print("📝 Starting with main_lightweight.py...")
        
        # Import and run lightweight version
        try:
            from main_lightweight import app
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except ImportError as e:
            print(f"❌ Error importing lightweight version: {e}")
            print("💡 Try running: python main_lightweight.py")
            sys.exit(1)
    else:
        print("🚀 Using full version (semantic search)")
        print("📝 Starting with main.py...")
        
        # Import and run full version
        try:
            from main import app
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except ImportError as e:
            print(f"❌ Error importing full version: {e}")
            print("💡 Try running: python main.py")
            sys.exit(1)

if __name__ == "__main__":
    main() 