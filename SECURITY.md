# Security Policy

## Supported version

Security fixes target the latest version on the `main` branch.

## Reporting a vulnerability

Do not open a public issue containing API keys, private documents, personal data, or a working exploit. Contact the repository owner privately through the contact method listed on the GitHub profile.

Include:

- A concise description
- Reproduction steps
- Affected component
- Potential impact
- Suggested mitigation, when available

## Secret exposure

If a Gemini API key appears in a screenshot, commit, log, or issue:

1. Revoke the key immediately.
2. Create a replacement key.
3. Remove the key from the current files.
4. Purge it from Git history when committed.
5. Review API usage for abuse.

## Known security limitations

The project is a local educational prototype and does not currently include authentication, multi-tenant isolation, encrypted storage, malware scanning, OCR sandboxing, or production-grade rate limiting.
