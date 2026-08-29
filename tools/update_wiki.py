import re
import sys
from pathlib import Path

from project_environment import ProjectEnv

from src.core import Log


def inject_diagrams(wiki_dir: Path):
    # Match the HTML comments and anything between them
    pattern = re.compile(r"(<!-- BEGIN_MERMAID: (.*?) -->)(.*?)(<!-- END_MERMAID -->)", re.DOTALL)
    
    # Grab the exact UML directory automatically using the environment tool
    uml_dir = ProjectEnv.UML_DIR

    def replacer(match):
        start_tag, uml_name, _, end_tag = match.groups()
        uml_path = uml_dir / f"{uml_name}.md"
        
        if uml_path.exists():
            mermaid_content = uml_path.read_text(encoding="utf-8").strip()
            Log.success(f"Injected diagram: {uml_name}.md")
            return f"{start_tag}\n```mermaid\n{mermaid_content}\n```\n{end_tag}"
            
        Log.error(f"Missing diagram asset: {uml_path.name}")
        return match.group(0)

    # Scan the Wiki directory and inject
    for filepath in wiki_dir.glob("*.md"):
        content = filepath.read_text(encoding="utf-8")
        new_content = pattern.sub(replacer, content)
        
        # Only write to disk if a change actually occurred
        if new_content != content:
            filepath.write_text(new_content, encoding="utf-8")
            Log.info(f"Successfully updated Wiki Page: {filepath.name}")

if __name__ == "__main__":
    wiki_target = Path(sys.argv[1])
    Log.divider()
    Log.info(f"Syncing diagrams to Wiki at: {wiki_target}")
    inject_diagrams(wiki_target)