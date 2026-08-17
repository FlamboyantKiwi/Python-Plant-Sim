import os
import subprocess
import datetime

def run_pyreverse():
    print("========================================")
    print("Running Pyreverse to generate diagrams...")
    print("========================================")
    
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    diagrams_dir = os.path.join(root_dir, "diagrams")
    src_dir = os.path.join(root_dir, "src")
    
    # Ensure diagrams folder exists
    os.makedirs(diagrams_dir, exist_ok=True)
    
    # Run pyreverse targeting src, outputting to diagrams folder
    cmd = ["pyreverse", "-o", "mmd", "-d", diagrams_dir, src_dir]
    result = subprocess.run(cmd, cwd=root_dir, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running pyreverse: {result.stderr}")
        return False
    
    print("[SUCCESS] Raw pyreverse diagrams generated.")
    return True

def process_packages_mmd():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_path = os.path.join(root_dir, "diagrams", "packages.mmd")
    output_path = os.path.join(root_dir, "diagrams", "packages_clean.mmd")
    log_path = os.path.join(root_dir, "diagrams", "last_updated.log")

    if not os.path.exists(input_path):
        print(f"Error: Could not find '{input_path}'.")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()

    # Define folder subgraphs mapping
    subgraphs = {
        "core": ["core", "controls", "database", "debug_logger", "spritesheet", "ui_utils"],
        "assets": ["assets", "asset_data", "asset_loader", "base", "collections", "database", "entities", "world"],
        "states": ["states", "hud", "menus", "playing"],
        "types": ["types", "data_models", "enums", "generated_enums", "geometry"],
        "entities": ["entities", "animal", "components", "animation", "interaction", "inventoryComponent", "entity", "items", "plant", "player"],
        "groups": ["groups", "camera", "plant_group", "ui_group"],
        "ui": ["ui", "InventoryUI", "timer", "ui_elements", "ui_factory", "ui_ghosts", "wrappers"],
        "world": ["world", "level", "tile"]
    }

    # Map duplicate names to unique flowchart node IDs to prevent Mermaid conflicts
    node_aliases = {
        ("core", "database"): "database_core",
        ("assets", "database"): "database_asset",
        ("assets", "base"): "base_asset",
        ("assets", "entities"): "entities_asset",
        ("assets", "world"): "world_asset",
    }

    relations = []
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("classDiagram") or line_stripped.startswith("class "):
            continue
        
        # Filter out type checking clutter
        if "custom_types" in line_stripped or line_stripped.startswith("..>"):
            continue
            
        # Standardize arrow types to clean flowchart syntax
        line_stripped = line_stripped.replace("..>", "-->")
        relations.append(line_stripped)

    # Build structured Mermaid Flowchart output with subgraphs
    new_lines = ["flowchart TB", "    direction TB"]
    
    seen_nodes = set()
    for sg_name, members in subgraphs.items():
        new_lines.append(f"    subgraph {sg_name} [{sg_name.capitalize()} Package]")
        for m in members:
            node_id = node_aliases.get((sg_name, m), m)
            if node_id not in seen_nodes:
                if node_id != m:
                    new_lines.append(f"        {node_id}[{m}]")
                else:
                    new_lines.append(f"        {m}")
                seen_nodes.add(node_id)
        new_lines.append("    end")

    new_lines.append("")
    
    def remap_name(name):
        name = name.strip()
        for (pkg, mod), alias in node_aliases.items():
            if name == mod:
                return alias
        return name

    # Use a set safely to eliminate duplicate relations
    processed_relations = set()
    for r in relations:
        if "-->" in r:
            parts = r.split("-->")
            if len(parts) == 2:
                src = remap_name(parts[0])
                dst = remap_name(parts[1])
                processed_relations.add(f"    {src} --> {dst}")

    for r in sorted(list(processed_relations)):
        new_lines.append(r)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    # Write timestamp log
    now = datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"Diagrams last updated on: {now}\n")

    print(f"[SUCCESS] Cleaned flowchart subgraph map saved to '{output_path}'")
    print(f"Timestamp saved to '{log_path}'")

if __name__ == "__main__":
    if run_pyreverse():
        process_packages_mmd()