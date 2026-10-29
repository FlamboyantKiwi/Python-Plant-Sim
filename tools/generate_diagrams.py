import subprocess
from pathlib import Path

from base_generator import BaseScriptGenerator, Log
from diagram_generator import DiagramBuilder
from project_environment import ProjectEnv


class DiagramGenerator(BaseScriptGenerator):
    """Orchestrates Pyreverse execution and coordinates file writing for architecture diagrams."""
    
    def __init__(self, target_paths: list[str] | None = None) -> None:
        super().__init__("diagrams/packages_clean.md")
        self.target_paths = target_paths or ["."]

    def run_pyreverse(self) -> bool:
        Log.divider(40, "=")
        Log.info(f"Running Pyreverse on: {', '.join(self.target_paths) if self.target_paths and self.target_paths != ['.'] else 'Entire Project'}")
        Log.divider(40, "=")
        
        ProjectEnv.DIAGRAMS_DIR.mkdir(exist_ok=True)
        cmd = ["pyreverse", "-o", "mmd", "-d", str(ProjectEnv.DIAGRAMS_DIR), str(ProjectEnv.SRC_DIR)]
        result = subprocess.run(cmd, check=False, cwd=ProjectEnv.ROOT_DIR, capture_output=True, text=True)
        
        if result.returncode != 0:
            Log.error(f"Error running pyreverse: {result.stderr}")
            return False
            
        Log.success("Raw pyreverse diagrams generated.")
        return True

    def run(self) -> None:
        if not self.run_pyreverse():
            return
            
        input_path = ProjectEnv.DIAGRAMS_DIR / "packages.mmd"
        pkg_dir = ProjectEnv.DIAGRAMS_DIR / "packages"
        pkg_dir.mkdir(exist_ok=True)
        
        if not input_path.exists():
            Log.error(f"Could not find '{input_path.name}'.")
            return
            
        content = input_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        
        builder = DiagramBuilder(self.target_paths)
        relations = builder.parse_relations(lines)
        
        # Write High-Level Overview Map
        overview_content = builder.build_overview_diagram(relations)
        self.output_path = ProjectEnv.DIAGRAMS_DIR / "packages_clean.md"
        self.write_if_changed(overview_content, Path(__file__).name, add_header=False)
        
        # Write Individual Package Focus Diagrams
        for target_pkg, sub_tree in builder.tree.items():
            if target_pkg == "__files__":
                continue
            focus_content = builder.build_focus_diagram(target_pkg, sub_tree, relations)
            out_file = pkg_dir / f"package_{target_pkg}.md"
            out_file.write_text(focus_content, encoding="utf-8")
            Log.info(f"Generated package focus diagram: package_{target_pkg}.md")
            
        self.write_timestamp_log("diagrams/last_updated.log", "Diagrams")
        Log.success(f"Overview and individual package diagrams generated successfully in '{ProjectEnv.DIAGRAMS_DIR.name}'!")

if __name__ == "__main__":
    BaseScriptGenerator.run_with_cli(
        tool_name="Diagram",
        examples="'core' or 'entities'",
        generator_callback=lambda paths: DiagramGenerator(paths).run()
    )