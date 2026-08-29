import ast
from pathlib import Path

from project_environment import ProjectEnv

from src.core import Log

IGNORE_TYPES: set[str] = {
    'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple', 'bytes', 'type',
    'Any', 'None', 'Optional', 'Union', 'Callable', 'Sequence', 'Iterable', 'Mapping',
    'TypeVar', 'Generic', 'Type'
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

def is_custom_class(name: str | None) -> bool:
    """Filters out built-in types and checks if it looks like a class (CamelCase)."""
    if not name or name in IGNORE_TYPES:
        return False
    return name[0].isupper()

class UMLVisitor(ast.NodeVisitor):
    """Visits the AST to extract class names, attributes, methods, and relationships."""
    
    def __init__(self) -> None:
        self.classes: dict[str, dict[str, list[str]]] = {}
        self.relationships: list[tuple[str, str]] = []
        self.compositions: set[tuple[str, str]] = set()

    def _extract_from_assignment(self, node: ast.Assign | ast.AnnAssign, attributes: set[str], class_name: str) -> None:
        """Extracts variables and type compositions from an assignment."""
        targets: list[ast.expr] = node.targets if isinstance(node, ast.Assign) else [node.target]
       
        # Extract "Contains" Relationships via type hints
        if isinstance(node, ast.AnnAssign) and node.annotation:
            for t_name in extract_type_names(node.annotation):
                if is_custom_class(t_name) and t_name != class_name:
                    self.compositions.add((class_name, t_name))

        # Grab the attribute name
        for target in targets:
            if isinstance(target, ast.Name):
                attributes.add(target.id)
            elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                attributes.add(target.attr)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_name: str = node.name
        methods: list[str] = []
        attributes: set[str] = set()

        for item in node.body:
            # Catch Class-Level Assignments
            if isinstance(item, (ast.Assign, ast.AnnAssign)):
                self._extract_from_assignment(item, attributes, class_name)
            
            # Catch Methods & Instance-Level Assignments
            elif isinstance(item, ast.FunctionDef):
                methods.append(item.name)
                
                for sub_item in ast.walk(item):
                    if isinstance(sub_item, (ast.Assign, ast.AnnAssign)):
                        self._extract_from_assignment(sub_item, attributes, class_name)
        
        self.classes[class_name] = {
            'methods': sorted(methods),
            'attributes': sorted(attributes)
        }

        # Catch Inheritance
        for base in node.bases:
            if isinstance(base, ast.Name):
                self.relationships.append((base.id, class_name))
            elif isinstance(base, ast.Attribute):
                self.relationships.append((base.attr, class_name))

        self.generic_visit(node)

class UMLCreator:
    """Manages the parsing of code and generation of Mermaid syntax."""
    def __init__(self) -> None:
        self.visitor: UMLVisitor = UMLVisitor()

    def parse_code(self, source_code: str) -> None:
        """Parses a string of Python code and feeds it into the visitor."""
        tree: ast.Module = ast.parse(source_code)
        self.visitor.visit(tree)

    def generate_mermaid(self) -> str:
        """Translates the visited AST data into Mermaid string formatting."""
        mermaid_output: list[str] = ["classDiagram"]
        
        # Write Inheritance Lines
        for parent, child in self.visitor.relationships:
            mermaid_output.append(f"    {parent} <|-- {child}")
            
        # Write Composition Lines
        for parent, child in self.visitor.compositions:
            mermaid_output.append(f"    {parent} *-- {child} : contains")
            
        # Write Classes, Attributes, and Methods
        for class_name, content in self.visitor.classes.items():
            mermaid_output.append(f"    class {class_name} {{")
            for attr_name in content['attributes']:
                mermaid_output.append(f"        +{attr_name}")
            for method_name in content['methods']:
                mermaid_output.append(f"        +{method_name}()")
            mermaid_output.append("    }")
        
        mermaid_output.append("```")
        return "\n".join(mermaid_output)

def run_generator(user_input: str) -> None:
    uml_creator: UMLCreator = UMLCreator()

    try:
        # Gather Files
        py_files = ProjectEnv.get_python_files(user_input)
        
        # Parse Files
        for file_path in py_files:
            try:
                code_content = file_path.read_text(encoding='utf-8')
                uml_creator.parse_code(code_content)
            except (SyntaxError, OSError, UnicodeDecodeError) as e:
                Log.error(f"Skipping {file_path.name} due to parsing error: {e}")
       
        # Generate mermaid text
        mermaid_content: str = uml_creator.generate_mermaid()
        
        # Save straight to the central UML directory
        ProjectEnv.UML_DIR.mkdir(exist_ok=True)
        output_file = ProjectEnv.UML_DIR / f"{Path(user_input).stem}_uml.md"
        output_file.write_text(mermaid_content, encoding='utf-8')
        
        Log.success(f"Generated UML diagram saved to: {output_file}")

    except FileNotFoundError as e:
        Log.error(str(e))
    except Exception as e: # noqa: BLE001
        Log.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    print("--- Python Plant Sim UML Generator ---")
    print("Enter a file or folder path inside 'src'")
    print("Examples: 'core/asset_loaders' or 'entities/player.py'")
    
    while True:
        user_input: str = input("\n> Path (or 'q' to quit): ").strip()
        
        if user_input.lower() == 'q':
            print("Exiting generator.")
            break
        elif user_input:
            run_generator(user_input)
        else:
            print("No input provided.")