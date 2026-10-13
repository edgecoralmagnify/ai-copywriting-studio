# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.6.x   | ✅        |
| 0.5.x   | ⚠️ security fixes only |
| < 0.5   | ❌        |

## Reporting a vulnerability

Do **not** open a public issue for security problems. Email
`security@ai-copywriting-studio.dev` with:

- A description of the issue and its impact.
- Steps to reproduce, ideally a minimal brief + config.
- The version (`ai-copywriting-studio --version`) and OS build.

We aim to acknowledge within 72 hours and ship a fix within 14 days for
confirmed issues.

## Scope

In scope:

- Prompt-injection paths where a brief file can hijack a processor's system
  prompt or exfiltrate the API key.
- Path traversal in any driver that writes to disk (`drivers/file_*`).
- Credential leaks in logs (`utils.logging` redaction bypasses).
- Deserialization of untrusted job files in `queue/job_store.py`.

Out of scope:

- The quality or factual accuracy of generated copy. That's a model problem,
  not a security problem.
- Running the tool against a provider you don't trust.

## Hardening notes

- API keys live in the Windows Credential Manager via `keyring`, never in
  `config/*.toml`.
- Job files are JSON, parsed with a strict schema. No pickle, no eval.
- Drivers that write files resolve every path under `data/exports/` and
  reject anything that escapes it.