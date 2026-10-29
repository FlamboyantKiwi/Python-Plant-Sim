import ast
from pathlib import Path

from base_generator import BaseScriptGenerator, Log
from project_environment import ProjectEnv


def get_classes_from_dir(target_dir: Path) -> list[str]:
    """Safely parses all Python files in a directory and extracts class names."""
    class_names = []
    if not target_dir.exists():
        Log.error(f"Could not find directory: {target_dir}")
        return class_names
        
    for file_path in target_dir.rglob("*.py"):
        if file_path.name == "__init__.py":
            continue
        
        # Read the file as raw text to avoid execution side-effects
        code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_names.append(node.name)
                    
    return sorted(class_names)

class GhostGenerator(BaseScriptGenerator):
    """An extensible engine that cross-multiplies UI targets into type-safe ghost classes."""
    
    def __init__(self, output_path: Path = ProjectEnv.UI_DIR / "ui_ghosts.py") -> None:
        super().__init__(output_path)  # Initialize our shared base controller!
        self.elements: list[str] = []
        self.wrappers: list[str] = []

    def register_elements(self, *element_names: str) -> "GhostGenerator":
        for name in element_names:
            if name not in self.elements: 
                self.elements.append(name)
        return self

    def register_wrappers(self, *wrapper_names: str) -> "GhostGenerator":
        for name in wrapper_names:
            if name not in self.wrappers: 
                self.wrappers.append(name)
        return self

    def run(self) -> None:
        if not self.elements or not self.wrappers:
            Log.error("Matrix compilation aborted: Missing component assets.")
            return

        ghost_names = []
        matrix_classes = []
        
        for w in self.wrappers:
            prefix = w.replace("Wrapper", "")
            for e in self.elements:
                ghost_name = f"{prefix}{e}"
                ghost_names.append(ghost_name)
                matrix_classes.append(f"class {ghost_name}({w}, {e}): pass")
                
        ghost_names.sort()
        # Compile data into unified string buffer
        body_buffer = (
            "from __future__ import annotations\n\n"
            f"from .elements import {', '.join(self.elements)}\n"
            f"from .wrappers import {', '.join(self.wrappers)}\n\n"
            "# --- Matrix Combinations ---\n" + "\n".join(matrix_classes) + "\n\n"
            "# --- Explicit Exports for Wildcard Import Support ---\n"
            f"__all__ = {str(ghost_names).replace("'", '"')}\n"
        )
        
        # Only makes changes if content has changed 
        if self.write_if_changed(body_buffer, Path(__file__).name):
            self.sync_init_files(ghost_names, ProjectEnv.UI_DIR, "UI_GHOSTS")
        
if __name__ == "__main__":
    # Dynamically target and extract the classes using ProjectEnv
    dynamic_elements = get_classes_from_dir(ProjectEnv.UI_DIR / "elements")
    dynamic_wrappers = get_classes_from_dir(ProjectEnv.UI_DIR / "wrappers")
    
    # Feed them into the generator via the unpacking operator (*)
    (GhostGenerator()
        .register_elements(*dynamic_elements)
        .register_wrappers(*dynamic_wrappers)
        .run())