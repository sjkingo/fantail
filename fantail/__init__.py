__version__ = '0.1.0'

# Fix path for package imports
import sys
import os.path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
