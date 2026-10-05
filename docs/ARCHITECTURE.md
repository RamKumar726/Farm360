# Farm360 architecture

## Delivery decision

Farm360 is currently a responsive web application. Native Customer, Agriculture Officer and Farm Employee applications are explicitly deferred. The responsive web surfaces must not be represented as released native apps, and durable device-offline execution remains a tracked gap.

## Runtime boundaries

- `frontend/`: React/Vite browser client. It contains presentation and interaction only; business authorization is enforced by the API.
- `backend/app/`: FastAPI modular monolith and shared business records.
- PostgreSQL: authoritative transactional store, evolved only through Alembic.
- Render worker: four-day work-order assignment and managed-service renewal processing.
- Cloudinary, Razorpay and Twilio: provider adapters. Production credentials and live modes are environment-controlled.
- Netlify/Render: current hosting configuration. A same-site production API domain is recommended for reliable HttpOnly cookie behavior.

## Authoritative record chain

Customer account → customer profile → farm/property → lead/service request → quote version → acceptance → invoice → payment/allocation → project → work order → proof/review.

IDs remain stable across role portals. Land sale and investment modules are disabled by default and are not part of the supported release scope.

## Security model

- HttpOnly authentication cookies; no browser-persisted bearer token.
- Role checks plus row-scope helpers for farms, projects, agreements, invoices and payments.
- Customer, zone and assignment scope is checked by the API even when a UI route is hidden.
- Critical quote and payment changes create append-only audit events.
- Live payment startup requires key ID, key secret and webhook secret.
- Captured provider status, amount, currency and order ID must all reconcile before fulfillment.

## Payment flow

1. AO creates quote version.
2. A different authorized employee approves it.
3. Approved version is sent to the linked customer.
4. Customer accepts the exact latest version.
5. Acceptance snapshot and immutable issued invoice are created together.
6. API creates a Razorpay order tied to the quote and invoice.
7. Browser callback is HMAC checked and the payment is fetched from Razorpay.
8. Signed webhook is stored and deduplicated.
9. Only a captured, matching payment is allocated to the invoice and triggers project conversion.

## Known architectural gaps

See `BUILD_STATUS.md`. The largest remaining domains are native/offline execution, conversations, private signed files, full assessment records, subscriptions/billing periods, lease-case separation and operational observability.
