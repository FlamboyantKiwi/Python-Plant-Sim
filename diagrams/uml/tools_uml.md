```mermaid
classDiagram
    BaseScriptGenerator <|-- DiagramGenerator
    BaseScriptGenerator <|-- EnumGenerator
    BaseScriptGenerator <|-- GhostGenerator
    NodeVisitor <|-- UMLVisitor
    BaseScriptGenerator <|-- UMLGenerator
    DiagramGenerator *-- DiagramBuilder : contains
    ProjectEnv *-- Path : contains
    UMLGenerator *-- Path : contains
    UMLGenerator *-- UMLCreator : contains
    UMLCreator *-- UMLVisitor : contains
    EnumGenerator *-- EnumDefinition : contains
    EnumGenerator *-- Path : contains
    SpriteSheetBuilder *-- SpriteRect : contains
    CropVisualData *-- SpriteRect : contains
    BaseScriptGenerator *-- Path : contains
    class NodeVisitor {
        <<EXTERNAL>>
    }
    class Path {
        <<EXTERNAL>>
    }
    class BaseScriptGenerator {
        +output_path
        -__init__()
        -_get_autogen_header()
        -_get_display_path()
        -_get_timestamp()
        -_prepare_directory()
        +generate_all()
        +inject_between_markers()
        +run_with_cli()
        +sync_init_files()
        +write_if_changed()
        +write_timestamp_log()
    }
    class DiagramBuilder {
        +target_paths
        -__init__()
        -_get_directory_tree()
        -_wrap_mermaid()
        +build_focus_diagram()
        +build_overview_diagram()
        +extract_mod_name()
        +generate_subgraphs_and_links()
        +parse_relations()
    }
    class SpriteRect {
        +h
        +w
        +x
        +y
        +extract_from()
    }
    class CropVisualData {
        +container
        +fruit
        +is_tree
        +world_art
    }
    class SpriteSheetBuilder {
        +alt_sheet
        +assets_dir
        +main_sheet
        -__init__()
        -_calculate_dimensions()
        -_draw_container()
        -_draw_fruit()
        -_draw_world_art()
        -_load_source()
        +build_group_sheet()
        +save_sheet()
    }
    class DiagramGenerator {
        +output_path
        +target_paths
        -__init__()
        +run()
        +run_pyreverse()
    }
    class EnumDefinition {
        +class_name
        +docstring
        +keys
    }
    class EnumGenerator {
        -_definitions
        +db_path
        -__init__()
        -_camel_to_screaming_snake()
        -_compile_enum_string()
        -_normalize_class_name()
        +add_asset_directories()
        +add_database_tables()
        +run()
    }
    class GhostGenerator {
        +elements
        +wrappers
        -__init__()
        +register_elements()
        +register_wrappers()
        +run()
    }
    class UMLVisitor {
        +aliases
        +classes
        +compositions
        +dependencies
        +relationships
        -__init__()
        -_extract_from_assignment()
        +is_custom_class()
        +visit_ClassDef()
    }
    class UMLCreator {
        +alias_library
        +type_library
        +visitor
        -__init__()
        -_get_vis()
        -_preload_types()
        +generate_mermaid()
        +parse_code()
    }
    class UMLGenerator {
        +uml_creator
        +user_inputs
        -__init__()
        +run()
    }
    class ProjectEnv {
        +ASSETS_DIR
        +DIAGRAMS_DIR
        +ROOT_DIR
        +SRC_DIR
        +TOOLS_DIR
        +TYPES_DIR
        +UI_DIR
        +UML_DIR
        +get_python_files()
    }
```