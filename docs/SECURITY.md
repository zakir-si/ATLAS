# Security and deployment boundary

## Current release

This is a local-development scaffold. The API has no authentication, authorization, tenant isolation, persistent job queue or hardened artifact store. Do not expose it to the public internet or an untrusted network. The API accepts measurement metadata only; do not send secrets or private training data.

## Before shared or enterprise deployment

- Document a threat model and deployment trust boundaries.
- Add authentication and least-privilege authorization.
- Protect tenant and artifact boundaries; encrypt network traffic and sensitive storage.
- Keep secrets out of source control and notebooks; use a secret manager.
- Validate paths/uploads and enforce request, time and resource limits.
- Treat model files, datasets and remote code as untrusted; do not enable arbitrary remote code by default.
- Add audit events for configuration changes, job actions, access and artifact exports.
- Add dependency, secret and container scanning; produce an SBOM and build provenance.
- Define data retention/deletion, backup/restore, incident response and vulnerability disclosure.
- Perform deployment-specific security review and penetration testing.

Please do not post sensitive exploit details in public issues. Use GitHub private vulnerability reporting if enabled.
