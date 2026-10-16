#!/usr/bin/env python3
import sys

# Importing a sibling module must never write __pycache__ into the governed
# tree. A release tree that mutates itself when a tool runs cannot satisfy
# ABS.CFG.RELEASE.SOURCE_TREE_MUTATION, and the resulting .pyc trips the very
# denylist this tooling enforces.
sys.dont_write_bytecode = True

from pathlib import Path
import json,re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
bad=[]; count=0
for p in root.rglob('*'):
 if not p.is_file() or p.suffix.lower() not in ('.yml','.yaml'): continue
 txt=p.read_text(encoding='utf-8',errors='ignore'); rp=str(p.relative_to(root)).lower()
 executable_ci=rp.startswith('.github/workflows/') or any(t in p.name.lower() for t in ('workflow','ci','action','template')) or ('jobs:' in txt and re.search(r'(?m)^on\s*:',txt))
 if not executable_ci: continue
 for line in txt.splitlines():
  m=re.search(r'\buses:\s*["\']?([^\s"\']+)',line)
  if not m: continue
  count+=1; u=m.group(1)
  if u.startswith('./') or u.startswith('docker://'): continue
  if '@' not in u or not re.fullmatch(r'[0-9a-fA-F]{40}',u.rsplit('@',1)[1]): bad.append({'path':str(p.relative_to(root)),'uses':u})
print(json.dumps({'uses_count':count,'unresolved':bad,'pass':not bad},indent=2))
raise SystemExit(0 if not bad else 1)
