#!/usr/bin/env bash
# Seal procedure for the current release — the executable form of the payload's
# 01_control_plane/manifests_releases/RELEASE_PROCEDURE.md (steps 0-8). GUIDE-170 in the payload is the
# normative description; this script only runs it. Usage:
#   scripts/release/seal.sh <report-dir>            # steps 0-3 (allowlist, metadata x3, verify) and stop
#   scripts/release/seal.sh <report-dir> --commit   # everything through build, artifact verification,
#                                                    # clean-room extraction, reproduction and record
#   scripts/release/seal.sh <report-dir> --build-only
# Requires: python3 with the pinned jsonschema/PyYAML, Graphviz at the recorded version, and the
# predecessor trees extracted (modes preserved) under <repo>/predecessor/ — see _release/predecessors/README.md.
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1
ROOT="$(git rev-parse --show-toplevel)"; R="$1"; MODE="${2:-dry}"
P="$(ls -d "$ROOT"/absolute-canonical-framework-v*/ | head -1)"; P="${P%/}"; V="$(cat "$P/VERSION")"
PRED="$(cd "$P/01_control_plane/manifests_releases/tools" && python3 -c "import release_integrity as r; print(r.BASELINE_CHAIN[-1]['release_id'].removeprefix('ABS.RELEASE.'))")"
mkdir -p "$R"; cd "$P" || exit 9
step(){ echo; echo "### $*"; }
hash_of(){ python3 01_control_plane/manifests_releases/tools/release_integrity.py candidate-hash . | grep -oE '[0-9a-f]{64}' | head -1; }

if [ "$MODE" = "--build-only" ]; then H2=$(hash_of); echo "build-only: candidate hash $H2"; MODE="--commit"; SKIP_PREP=1; else SKIP_PREP=0; fi
if [ "$SKIP_PREP" = "0" ]; then
step "0 hygiene"; find . -name __pycache__ -prune -exec rm -rf {} + ; rm -rf .docgen .health graphify-out .docgen_cache.json; find . -name .DS_Store -delete; echo "untracked in payload: $(cd "$ROOT" && git status --short --ignored absolute-canonical-framework-v1.3.0 | grep -c '^\(??\|!!\)')"
step "1 allowlist"; python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2 | tail -1; python3 01_control_plane/manifests_releases/tools/generate_release_allowlist.py . ../predecessor/absolute-canonical-framework-v1.0.0-rc.2 --check | tail -1
step "2 metadata (x3; hash must be stable across the last two)"
python3 tools/prepare_release_metadata.py --report "$R/prep1.json" >/dev/null 2>&1; echo "prep1 rc=$?"
python3 tools/prepare_release_metadata.py --report "$R/prep2.json" >/dev/null 2>&1; echo "prep2 rc=$?"; H1=$(hash_of)
python3 tools/prepare_release_metadata.py --report "$R/prep3.json" >/dev/null 2>&1; echo "prep3 rc=$?"; H2=$(hash_of)
echo "candidate hash after prep2: $H1"; echo "candidate hash after prep3: $H2"; [ "$H1" = "$H2" ] && echo "STABLE" || { echo "UNSTABLE"; exit 2; }
step "3 verify (fresh processes)"
python3 tools/deep_verify.py --report "$R/deep.json" > "$R/deep.out" 2>&1; echo "deep_verify rc=$? :: $(tail -n +1 "$R/deep.out" | grep -E '^(PASS|FAIL) ' | head -1)"
python3 tools/verifier_mutation_check.py --report "$R/mutation.json" > "$R/mutation.out" 2>&1; echo "mutation rc=$? :: $(head -1 "$R/mutation.out")"
python3 09_tests_evals/run_all.py --report "$R/validator.json" > "$R/run_all.json" 2>&1; echo "run_all rc=$? :: status $(python3 -c "import json;print(json.load(open('$R/run_all.json'))['status'])")"
python3 tools/check_no_loss.py --predecessor ../predecessor/absolute-canonical-framework-v$PRED --report "$R/noloss.json" > "$R/noloss.out" 2>&1; echo "no_loss rc=$? :: $(tail -1 "$R/noloss.out")"
python3 tests/run_successor_controls.py > "$R/successor.json" 2>&1; echo "successor_controls rc=$? :: $(python3 -c "import json;print(json.load(open('$R/successor.json'))['status'])")"
python3 tools/validate_v2_contracts.py > "$R/v2.json" 2>&1; echo "v2_contracts rc=$?"
find . -name __pycache__ | grep -q . && { echo "BYTECODE LEFT IN TREE"; exit 3; }
fi
[ "$MODE" = "--commit" ] || { echo; echo "PREP DONE — run with --commit to build"; exit 0; }
step "4 build"; ZIP="$ROOT/_release/absolute-canonical-framework-v$V.zip"; rm -f "$ZIP"
python3 01_control_plane/manifests_releases/tools/build_release.py . "$ZIP" --expected-candidate-sha256 "$H2" --authority-record .absolute/release/authority_record.json --gate-binding .absolute/release/gate_binding.json --report "$R/build-dry.json" > "$R/build-dry.out" 2>&1; echo "build dry rc=$?"
python3 01_control_plane/manifests_releases/tools/build_release.py . "$ZIP" --expected-candidate-sha256 "$H2" --authority-record .absolute/release/authority_record.json --gate-binding .absolute/release/gate_binding.json --commit --report "$R/build.json" > "$R/build.out" 2>&1; echo "build commit rc=$?"; ls -la "$ZIP"
step "5 verify the artifact"
python3 01_control_plane/manifests_releases/tools/verify_release.py "$ZIP" --expected-candidate-sha256 "$H2" --report "$R/verify_release.json" > "$R/verify_release.out" 2>&1; echo "verify_release rc=$?"
python3 tools/verify_successor_release.py "$ZIP" --expected-candidate-sha256 "$H2" > "$R/verify_successor.out" 2>&1; echo "verify_successor_release rc=$?"
step "6 clean-room extract (modes preserved) + full suite there"
CR="$ROOT/_cleanroom"; rm -rf "$CR"; mkdir -p "$CR"
python3 - "$ZIP" "$CR" <<'PY'
import zipfile,os,sys
from pathlib import Path
z=zipfile.ZipFile(sys.argv[1]); out=Path(sys.argv[2])
for i in z.infolist():
    t=out/i.filename
    if i.is_dir(): t.mkdir(parents=True,exist_ok=True); continue
    t.parent.mkdir(parents=True,exist_ok=True); t.write_bytes(z.read(i)); m=(i.external_attr>>16)&0xFFFF
    if m: os.chmod(t,m)
