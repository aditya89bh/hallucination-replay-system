# Security and Privacy

`hallucination-replay-system` works with AI agent traces. Traces can contain prompts, model outputs, retrieval content, memory records, tool inputs, tool outputs, validation events, metadata, and failure reports. Treat trace data as sensitive by default.

## Trace storage considerations

The default repository stores trace artifacts on the filesystem. Before using it with real traces:

- choose a directory with restricted filesystem permissions;
- avoid shared world-readable locations;
- exclude trace directories from public repositories;
- configure backups according to your data retention policy;
- delete traces when they are no longer needed;
- avoid storing production secrets in benchmark fixtures.

For CI workflows, use sanitized fixtures only. If CI artifacts include reports or trace exports, make sure artifact visibility matches your organization’s privacy expectations.

## Sensitive data handling

Traces may include:

- customer or end-user text;
- private prompts and system instructions;
- retrieved document snippets;
- memory records;
- API request and response payloads;
- tool arguments and outputs;
- internal identifiers;
- validation failures and incident context.

Before sharing a trace, report, dashboard page, or benchmark fixture:

1. Remove secrets, tokens, passwords, cookies, and credentials.
2. Redact customer data and personally identifiable information.
3. Remove private prompts and proprietary policy text unless explicitly approved.
4. Replace internal hostnames, ticket IDs, and account IDs if they are sensitive.
5. Review tool outputs for embedded credentials or private payloads.

## Privacy recommendations

- Prefer synthetic or heavily sanitized traces for demos.
- Store minimal trace content needed to reproduce the failure.
- Separate raw traces from public documentation and benchmark fixtures.
- Keep incident reports access-controlled.
- Establish retention windows for debugging traces.
- Document who can access trace repositories and generated reports.

## API and dashboard deployment considerations

The FastAPI app and dashboard helpers are designed for trusted local or internal use. The core package does not provide built-in authentication, authorization, tenant isolation, or rate limiting.

If you expose the API or dashboard beyond a local machine:

- place it behind your organization’s authentication layer;
- restrict network access with firewall or private networking rules;
- use TLS at the edge;
- enforce authorization before returning traces or reports;
- rate limit upload and analysis endpoints;
- monitor logs for sensitive data exposure;
- avoid serving unredacted dashboard HTML publicly.

## Report handling

Markdown, JSON, and HTML reports can contain the same sensitive information as the original traces. Treat generated reports as derived sensitive data.

Recommended practices:

- write reports to controlled directories;
- avoid committing reports generated from production traces;
- sanitize report excerpts before sharing them externally;
- delete temporary report artifacts after incident review;
- include report retention in your incident response process.

## Dependency and supply-chain notes

The project is a Python package with a small runtime dependency set. Before release or deployment:

- build from a clean checkout;
- verify wheel and source distribution contents;
- install dependencies from trusted package indexes;
- run tests, coverage, Ruff, MyPy, build, and repository validation;
- review CI workflow permissions;
- avoid publishing from machines with untrusted local modifications.

## Reporting vulnerabilities

If you discover a security issue in the project, do not publish exploit details in a public issue. Contact the repository maintainer privately or use the repository’s preferred private disclosure path if one is configured.
