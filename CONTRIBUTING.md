# Contributing

Thanks for helping. Issues, questions and pull requests are welcome.

## Ground rules

- Be kind — see the [Code of Conduct](CODE_OF_CONDUCT.md).
- **Never commit secrets or personal data.** No credentials, tokens, private keys, absolute paths
  from your machine, or personal email addresses. Use `git config user.email` with a no-reply address.
- Report security issues privately — [SECURITY.md](SECURITY.md).
- By contributing you agree your contribution is licensed under Apache-2.0 (the repository license).

## How the repository is shaped

`absolute-canonical-framework-v1.3.1/` is a **hash-bound release payload**. Every file in it is
enumerated by `RELEASE_ALLOWLIST.json` and bound by `MANIFEST.json` and `SHA256SUMS.txt`, and the
verifier refuses a tree where they disagree. So a change to the payload is not a normal edit — it
becomes a new release, cut by a maintainer following
`absolute-canonical-framework-v1.3.1/docs/ultimate-engine/GUIDE-170-repository-release.md`.

That is not a barrier to contributing; it just shapes the workflow:

1. **Open an issue first** for anything that touches the payload, so we can agree the change and
   its release placement.
2. **Fork, branch, and open a pull request** with the change and the reasoning. You do not need to
   regenerate the allowlist, the metadata or the stamps — a maintainer does that when cutting the
   release. A payload pull request will therefore show verifier findings for the hash-bound files;
   that is expected.
3. Changes outside the payload (docs at the repository root, `scripts/`, `.github/`, `engine/`) are
   ordinary pull requests.

## Local checks

```sh
cd absolute-canonical-framework-v1.3.1
python3 -m pip install -r 04_enforcement/requirements-validation.txt
PYTHONDONTWRITEBYTECODE=1 python3 09_tests_evals/run_all.py
PYTHONDONTWRITEBYTECODE=1 python3 tools/deep_verify.py
```

Always set `PYTHONDONTWRITEBYTECODE=1` when touching the payload — a stray `__pycache__` is a file the
tree-identity control will find. Keep PRs small and say what you ran.

## Commit style

Imperative subject, one logical change per commit, explain the *why* in the body.
