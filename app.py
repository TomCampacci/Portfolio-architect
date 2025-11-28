#Welcome ! This is my portfolio application 
"""
Portfolio Analysis Application
Entry point for the graphical user interface.

Usage:
    python app.py
"""

import sys
import os

# Add current directory to path to enable imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and launch NEW two-page architecture v4
from ui.menu_principal_v4 import main

if __name__ == "__main__":
    main()
    


