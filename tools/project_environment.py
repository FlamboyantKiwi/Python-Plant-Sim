from pathlib import Path


class ProjectEnv:
    """Single source of truth for project directories and file hunting."""
    # Anchors the paths relative to this exact file, preventing execution-location bugs
    TOOLS_DIR: Path = Path(__file__).resolve().parent
    ROOT_DIR: Path = TOOLS_DIR.parent
    SRC_DIR: Path = ROOT_DIR / "src"
    ASSETS_DIR: Path = ROOT_DIR / "assets"
    UML_DIR: Path = ROOT_DIR / "uml"
    DIAGRAMS_DIR: Path = ROOT_DIR / "diagrams"

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