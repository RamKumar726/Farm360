# API conventions

- JSON success envelope: `{ "success": true, "data": ..., "message": "..." }`.
- Errors use HTTP status codes and FastAPI's `detail` field.
- List endpoints use one-based `page` and bounded `page_size` values and return `total` plus `items`.
- UUID-compatible opaque string IDs are used externally; callers must not infer authorization from IDs.
- Dates are ISO-8601. New timestamps are UTC-aware.
- New financial contracts use integer paise internally and expose rupee decimal values at API boundaries.
- Retried state-changing integrations require stable provider/event identifiers.
- Webhooks are authenticated against the exact raw body before JSON parsing.
- A duplicate webhook returns success without applying business effects again.
- Out-of-scope features return 404 and are not registered as active API modules.
- Private records return 404, rather than confirming existence, when outside the caller's row scope.
