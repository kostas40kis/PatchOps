from pathlib import Path
import ast
import sys

for arg in sys.argv[1:]:
    target = Path(arg)
    source = target.read_text(encoding="utf-8")
    ast.parse(source, filename=str(target))
    print(f"AST_OK: {target}")