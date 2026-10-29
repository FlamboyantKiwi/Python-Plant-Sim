import sys
from pathlib import Path

# Automatically resolve root and add to sys.path on import
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

class ProjectEnv:
    """Single source of truth for project directories and file hunting."""
    # Anchors the paths relative to this exact file, preventing execution-location bugs
    TOOLS_DIR: Path = Path(__file__).resolve().parent
    ROOT_DIR: Path = TOOLS_DIR.parent
    # ROOT DIRECTORIES
    SRC_DIR: Path = ROOT_DIR / "src"
    ASSETS_DIR: Path = ROOT_DIR / "assets"
    DIAGRAMS_DIR: Path = ROOT_DIR / "diagrams"
    UML_DIR: Path = DIAGRAMS_DIR / "uml"
    # SRC DIRECTORIES
    UI_DIR: Path = SRC_DIR / "ui"
    TYPES_DIR: Path = SRC_DIR / "types"

    @classmethod
    def get_python_files(cls, target_rel_path: str | Path) -> list[Path]:
        """Validates a target path inside 'src' and returns a list of Python files."""
        target_path = cls.SRC_DIR / target_rel_path
        
        if not target_path.exists():
            raise FileNotFoundError(f"Could not find target at {target_path}")

        if target_path.is_file() and target_path.suffix == '.py':
            return [target_path]
        elif target_path.is_dir():
            files = list(target_path.rglob("*.py"))
            if not files:
                raise FileNotFoundError(f"No Python files found in {target_path}")
            return files
        return []