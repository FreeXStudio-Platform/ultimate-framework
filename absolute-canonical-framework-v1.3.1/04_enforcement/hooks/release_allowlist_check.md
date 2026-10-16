# Release Allowlist Hook
Run the deterministic validator, build staging from the source allowlist, reject archives/caches/chats/raw sources/secrets/symlinks/unmanifested files, create `MANIFEST.json` and `SHA256SUMS.txt`, build with fixed metadata, then verify CRC, path safety, single-root extraction, inventory, and post-extraction hashes.
