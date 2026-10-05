# Farm360 build status

Updated: 2026-10-01

## Supported now

- Responsive React web delivery for the existing role portals.
- FastAPI/PostgreSQL modular-monolith foundation and Alembic migration chain.
- Public and authenticated lead intake.
- Farm, project, visit, work-order, proof, issue, harvest and finance prototype records.
- Four-days-ahead work assignment worker.
- Itemized/versioned quote records with separated internal cost.
- Independent approval, exact latest-version customer acceptance and acceptance snapshot.
- Invoice/line creation and payment allocation records in integer paise.
- Razorpay order creation, callback HMAC verification and provider-side captured-state fetch.
- Raw-body webhook HMAC verification, event deduplication and captured/failed/refund processing.
- Payment amount, currency and order reconciliation before business transition.
- Append-only audit records for quote and payment events.
- Scoped farm, project, agreement, invoice and payment reads.
- Investments and land sales disabled by default in API and principal navigation.
- HttpOnly cookie authentication without localStorage access tokens.

## Partial

- Some older finance/project tables still use floating-point money and require additive conversion migrations.
- Existing portal dashboards do not yet expose every new audit/reconciliation action.
- Proof review exists, but customer publication is not yet a distinct persisted transition.
- Direct lease workflow exists in lead/project form but partner matching is not a separate case aggregate.
- Notifications exist but do not yet use a transactional outbox/delivery-attempt ledger.
- File uploads use provider URLs rather than signed private access.

## Not implemented

- Native apps and durable offline sync.
- Full assessment/sample/lab provenance domain.
- Subscription, billing-period and crop-cycle separation.
- Conversation membership/messages and attachment authorization.
- Full refund initiation, chargeback and manual transfer verification workflows.
- Policy-versioned approval limits and delegation.
- Backup restore drill, production observability and performance/UAT evidence.

## Verification evidence

- Python compile: passed.
- FastAPI import: passed.
- SQLAlchemy metadata creation: passed (37 tables).
- Alembic graph: one head, `20261001_enterprise`.
- Unit/integration tests: 6 passed, including exact-version quote acceptance, invoice creation and cross-customer farm denial.
- Frontend production build: passed; bundle-size warning remains.
- Frontend lint: completes with pre-existing warnings and no errors.

Commands:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
cd frontend
npm run lint
npm run build
```

PostgreSQL staging migration is required before release. The legacy initial migration uses PostgreSQL-style constraint operations and therefore is not validated by SQLite Alembic upgrade.
