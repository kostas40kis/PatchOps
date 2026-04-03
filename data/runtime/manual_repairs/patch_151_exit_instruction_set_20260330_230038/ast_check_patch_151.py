from pathlib import Path
import ast
import sys

target = Path(sys.argv[1])
source = target.read_text(encoding="utf-8")
ast.parse(source, filename=str(target))
print(f"AST_OK: {target}")