#!/usr/bin/env python3
"""
Launch script for Project Galileo Streamlit UI
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit UI"""

    print("🚀 Launching Project Galileo UI...")
    print("=" * 50)

    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        streamlit_app = os.path.join(script_dir, "streamlit_app.py")

        print(f"📂 App location: {streamlit_app}")
        print(f"🌐 Starting Streamlit server...")
        print(f"💡 The UI will open in your browser automatically")
        print(f"🔧 To stop the server, press Ctrl+C")
        print()

        # Launch streamlit
        subprocess.run([
            sys.executable,
            "-m", "streamlit", "run",
            streamlit_app,
            "--server.port", "8501",
            "--server.headless", "false"
        ])

    except KeyboardInterrupt:
        print("\n👋 Streamlit server stopped")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        print(f"💡 Try running manually: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()