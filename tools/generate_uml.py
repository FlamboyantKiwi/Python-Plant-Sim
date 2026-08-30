import ast
from pathlib import Path
from typing import Any

from project_environment import ProjectEnv

from src.utils import Log

IGNORE_TYPES: set[str] = {
    'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple', 'bytes', 'type',
    'Any', 'None', 'Optional', 'Union', 'Callable', 'Sequence', 'Iterable', 'Mapping',
    'TypeVar', 'Generic', 'Type', "Enum",
}

# AST HELPER FUNCTIONS
def extract_type_names(node: ast.AST | None) -> set[str]:
    """Recursively extracts string names of types from an AST annotation node."""
    names: set[str] = set()
    if isinstance(node, ast.Name):
        names.add(node.id)
    elif isinstance(node, ast.Subscript):
        names.update(extract_type_names(node.value))
        names.update(extract_type_names(node.slice))
    elif isinstance(node, ast.BinOp):
        names.update(extract_type_names(node.left))
        names.update(extract_type_names(node.right))
    elif isinstance(node, ast.Tuple):
        for elt in node.elts:
            names.update(extract_type_names(elt))
    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
        names.add(node.value.strip("'\""))
    return names


class UMLVisitor(ast.NodeVisitor):
    """Visits the AST to extract class names, attributes, methods, and relationships."""
    
    def __init__(self) -> None:
        self.classes: dict[str, dict[str, Any]] = {}
        self.relationships: list[tuple[str, str]] = []
        self.compositions: set[tuple[str, str]] = set()
        self.dependencies: set[tuple[str, str]] = set() 
        self.aliases: dict[str, str] = {}

    @staticmethod
    def is_custom_class(name: str | None) -> bool:
        """Filters out built-in types and checks if it looks like a class (CamelCase)."""
        if not name or name in IGNORE_TYPES:
            return False
        return name[0].isupper()


    def _extract_from_assignment(self, node: ast.Assign | ast.AnnAssign, attributes: set[str], class_name: str, is_class_level: bool = False) -> None:
        """Extracts variables and type relationships from an assignment."""
        targets: list[ast.expr] = node.targets if isinstance(node, ast.Assign) else [node.target]
        
        # Extract Relationships via type hints
        if isinstance(node, ast.AnnAssign) and node.annotation:
            for t_name in extract_type_names(node.annotation):
                if self.is_custom_class(t_name) and t_name != class_name:
                    # Route Enums/IDs to dependency, everything else to composition
                    if t_name.endswith(('ID', 'Enum')):
                        self.dependencies.add((class_name, t_name))
                    else:
                        self.compositions.add((class_name, t_name))

        #Extract Relationships via direct instantiation (Right side)
        if getattr(node, 'value', None) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            t_name = node.value.func.id
            if self.is_custom_class(t_name) and t_name != class_name:
                self.compositions.add((class_name, t_name))
        
        # Grab the attribute name
        for target in targets:
            # Catch class-level constants (e.g., MAP_HEIGHT = 10)
            if is_class_level and isinstance(target, ast.Name):
                attributes.add(target.id)
            # Catch instance variables (e.g., self.tile_grid = [])
            elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                attributes.add(target.attr)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_name: str = node.name
        methods: list[str] = []
        attributes: set[str] = set()
        is_abstract: bool = False

        for item in node.body:
            # Catch Class-Level Assignments
            if isinstance(item, (ast.Assign, ast.AnnAssign)):
                self._extract_from_assignment(item, attributes, class_name, is_class_level=True)
            
            # Catch Methods & Instance-Level Assignments
            elif isinstance(item, ast.FunctionDef):
                # Extract arguments dynamically
                methods.append(f"{item.name}()")
                
                """# Catch Return Types
                if getattr(item, 'returns', None):
                    for t_name in extract_type_names(item.returns):
                        if self.is_custom_class(t_name) and t_name != class_name:
                            self.dependencies.add((class_name, t_name))
                """
                for sub_item in ast.walk(item):
                    if isinstance(sub_item, (ast.Assign, ast.AnnAssign)):
                        self._extract_from_assignment(sub_item, attributes, class_name, is_class_level=False)
        
        # Catch Inheritance & Abstract properties
        for base in node.bases:
            # Check for either base.id (Name) or base.attr (Attribute)
            base_name = getattr(base, 'id', getattr(base, 'attr', ''))
            if base_name in IGNORE_TYPES:
                continue  # Skip built-ins and standard library wrappers
            if base_name == 'ABC':
                is_abstract = True
            elif base_name:
                self.relationships.append((base_name, class_name))

        self.classes[class_name] = {
            'methods': sorted(methods),
            'attributes': sorted(attributes),
            'is_abstract': is_abstract
        }

        self.generic_visit(node)

