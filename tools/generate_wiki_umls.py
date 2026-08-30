from generate_uml import UMLCreator
from project_environment import ProjectEnv

from src.utils import Log

WIKI_MAPPINGS = {
    # --- World & Architecture ---
    "world_uml": ["world"],
    "asset_loaders_uml": ["core/asset_loaders"], 
    "database_database_group_uml": ["core/database.py", "core/asset_loaders/database_group.py"],
    "groups_uml": ["groups"],
    "states_uml": ["core/states"],

    # --- UI System ---
    "elements_uml": ["ui/elements"],
    "wrappers_uml": ["ui/wrappers"],
    "ui_factory_uml": ["ui/ui_factory.py"],
    "elements_ui_factory_uml": ["ui/elements", "ui/ui_factory.py"],
    "inventory_uml": ["ui/inventory"], 

    # --- Entities, Player & Items ---
    "nature_base_uml": ["entities/nature", "entities/base"], 
    "player_components_inventory_base_uml": ["entities/player.py", "entities/components", "entities/inventory", "entities/base"],
    "items_uml": ["entities/items"],

    # --- Types & Data Models ---
    "data_models_uml": ["types/data_models.py"],
    "enums_uml": ["types/enums.py"],
    "generated_enums_uml": ["types/generated_enums.py"],
    "geometry_uml": ["types/geometry.py"],

    # --- Tooling ---
    "tools_uml": ["../tools/"]
}

def build_wiki_umls() -> None:
    """Automates the generation of mapped UML diagrams for Wiki injection."""
    ProjectEnv.UML_DIR.mkdir(exist_ok=True)
    
    for target_name, paths in WIKI_MAPPINGS.items():
        creator = UMLCreator()
        valid = True
        
        for path_str in paths:
            try:
                for file_path in ProjectEnv.get_python_files(path_str):
                    try:
                        creator.parse_code(file_path.read_text(encoding='utf-8'))
                    except (SyntaxError, UnicodeDecodeError) as e:
                        Log.error(f"Skipping '{file_path.name}' due to parsing error: {e}")
                        valid = False
            except FileNotFoundError as e:
                Log.error(str(e))
                valid = False
                
        if not valid:
            Log.error(f"Failed to build '{target_name}.md' due to previous errors.\n")
            continue
            
        mermaid_content = creator.generate_mermaid()
        out_file = ProjectEnv.UML_DIR / f"{target_name}.md"
        
        # SMART CACHING CHECK
        if out_file.exists() and out_file.read_text(encoding='utf-8') == mermaid_content:
            Log.info(f"No adjustments detected for '{out_file.name}'. Skipping file write.")
        else:
            out_file.write_text(mermaid_content, encoding='utf-8')
            Log.success(f"Baked updates to '{out_file.name}'.")
            
if __name__ == "__main__":
    build_wiki_umls()