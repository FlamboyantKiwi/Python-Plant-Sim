import os
import subprocess
from datetime import datetime, timezone

from base_generator import ProjectEnv


def run_pyreverse():
    print("========================================")
    print("Running Pyreverse to generate diagrams...")
    print("========================================")
    
    ProjectEnv.DIAGRAMS_DIR.mkdir(exist_ok=True)
    
    cmd = ["pyreverse", "-o", "mmd", "-d", str(ProjectEnv.DIAGRAMS_DIR), str(ProjectEnv.SRC_DIR)]
    result = subprocess.run(cmd, check=False, cwd=ProjectEnv.ROOT_DIR, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running pyreverse: {result.stderr}")
        return False
    
    print("[SUCCESS] Raw pyreverse diagrams generated.")
    return True

def get_directory_tree(src_dir):
    """Deeply maps the source directory into a nested dictionary tree structure."""
    mod_to_top_pkg = {}
    tree = {}
    
    for root, dirs, files in os.walk(src_dir):
        if "__pycache__" in root:
            continue
            
        rel_path = os.path.relpath(root, src_dir).replace("\\", "/")
        if rel_path == ".":
            continue
            
        parts = rel_path.split("/")
        top_pkg = parts[0]
        
        curr = tree
        for p in parts:
            if p not in curr:
                curr[p] = {"__files__": []}
            curr = curr[p]
            
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                mod_name = file[:-3]
                mod_to_top_pkg[mod_name] = top_pkg
                curr["__files__"].append(mod_name)
                
    return mod_to_top_pkg, tree

def generate_subgraphs_and_links(tree, parent_name=None, indent_level=1):
    """Recursively converts the dictionary tree into nested Mermaid subgraphs and structural links."""
    lines = []
    structural_links = []
    indent = "    " * indent_level
    
    for key, value in sorted(tree.items()):
        if key == "__files__": 
            continue
        
        # STANDARDIZED: All directories are labeled as 'Package'
        display_name = f"{key.capitalize()} Package"
        sub_id = key
        
        lines.append(f"{indent}subgraph {sub_id} [{display_name}]")
        
        files = sorted(value.get("__files__", []))
        has_subdirs = len([k for k in value if k != "__files__"]) > 0
        
        # Format top-level packages cleanly
        if indent_level == 1 and files and has_subdirs:
            if len(files) > 1:
                # STANDARDIZED: Loose files are grouped as 'Modules'
                file_sub_id = f"{sub_id}_files"
                lines.append(f"{indent}    subgraph {file_sub_id} [{key.capitalize()} Modules]")
                for f in files:
                    lines.append(f"{indent}        {f}")
                lines.append(f"{indent}    end")
                structural_links.append(f"    {sub_id} --> {file_sub_id}")
            else:
                # If there's only one loose file (e.g. world -> level), just point to the file
                for f in files:
                    lines.append(f"{indent}    {f}")
                    structural_links.append(f"    {sub_id} --> {f}")
        else:
            for f in files:
                lines.append(f"{indent}    {f}")
                
        # Recurse for deeper subdirectories
        sub_lines, sub_links = generate_subgraphs_and_links(value, sub_id, indent_level + 1)
        lines.extend(sub_lines)
        structural_links.extend(sub_links)
        
        lines.append(f"{indent}end")
        
        # Formulate explicit structural arrows
        if parent_name:
            structural_links.append(f"    {parent_name} --> {sub_id}")
        elif indent_level == 1:
            for k in sorted(value.keys()):
                if k != "__files__":
                    structural_links.append(f"    {sub_id} --> {k}")
            
    return lines, structural_links
def extract_mod_name(full_name):
    """Safely extracts the absolute module name regardless of pyreverse package dot-notation."""
    clean = full_name.strip(' "')
    return clean.split('.')[-1]

def process_diagrams():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_path = os.path.join(root_dir, "diagrams", "packages.mmd")
    diagrams_dir = os.path.join(root_dir, "diagrams")
    pkg_dir = os.path.join(diagrams_dir, "packages")
    log_path = os.path.join(diagrams_dir, "last_updated.log")
    src_dir = os.path.join(root_dir, "src")

    os.makedirs(pkg_dir, exist_ok=True)

    if not os.path.exists(input_path):
        print(f"Error: Could not find '{input_path}'.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    mod_to_top_pkg, tree = get_directory_tree(src_dir)

    # 1. Parse all valid relations from the Pyreverse output
    relations = set()
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith(("classDiagram", "class ")):
            continue
        if "custom_types" in line_stripped or line_stripped.startswith("..>"):
            continue
            
        if "-->" in line_stripped:
            parts = line_stripped.replace("..>", "-->").split("-->")
            if len(parts) == 2:
                src_mod = extract_mod_name(parts[0])
                dst_mod = extract_mod_name(parts[1])
                if src_mod in mod_to_top_pkg and dst_mod in mod_to_top_pkg:
                    relations.add((src_mod, dst_mod))

    # --- PART A: Generate High-Level Package Map ---
    overview_lines = ["flowchart TB", "    direction TB", ""]
    sub_lines, _ = generate_subgraphs_and_links(tree, None, 1)
    overview_lines.extend(sub_lines)
    
    # Map package-to-package relations instead of file-to-file
    pkg_relations = set()
    for src_mod, dst_mod in relations:
        src_pkg = mod_to_top_pkg.get(src_mod)
        dst_pkg = mod_to_top_pkg.get(dst_mod)
        if src_pkg and dst_pkg and src_pkg != dst_pkg:
            pkg_relations.add(f"    {src_pkg} --> {dst_pkg}")

    overview_lines.append("")
    overview_lines.append("    %% Package Dependency Links")
    overview_lines.extend(sorted(pkg_relations))
     # Append cross-module dependencies
    overview_lines.extend(f"    {src} --> {dst}" for src, dst in sorted(relations))
   
    with open(os.path.join(diagrams_dir, "packages_clean.mmd"), "w", encoding="utf-8") as f:
        f.write("\n".join(overview_lines))

    # --- PART B: Generate Individual Package Focus Diagrams ---
    for target_pkg, sub_tree in tree.items():
        if target_pkg == "__files__": 
            continue
        
        focus_lines = ["flowchart TB", "    direction TB", ""]
        
        # Identify external modules/packages that interact with this focus package
        external_modules_involved = set()
        pkg_relations_filtered = set()
        
        for src_mod, dst_mod in relations:
            src_pkg = mod_to_top_pkg.get(src_mod)
            dst_pkg = mod_to_top_pkg.get(dst_mod)
            
            if (src_pkg == target_pkg or dst_pkg == target_pkg) and src_pkg != dst_pkg:  # Inter-package only for focus view external links
                pkg_relations_filtered.add(f"    {src_mod} --> {dst_mod}")
                if src_pkg == target_pkg:
                    external_modules_involved.add(dst_mod)
                else:
                    external_modules_involved.add(src_mod)

        # Draw the target package fully expanded
        target_tree = {target_pkg: sub_tree}
        t_sub_lines, t_sub_links = generate_subgraphs_and_links(target_tree, None, 1)
        focus_lines.extend(t_sub_lines)

        # Group and draw external packages containing connected modules
        external_by_pkg = {}
        for ext_mod in external_modules_involved:
            ext_pkg = mod_to_top_pkg.get(ext_mod, "other")
            if ext_pkg not in external_by_pkg:
                external_by_pkg[ext_pkg] = []
            external_by_pkg[ext_pkg].append(ext_mod)

        for ext_pkg, ext_mods in external_by_pkg.items():
            focus_lines.append(f"    subgraph {ext_pkg} [{ext_pkg.capitalize()} Package]")
            for m in sorted(ext_mods):
                focus_lines.append(f"        {m}")
            focus_lines.append("    end")

        focus_lines.append("")
        focus_lines.append("    %% Structural & Dependency Links")
        focus_lines.extend(sorted(t_sub_links))
        focus_lines.extend(sorted(pkg_relations_filtered))

        # Save individual mmd file
        out_file = os.path.join(pkg_dir, f"package_{target_pkg}.mmd")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("\n".join(focus_lines))

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d at %H:%M:%S")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"Diagrams last updated on: {now}\n")

    print(f"[SUCCESS] Overview and individual package diagrams generated successfully in '{diagrams_dir}'!")

if __name__ == "__main__":
    if run_pyreverse():
        process_diagrams()