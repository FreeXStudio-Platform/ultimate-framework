# Interface fixtures

One positive and one negative instance for every interface in
`docs/registries/INTERFACE_INDEX.json`.

Before these existed, the 29 interface schemas were declared, indexed, and
referenced by module integration files — but never executed. A schema that
nothing validates against is an assertion, not a contract: it can drift, or be
wrong from the day it was written, and no test would notice.

Each `*.valid.json` must be accepted by its schema. Each `*.invalid.json` must
be rejected, and is built by removing a required field and injecting a forbidden
`authority_override` property, so it exercises both required-ness and
`additionalProperties: false` rather than failing for an incidental reason.

`tools/deep_verify.py` (section `FRAMEWORK_CONTRACTS`) fails if a pair is
missing, if a valid fixture is rejected, or if an invalid fixture is accepted.
