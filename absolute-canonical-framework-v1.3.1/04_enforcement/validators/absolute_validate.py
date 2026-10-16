#!/usr/bin/env python3
"""Deterministic structural and semantic validator for Absolute Framework projects."""
from __future__ import annotations
import sys

# Importing a sibling module must never write __pycache__ into the governed
# tree. A release tree that mutates itself when a tool runs cannot satisfy
# ABS.CFG.RELEASE.SOURCE_TREE_MUTATION, and the resulting .pyc trips the very
# denylist this tooling enforces.
sys.dont_write_bytecode = True

import argparse, json, re, sys
from pathlib import Path, PurePosixPath
from typing import Any
try:
    import yaml
    import jsonschema
except Exception as exc:
    raise SystemExit("Install dependencies from requirements-validation.txt") from exc

# The module denominator is asserted, not counted, so that a package silently
# disappearing from the tree is a validation failure rather than a smaller
# number nobody notices. Update it deliberately when a module is added.
EXPECTED_MODULE_COUNT=33

GATE_STATES={"PASS","FAIL","BLOCKED","NOT_RUN","INCONCLUSIVE","STALE","INVALID_REPORT","WAIVED_WITH_APPROVED_EXPIRY"}
DENY_NAMES={".DS_Store","Thumbs.db","__pycache__",".pytest_cache","node_modules",".venv","venv"}
SECRET_PATTERNS=[
    ("private_key",re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("seed_phrase",re.compile(r"(?i)\b(?:seed phrase|mnemonic)\s*[:=]\s*\S+")),
    ("credential",re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}")),
]

def load(path:Path)->Any:
    text=path.read_text(encoding="utf-8")
    if path.suffix.lower()==".json": return json.loads(text)
    if path.suffix.lower() in {".yaml",".yml"}: return yaml.safe_load(text)
    raise ValueError(path)

def validate(instance:Path,schema:Path)->list[str]:
    try:
        v=jsonschema.Draft202012Validator(load(schema),format_checker=jsonschema.FormatChecker())
        return [f"{instance}: {e.message}" for e in sorted(v.iter_errors(load(instance)),key=lambda x:list(x.path))]
    except Exception as exc: return [f"{instance}: validation exception: {exc}"]

def packages(root:Path):
    for p in sorted(root.rglob("MODULE_MANIFEST.yaml")): yield p.parent,load(p)

def check_modules(root:Path)->list[str]:
    errors=[]; mids=set(); known_ifaces=set()
    idx=load(root/"docs/registries/INTERFACE_INDEX.json")
    known_ifaces={x["interface_id"] for x in idx["interfaces"]}
    for base,m in packages(root):
        mids.add(m.get("module_id"))
        errors+=validate(base/"MODULE_MANIFEST.yaml",root/"04_enforcement/schemas/module_manifest.schema.json")
        for rel in m.get("canonical_paths",{}).values():
            if not (base/rel).exists(): errors.append(f"{base}: missing {rel}")
        req=load(base/"requirements.json"); reqids={x["requirement_id"] for x in req.get("requirements",[])}
        if reqids!=set(m.get("requirements",[])): errors.append(f"{base}: manifest/requirements mismatch")
        pol=load(base/"machine/policy.json")
        errors+=validate(base/"machine/policy.json",root/"04_enforcement/schemas/module_policy.schema.json")
        if {x.get("requirement_id") for x in pol.get("rules",[])}!=reqids: errors.append(f"{base}: policy traceability mismatch")
        errors+=validate(base/"blueprint/visual_manifest.json",root/"04_enforcement/schemas/visual_spec.schema.json")
        contract=base/"machine/contract.schema.json"
        errors+=validate(base/"tests/positive/valid_instance.json",contract)
        if not validate(base/"tests/negative/missing_evidence.json",contract): errors.append(f"{base}: negative fixture passed")
        if not validate(base/"tests/adversarial/authority_override.json",contract): errors.append(f"{base}: adversarial fixture passed")
        text=(base/"MODULE.md").read_text(encoding="utf-8")+(base/"tests/TEST_PLAN.md").read_text(encoding="utf-8")
        for rid in reqids:
            if text.count(rid)<2: errors.append(f"{base}: weak traceability for {rid}")
        refs=set(m.get("provided_interfaces",[]))|set(m.get("consumed_interfaces",[]))
        if refs-known_ifaces: errors.append(f"{base}: unknown interfaces {sorted(refs-known_ifaces)}")
        if m.get("status")=="CERTIFIED":
            v=m.get("verification",{})
            if not v.get("candidate_hash") or not v.get("evidence_ids") or v.get("independent_status") not in {"CERTIFIED","CERTIFIED_WITH_ACCEPTED_RISK"}:
                errors.append(f"{base}: false CERTIFIED state")
    if len(mids)!=EXPECTED_MODULE_COUNT: errors.append(f"expected {EXPECTED_MODULE_COUNT} module identities; found {len(mids)}")
    return errors

def check_profiles_adapters(root:Path)->list[str]:
    errors=[]; mids={m.get("module_id") for _,m in packages(root)}
    for p in sorted((root/"06_project_profiles").glob("*/profile.json")):
        errors+=validate(p,root/"04_enforcement/schemas/profile.schema.json")
        x=load(p); unknown=(set(x.get("required_modules",[]))|set(x.get("optional_modules",[])))-mids
        if unknown: errors.append(f"{p}: unknown modules {sorted(unknown)}")
    for p in sorted((root/"05_platform_adapters").glob("*/adapter.json")):
        errors+=validate(p,root/"04_enforcement/schemas/adapter.schema.json")
    return errors

def check_examples(root:Path)->list[str]:
    errors=[]; s=root/"04_enforcement/schemas"
    mapping={"project_state.json":"project_state.schema.json","work_packet.json":"work_packet.schema.json","evidence_record.json":"evidence_record.schema.json","gate_report.json":"gate_report.schema.json","capability_record.json":"capability_record.schema.json","session_checkpoint.json":"session_checkpoint.schema.json","publication_claim.json":"publication_claim.schema.json"}
    for i,sc in mapping.items(): errors+=validate(root/"08_examples"/i,s/sc)
    g=load(root/"08_examples/gate_report.json")
    if g.get("decision") not in GATE_STATES: errors.append("example gate state invalid")
    if g.get("decision")=="PASS" and not g.get("evidence_ids"): errors.append("PASS without evidence")
    if g.get("decision")=="PASS" and any(g.get("counts",{}).get(k,0)>0 for k in ["fail","blocked","not_run","inconclusive","stale"]): errors.append("PASS with non-pass counts")
    c=load(root/"08_examples/capability_record.json")
    if c.get("activation_state")=="ENABLED" and (c.get("health",{}).get("state") not in {"HEALTHY","DEGRADED"} or not c.get("health",{}).get("checked_at")): errors.append("enabled capability lacks current health")
    pc=load(root/"08_examples/publication_claim.json")
    if "PUBLIC" in pc.get("allowed_audiences",[]) and pc.get("classification") in {"CONFIDENTIAL","RESTRICTED"}: errors.append("restricted public claim")
    # prove negative semantic controls
    ng=load(root/"09_tests_evals/fixtures/false_pass_no_evidence.json")
    if not (ng.get("decision")=="PASS" and not ng.get("evidence_ids")): errors.append("false-PASS fixture malformed")
    nc=load(root/"09_tests_evals/fixtures/enabled_unknown_health.json")
    if not (nc.get("activation_state")=="ENABLED" and nc.get("health",{}).get("state")=="UNKNOWN"): errors.append("capability negative fixture malformed")
    np=load(root/"09_tests_evals/fixtures/restricted_public_claim.json")
    if not ("PUBLIC" in np.get("allowed_audiences",[]) and np.get("classification")=="RESTRICTED"): errors.append("publication negative fixture malformed")
    return errors

def check_hygiene(root:Path)->list[str]:
    errors=[]
    for p in sorted(root.rglob("*")):
        if p.is_symlink(): errors.append(f"symlink forbidden: {p}"); continue
        if any(x in DENY_NAMES for x in p.parts): errors.append(f"denylisted path: {p}")
        if not p.is_file(): continue
        rel=p.relative_to(root).as_posix(); pp=PurePosixPath(rel)
        if pp.is_absolute() or ".." in pp.parts: errors.append(f"unsafe path: {rel}")
        if p.suffix.lower() in {".zip",".tar",".gz",".7z",".pyc",".pyo"}: errors.append(f"nested/binary build artifact: {rel}")
        if p.stat().st_size<5_000_000 and p.suffix.lower() not in {".svg",".png",".jpg",".jpeg",".pdf"}:
            try: text=p.read_text(encoding="utf-8")
            except UnicodeDecodeError: continue
            for name,pat in SECRET_PATTERNS:
                if pat.search(text): errors.append(f"possible {name}: {rel}")
    return errors

_ARCHIVE_GENERATION=re.compile(r"^v\d+$")
def _link_base(root:Path,p:Path)->Path:
    # A document generation archived by the documentation engine lives at
    # docs/archive/<id>/vN/<name> and MUST stay byte-identical to the live document it was cut
    # from (the engine's identity guard compares the bytes), so its relative links were written
    # for the live document's directory and cannot be rewritten. Resolve them there. Anything
    # else — including the archive's own HISTORY.md — resolves from its own directory as before.
    parts=p.relative_to(root).parts
    if len(parts)>=5 and parts[0]=="docs" and parts[1]=="archive" and _ARCHIVE_GENERATION.match(parts[3]):
        live=[q for q in root.glob(f"docs/**/{p.name}") if q.relative_to(root).parts[:2]!=("docs","archive")]
        if len(live)==1: return live[0].parent
    return p.parent
def check_links(root:Path)->list[str]:
    errors=[]; rx=re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for p in root.rglob("*.md"):
        base=_link_base(root,p)
        for target in rx.findall(p.read_text(encoding="utf-8")):
            if target.startswith(("http://","https://","mailto:","#")): continue
            target=target.split("#",1)[0]
            if target and not (base/target).resolve().exists(): errors.append(f"{p.relative_to(root)}: broken link {target}")
    return errors

def run(root:Path)->dict[str,Any]:
    checks={"modules":check_modules(root),"profiles_adapters":check_profiles_adapters(root),"examples_semantics":check_examples(root),"security_hygiene":check_hygiene(root),"links":check_links(root)}
    errors=[e for xs in checks.values() for e in xs]
    return {"schema_version":"1.0.0","root":str(root),"status":"PASS" if not errors else "FAIL","counts":{"checks":len(checks),"errors":len(errors)},"checks":{k:{"status":"PASS" if not v else "FAIL","errors":v} for k,v in checks.items()},"errors":errors}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("root",nargs="?",default=str(Path(__file__).resolve().parents[2])); ap.add_argument("--report"); a=ap.parse_args()
    r=run(Path(a.root).resolve()); text=json.dumps(r,indent=2)
    if a.report: Path(a.report).write_text(text+"\n",encoding="utf-8")
    print(text); raise SystemExit(0 if r["status"]=="PASS" else 1)
if __name__=="__main__": main()
