import sqlite3
import os
import re
from dataclasses import dataclass
from base_generator import BaseScriptGenerator

@dataclass
class EnumDefinition:
    """A structured container for everything needed to build an Enum class."""
    class_name: str
    keys: list[str]
    docstring: str
    
class EnumGenerator(BaseScriptGenerator):
    """An extensible engine that collects data sources to auto-generate Python Enums."""
    
    def __init__(self, db_path: str, output_path: str) -> None:
        super().__init__(output_path)
        self.db_path = db_path
        self._definitions: list[EnumDefinition] = []

    def _camel_to_screaming_snake(self, name: str) -> str:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name.replace(" ", "_"))
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()

    def _normalize_class_name(self, raw_name: str, suffix: str) -> str:
        clean_name = raw_name.replace("_", " ").title().replace(" ", "")
        if clean_name.endswith("s") and not clean_name.endswith("ss"):
            clean_name = clean_name[:-1]
        return f"{clean_name}{suffix}"

    def add_database_tables(self, *table_names: str, suffix: str = "ID") -> "EnumGenerator":
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for table in table_names:
                    cursor.execute(f"SELECT id FROM {table}")
                    keys = [row[0] for row in cursor.fetchall()]
                    if keys:
                        self._definitions.append(EnumDefinition(
                            class_name=self._normalize_class_name(table, suffix),
                            keys=keys,
                            docstring=f"Maps directly to the '{table}' table in the database."
                        ))
        except sqlite3.OperationalError as e:
            print(f"Database Error: {e}")
        return self

    def add_asset_directories(self, *directory_paths: str, suffix: str = "Type") -> "EnumGenerator":
        for path in directory_paths:
            if not os.path.exists(path):
                continue
            names = {os.path.splitext(item)[0] for item in os.listdir(path) if not item.startswith(".")}
            if names:
                folder_name = os.path.basename(os.path.normpath(path))
                self._definitions.append(EnumDefinition(
                    class_name=self._normalize_class_name(folder_name, suffix),
                    keys=sorted(list(names)),
                    docstring=f"Maps directly to filenames inside the asset folder '{folder_name}'."
                ))
        return self

    def _compile_enum_string(self, enum_def: EnumDefinition) -> str:
        """Compiles a standalone typed Enum class slice into a string block."""
        lines = [
            f"class {enum_def.class_name}(str, Enum):",
            f'    """{enum_def.docstring}"""'
        ]
        for key in enum_def.keys:
            lines.append(f'    {self._camel_to_screaming_snake(key)} = "{key}"')
        
        lines.append("\n")
        return "\n".join(lines)

    def run(self) -> None:
        if not self._definitions:
            print("Enum generation aborted: No valid source definitions registered.")
            return

        print("Compiling game databases and asset directories...")
        
        body_buffer = "from enum import Enum\n\n"
        for definition in self._definitions:
            body_buffer += self._compile_enum_string(definition)
            
        # Safely pipes to your standard write_if_changed logic
        self.write_if_changed(body_buffer, os.path.basename(__file__))

        
if __name__ == "__main__":
    DB_PATH = os.path.join("Assets", "data", "gamedata.db")
    OUTPUT_PATH = os.path.join("core", "types", "generated_enums.py")
    
    (EnumGenerator(db_path=DB_PATH, output_path=OUTPUT_PATH)
        .add_database_tables("items", "shops")
        .add_asset_directories(
            os.path.join("Assets", "Player"),
            os.path.join("Assets", "Farm_Animals")
        )
        .run())