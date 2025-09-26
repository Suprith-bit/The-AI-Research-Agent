#!/usr/bin/env python3
"""
Launch script for Project Galileo Beautiful UI v2
"""

import subprocess
import sys
import os

def main():
    """Launch the beautiful Streamlit UI"""

    print("🚀 Launching Project Galileo Beautiful UI...")
    print("=" * 60)
    print("✨ Features:")
    print("   • Sleek black theme inspired by premium AI interfaces")
    print("   • Smart time-based greeting system")
    print("   • Glowing AI orb with animations")
    print("   • Beautiful progress indicators")
    print("   • Elegant chat interface for follow-ups")
    print("   • Seamless MD + JSON downloads")
    print("=" * 60)

    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        streamlit_app = os.path.join(script_dir, "streamlit_app_v2.py")

        print(f"📂 App location: {streamlit_app}")
        print(f"🌐 Starting beautiful UI server...")
        print(f"💡 The UI will open in your browser automatically")
        print(f"🔧 To stop the server, press Ctrl+C")
        print()

        # Launch streamlit
        subprocess.run([
            sys.executable,
            "-m", "streamlit", "run",
            streamlit_app,
            "--server.port", "8502",  # Different port to avoid conflicts
            "--server.headless", "false",
            "--theme.base", "dark"
        ])

    except KeyboardInterrupt:
        print("\n👋 Beautiful UI server stopped")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        print(f"💡 Try running manually: streamlit run streamlit_app_v2.py")

if __name__ == "__main__":
    main()