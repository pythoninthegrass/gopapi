import os
import sys
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
src_dir = project_root / 'src'
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))
