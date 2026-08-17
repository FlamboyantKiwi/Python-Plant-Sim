# tools/generate_ghosts.py
import os
from base_generator import BaseScriptGenerator  # Import our shared logic!
from src.core.debug_logger import Log

class GhostGenerator(BaseScriptGenerator):
    """An extensible engine that cross-multiplies UI targets into type-safe ghost classes."""
    
    def __init__(self, output_path: str = "ui/ui_ghosts.py") -> None:
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
            "from __future__ import annotations\n"
            f"from ui.ui_elements import {', '.join(self.elements)}\n"
            f"from ui.wrappers import {', '.join(self.wrappers)}\n\n"
            "# --- Matrix Combinations ---\n" + "\n".join(matrix_classes) + "\n\n"
            "# --- Explicit Exports for Wildcard Import Support ---\n"
            f"__all__ = {str(ghost_names).replace("'", '"')}\n"
        )
        
        # Pipe directly to the base manager for analysis and execution!
        did_write = self.write_if_changed(body_buffer, os.path.basename(__file__))
        
        # Output layout recipe instructions to console only if modifications were committed
        if did_write:
            Log.divider(40, "=")
            Log.info(f"from ui.ui_ghosts import {', '.join(ghost_names)}")
            Log.divider(40, "=")
        
if __name__ == "__main__":
    # Instantiating elements, chaining wrappers, and processing the pipeline fluidly!
    (GhostGenerator(output_path="ui/ui_ghosts.py")
        .register_elements("Button", "Slot", "TextBox")
        .register_wrappers("BorderWrapper", "FlashWrapper", "ShadowWrapper")
        .run())