print("extracted", len(z.infolist()))
PY
mkdir -p "$CR/predecessor" && cp -R "$ROOT/predecessor/absolute-canonical-framework-v1.2.0" "$CR/predecessor/"
( cd "$CR/absolute-canonical-framework-v$V" && python3 tools/deep_verify.py --quiet > "$R/cleanroom-deep.out" 2>&1; echo "cleanroom deep_verify rc=$? :: $(cat "$R/cleanroom-deep.out")"; python3 09_tests_evals/run_all.py > "$R/cleanroom-run_all.json" 2>&1; echo "cleanroom run_all rc=$?"; python3 tools/check_no_loss.py --predecessor ../predecessor/absolute-canonical-framework-v$PRED > "$R/cleanroom-noloss.out" 2>&1; echo "cleanroom no_loss rc=$?" )
step "7 reproduce from a fresh staging copy"
ST="$ROOT/_staging"; rm -rf "$ST"; mkdir -p "$ST"; cp -R "$P" "$ST/"; cp -R "$ROOT/predecessor" "$ST/" 2>/dev/null
( cd "$ST/absolute-canonical-framework-v$V" && python3 01_control_plane/manifests_releases/tools/build_release.py . "$ST/repro.zip" --expected-candidate-sha256 "$H2" --authority-record .absolute/release/authority_record.json --gate-binding .absolute/release/gate_binding.json --commit > "$R/repro-build.out" 2>&1; echo "repro build rc=$?" )
A=$(shasum -a 256 "$ZIP" | cut -d' ' -f1); B=$(shasum -a 256 "$ST/repro.zip" | cut -d' ' -f1); echo "sealed  $A"; echo "repro   $B"; [ "$A" = "$B" ] && echo "REPRODUCIBLE" || echo "NOT REPRODUCIBLE"
step "8 record"; (cd "$ROOT/_release" && shasum -a 256 "absolute-canonical-framework-v$V.zip" > "absolute-canonical-framework-v$V.zip.sha256" && cat "absolute-canonical-framework-v$V.zip.sha256")
echo "CANDIDATE_TREE_SHA256=$H2" > "$R/identity.env"; echo "ZIP_SHA256=$A" >> "$R/identity.env"; echo "ZIP_BYTES=$(stat -f%z "$ZIP")" >> "$R/identity.env"
rm -rf "$ST" "$CR"; echo; echo "SEAL COMPLETE"
