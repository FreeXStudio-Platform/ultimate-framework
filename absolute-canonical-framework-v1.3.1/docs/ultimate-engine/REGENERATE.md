# Regenerating the Ultimate Engine documentation set

The regeneration command sequence for this repository's layout — payload plus vendored `engine/`,
no sibling `subject/` directory — is maintained in one place:
[`GUIDE-170-repository-release.md`](GUIDE-170-repository-release.md#regenerating-the-documentation-set-for-this-layout),
which is a governed document and therefore carries this documentation set's own lifecycle (tag,
wire, date, version, changelog, stamp). Keeping the sequence there instead of here avoids the two
normative copies of one procedure this framework's own rules exist to prevent.

`system.spec.json`'s `documentation-derivation` container names `GUIDE-170-repository-release.md`
as its owning document for the same reason: this file itself carries no doc-system header, so it
cannot appear in the completeness lifecycle table, and a procedure with no governed owner is a
procedure nobody's contract covers.

If this file's regeneration commands and GUIDE-170's ever disagree, GUIDE-170 is authoritative —
regenerate this pointer, not the other way around.
