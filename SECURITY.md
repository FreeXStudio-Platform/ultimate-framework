# Security policy

## Reporting a vulnerability

Please report suspected vulnerabilities **privately** by email to **Admin@FreeXStudio.com** with
"SECURITY" in the subject. Please do not open a public issue.

Include the affected file and release (`VERSION`), what you observed, and — where you can — a minimal
reproduction. Please do not open a public issue or publish exploit details before a fix is available.
You will get an acknowledgement; we will agree a disclosure timeline with you.

## Scope

In scope: the `absolute` runtime, the verifiers and release tooling under
`absolute-canonical-framework-v1.3.1/`, and the vendored `engine/`. The payload's own
`SECURITY.md` states the security boundary the runtime enforces in code (no network calls, no
credential reads, writes confined to the project tree).

The ledger makes tampering *evident*, not impossible (see the payload's `LIMITATIONS.md`);
reports that restate that documented property are not vulnerabilities.

## Supported versions

Only the latest release receives fixes.
