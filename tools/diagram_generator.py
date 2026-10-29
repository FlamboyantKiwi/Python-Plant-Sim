from base_generator import Log
from project_environment import ProjectEnv


class DiagramBuilder:
    """Processes Pyreverse output and builds structured Mermaid diagram strings."""
    
    def __init__(self, target_paths: list[str] | None = None) -> None:
        self.target_paths = target_paths or ["."]
        self.mod_to_top_pkg, self.tree = self._get_directory_tree()

    @staticmethod
    def _wrap_mermaid(lines: list[str]) -> str:
        """Wraps raw flowchart lines into standard Markdown Mermaid code fences."""
        return "```mermaid\n" + "\n".join(lines) + "\n```\n"

    def _get_directory_tree(self) -> tuple[dict[str, str], dict]:
        """Deeply maps the source directory into a nested dictionary tree structure."""
        mod_to_top_pkg = {}
        tree = {}
        
        for file_path in ProjectEnv.get_python_files("."):
            if file_path.name == "__init__.py":
                continue
                
            rel_path = file_path.relative_to(ProjectEnv.SRC_DIR)
            parts = rel_path.parent.parts
            if not parts:
                continue
                
            top_pkg = parts[0]
            curr = tree
            for p in parts:
                curr = curr.setdefault(p, {"__files__": []})
                
            mod_name = file_path.stem
            mod_to_top_pkg[mod_name] = top_pkg
            curr["__files__"].append(mod_name)
                
        return mod_to_top_pkg, tree

    def generate_subgraphs_and_links(self, tree: dict, parent_name: str | None = None, indent_level: int = 1) -> tuple[list[str], list[str]]:
        """Recursively converts the dictionary tree into nested Mermaid subgraphs and structural links."""
        lines = []
        structural_links = []
        indent = "    " * indent_level
        
        for key, value in sorted(tree.items()):
            if key == "__files__": 
                continue
                
            name = f"{key.capitalize()}"
            
            lines.append(f"{indent}subgraph {key} [{name} Package]")
            
            files = sorted(value.get("__files__", []))
            has_subdirs = any(k != "__files__" for k in value)
            
            if indent_level == 1 and files and has_subdirs:
                if len(files) > 1:
                    lines.extend([f"{indent}    subgraph {key}_files [{name} Modules]",
                                 *(f"{indent}        {f}" for f in files),
                                 f"{indent}    end"])
                    structural_links.append(f"    {key} --> {key}_files")
                else:
                    for f in files:
                        lines.append(f"{indent}    {f}")
                        structural_links.append(f"    {key} --> {f}")
            else:
                lines.extend(f"{indent}    {f}" for f in files)
                    
            sub_lines, sub_links = self.generate_subgraphs_and_links(value, key, indent_level + 1)
            lines.extend(sub_lines)
            structural_links.extend(sub_links)
            
            lines.append(f"{indent}end")
            
            if parent_name:
                structural_links.append(f"    {parent_name} --> {key}")
            elif indent_level == 1:
                structural_links.extend(f"    {key} --> {k}" for k in sorted(value) if k != "__files__")
                        
        return lines, structural_links

    @staticmethod
    def extract_mod_name(full_name: str) -> str:
        """Safely extracts the absolute module name regardless of pyreverse package dot-notation."""
        return full_name.strip(' "').split('.')[-1]

    def parse_relations(self, lines: list[str]) -> set[tuple[str, str]]:
        """Parses valid module relations from Pyreverse output."""
        relations = set()
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith(("classDiagram", "class ", "..>")) or "custom_types" in line_stripped :
                continue
                
            if "-->" in line_stripped:
                parts = line_stripped.split("-->")
                if len(parts) == 2:
                    src = self.extract_mod_name(parts[0])
                    dst = self.extract_mod_name(parts[1])
                    if src in self.mod_to_top_pkg and dst in self.mod_to_top_pkg:
                        relations.add((src, dst))
        return relations

    def build_overview_diagram(self, relations: set[tuple[str, str]]) -> str:
        """Constructs the high-level package map Mermaid content."""
        lines = ["flowchart TB", "    direction TB", ""]
        sub_lines, _ = self.generate_subgraphs_and_links(self.tree, None, 1)
        lines.extend(sub_lines)
        
        pkg_relations = set()
        for src_mod, dst_mod in relations:
            src_pkg = self.mod_to_top_pkg.get(src_mod)
            dst_pkg = self.mod_to_top_pkg.get(dst_mod)
            if src_pkg and dst_pkg and src_pkg != dst_pkg:
                pkg_relations.add(f"    {src_pkg} --> {dst_pkg}")
                
        lines.extend(["", "    %% Package Dependency Links", *sorted(pkg_relations)])
        lines.extend(f"    {src} --> {dst}" for src, dst in sorted(relations))
        return self._wrap_mermaid(lines)

    def build_focus_diagram(self, target_pkg: str, sub_tree: dict, relations: set[tuple[str, str]]) -> str:
        """Constructs an individual package focus diagram Mermaid content."""
        lines = ["flowchart TB", "    direction TB", ""]
        external_mods = set()
        pkg_rels = set()
        
        for src, dst in relations:
            src_pkg = self.mod_to_top_pkg.get(src)
            dst_pkg = self.mod_to_top_pkg.get(dst)
            
            if src_pkg == target_pkg or dst_pkg == target_pkg:
                pkg_rels.add(f"    {src} --> {dst}")
                if src_pkg == target_pkg and dst_pkg != target_pkg:
                    external_mods.add(dst)
                elif dst_pkg == target_pkg and src_pkg != target_pkg:
                    external_mods.add(src)
                    
        sub_lines, sub_links = self.generate_subgraphs_and_links({target_pkg: sub_tree}, None, 1)
        lines.extend(sub_lines)
        
        external_by_pkg = {}
        for m in external_mods:
            external_by_pkg.setdefault(self.mod_to_top_pkg.get(m, "other"), []).append(m)
            
        for ext_pkg, mods in external_by_pkg.items():
            lines.extend([f"    subgraph {ext_pkg} [{ext_pkg.capitalize()} Package]", 
                          *(f"        {m}" for m in sorted(mods)), 
                          "    end"])
            
        lines.extend(["", 
                      "    %% Structural & Dependency Links", 
                      *sorted(sub_links), 
                      *sorted(pkg_rels)])
        return self._wrap_mermaid(lines)