# Farm360 release checklist

## Blocking before production

- [ ] Apply migrations to an isolated PostgreSQL staging database and record the result.
- [ ] Configure a non-default `JWT_SECRET`.
- [ ] Configure same-site production frontend/API domains and secure cookies.
- [ ] Configure Razorpay Test Mode first: key ID, key secret and webhook secret.
- [ ] Subscribe the webhook to `payment.captured`, `payment.failed` and `refund.processed`.
- [ ] Complete signed webhook replay and amount/currency mismatch tests in Razorpay Test Mode.
- [ ] Confirm tax, invoice-number, refund and accounting policy.
- [ ] Run cross-customer/cross-zone API authorization suite against PostgreSQL.
- [ ] Replace permanent public evidence URLs with authorized private delivery.
- [ ] Complete backup and restore drill, including database and object storage.
- [ ] Configure structured logging/error monitoring without secrets or full payment credentials.
- [ ] Review privacy policy, terms, consent language and retention policy.
- [ ] Confirm actual business contacts, brand artwork and Telugu translations.
- [ ] Keep investments and land sales disabled.

## Explicitly deferred

- Native mobile distribution.
- Durable offline field queue and device conflict handling.
- Live payments, refunds, messages or notifications until separate launch authorization.