class UMLCreator:
    """Manages the parsing of code and generation of Mermaid syntax."""
    def __init__(self) -> None:
        self.visitor: UMLVisitor = UMLVisitor()
        self.type_library: dict[str, dict[str, Any]] = {}
        self.alias_library: dict[str, str] = {}
        self._preload_types()

    def _preload_types(self) -> None:
        """Background parses the 'types' directory to build a lookup library."""
        try:
            type_visitor = UMLVisitor()
            # Grabs everything in src/types and custom_types.py
            py_files = ProjectEnv.get_python_files('types')
            custom_types_path = ProjectEnv.SRC_DIR / 'custom_types.py' 
            if custom_types_path.exists():
                py_files.append(custom_types_path)
                
            for file_path in py_files:
                try:
                    code = file_path.read_text(encoding='utf-8')
                    type_visitor.visit(ast.parse(code))
                except Exception:
                    pass # Skip unparseable files
            
            # Store the resulting data dictionary!
            self.type_library = type_visitor.classes
            self.alias_library = type_visitor.aliases
        except Exception:
            pass # Fail silently if the types folder doesn't exist yet

    @staticmethod
    def _get_vis(name: str) -> str:
        """Determines the UML visibility modifier based on the attribute/method name."""
        if name.startswith("__") and name.endswith("__"):
            return "+"  # Standard dunder (public)
        elif name.startswith("_"):
            return "-"  # Protected/Private
        return "+"      # Public

    def parse_code(self, source_code: str) -> None:
        """Parses a string of Python code and feeds it into the visitor."""
        tree: ast.Module = ast.parse(source_code)
        self.visitor.visit(tree)

    def generate_mermaid(self) -> str:
        """Translates the visited AST data into Mermaid string formatting."""
        mermaid_output: list[str] = ["```mermaid", "classDiagram"]
        
        referenced_classes: set[str] = set()
        
        # Write Inheritance Lines
        for parent, child in self.visitor.relationships:
            mermaid_output.append(f"    {parent} <|-- {child}")
            referenced_classes.update([parent, child])
            
        # Write Composition Lines with Dynamic Labels
        for parent, child in self.visitor.compositions:
            label = "component" if child.endswith(('Controller', 'Handler', 'Manager')) else "contains"
            mermaid_output.append(f"    {parent} *-- {child} : {label}")
            referenced_classes.update([parent, child])
        
        # Write Dependency Lines with Dynamic Labels
        for parent, child in self.visitor.dependencies:
            label = "creates" if "Factory" in parent else "uses"
            mermaid_output.append(f"    {parent} ..> {child} : {label}")
            referenced_classes.update([parent, child])
        
        # Filter and write External Classes and Aliases
        internal_classes = set(self.visitor.classes.keys()) | set(self.visitor.aliases.keys())
        external_classes = referenced_classes - internal_classes

        for ext_class in sorted(external_classes):
            if ext_class in self.type_library:
                content = self.type_library[ext_class]
                mermaid_output.extend([
                    f"    class {ext_class} {{",
                    "        <<TYPE>>"
                ])
                members = content['attributes'] + content['methods']
                mermaid_output.extend(f"        {self._get_vis(m)}{m}" for m in members)
                mermaid_output.append("    }")
                
            elif ext_class in self.alias_library:
                alias_val = self.alias_library[ext_class].replace('[', '~').replace(']', '~')
                mermaid_output.extend([
                    f"    class {ext_class} {{",
                    "        <<ALIAS>>",
                    f"        +{alias_val}",
                    "    }"
                ])
                
            else:
                mermaid_output.extend([
                    f"    class {ext_class} {{",
                    "        <<EXTERNAL>>",
                    "    }",
                ])
                
        # Write Local Aliases
        for alias_name, alias_val in self.visitor.aliases.items():
            safe_val = alias_val.replace('[', '~').replace(']', '~')
            mermaid_output.extend([
                f"    class {alias_name} {{",
                "        <<ALIAS>>",
                f"        +{safe_val}",
                "    }"
            ])
            
        # Write Parsed Classes, Attributes, and Methods
        for class_name, content in self.visitor.classes.items():
            mermaid_output.append(f"    class {class_name} {{")
            
            if content['is_abstract']:
                mermaid_output.append("        <<ABSTRACT>>")
            
            members = content['attributes'] + content['methods']
            mermaid_output.extend(f"        {self._get_vis(m)}{m}" for m in members)
                
            mermaid_output.append("    }")
        mermaid_output.append("```")
        return "\n".join(mermaid_output)
    
def run_generator(user_inputs: list[str]) -> None:
    uml_creator: UMLCreator = UMLCreator()
    all_py_files: set[Path] = set()
    try:
        # Gather Files
        for path_str in user_inputs:
            py_files = ProjectEnv.get_python_files(path_str)
            all_py_files.update(py_files)
            
        if not all_py_files:
            Log.error("No Python files found in the provided paths.")
            return
        
        # Parse Files
        for file_path in all_py_files:
            try:
                code_content = file_path.read_text(encoding='utf-8')
                uml_creator.parse_code(code_content)
            except (SyntaxError, OSError, UnicodeDecodeError) as e:
                Log.error(f"Skipping {file_path.name} due to parsing error: {e}")
       
        # Generate mermaid text
        mermaid_content: str = uml_creator.generate_mermaid()
        
        # Dynamic Naming: Join the stems of all provided paths
        stems = [Path(p).stem for p in user_inputs]
        file_stem = "_".join(stems)
        
        # Save straight to the central UML directory
        ProjectEnv.UML_DIR.mkdir(exist_ok=True)
        output_file = ProjectEnv.UML_DIR / f"{file_stem}_uml.md"
        output_file.write_text(mermaid_content, encoding='utf-8')
        
        Log.success(f"Generated UML diagram saved to: {output_file}")

    except FileNotFoundError as e:
        Log.error(str(e))
    except Exception as e: # noqa: BLE001
        Log.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    print("--- Python Plant Sim UML Generator ---")
    print("Enter a file or folder path inside 'src'")
    print("Examples: 'core/asset_loaders' or 'entities/player.py, ui/inventory'")
    
    while True:
        user_input: str = input("\n> Path (or 'q' to quit): ").strip()
        
        if user_input.lower() == 'q':
            print("Exiting generator.")
            break
        elif user_input:
            paths = [p.strip() for p in user_input.split(',') if p.strip()]
            if paths:
                run_generator(paths)
        else:
            print("No input provided.")