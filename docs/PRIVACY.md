# Privacy and Data Handling

## Local data

The following data is stored locally by default:

- Uploaded PDF files: `data/uploads/`
- Qdrant vectors and payloads: `data/qdrant/`
- Downloaded embedding model files: `data/models/`

These directories are excluded from Git.

## Data sent to Gemini

For answer generation, the application sends:

- The user's question
- The small set of source passages retrieved by Qdrant
- Source labels used to generate citations

It does not send numeric embedding vectors. It also does not intentionally send the entire PDF unless the retrieval result itself contains all of its text.

## API keys

The Gemini key belongs in `.env`. The file is excluded by `.gitignore`. Never paste a live key into screenshots, README files, commits, issue reports, or logs. Revoke and rotate any key that has been exposed.

## Reset behavior

`DELETE /documents/reset` removes the Qdrant collection and PDFs stored under `data/uploads/`. The downloaded embedding model cache remains because it contains no uploaded document content.

## Production warning

The current repository does not provide user authentication, encrypted document storage, tenant isolation, audit logging, data-loss prevention, or legal compliance controls. Do not use it for confidential documents without implementing and reviewing those controls.
