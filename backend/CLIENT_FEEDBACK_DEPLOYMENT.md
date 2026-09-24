# Farm360 client feedback workflows: deployment notes

The workflow changes in this branch require a database schema update and a continuously running scheduler process.

## Required environment

Configure the backend with its production `DATABASE_URL`, `FRONTEND_URL`, `RAZORPAY_KEY_ID`, and `RAZORPAY_KEY_SECRET`. Set the Cloudinary variables when proof/document uploads are enabled. Keep secrets in the deployment secret store; do not commit `.env` files.

## Database migration

1. Take a database backup and confirm it can be restored.
2. Deploy the backend code and install `backend/requirements.txt` in the backend runtime.
3. From `backend/`, run `alembic upgrade head` against the intended database.
4. Confirm the API health endpoint and inspect the Alembic revision before enabling customer payment flows.

The migrations add workflow fields, payment/expense/settlement records, the database-backed one-time service catalog, and new project/work-order statuses. They have not been applied to the configured database from this workspace.

The later migrations also add task proof history, work start timestamps, and authenticated provider accounts. Before assigning outsourced work, create a user with the `work_partner` role, then link that login email to the provider record in Partner Assignment. Existing provider records require the same account link before the provider portal can confirm dates or upload task proof.

## Scheduler process

Run a separate long-lived worker alongside the API:

```sh
cd backend
python -m app.services.work_order_scheduler
```

Keep it under the platform's process supervisor and monitor its logs. The worker assigns eligible tasks approaching their due date and creates subscription renewal opportunities shortly before expiry. Running only the API does not run these scheduled jobs.

## Payment setup

Use Razorpay test credentials for staging and live credentials for production. Checkout confirmation is verified server-side; successful payment depends on a reachable Razorpay account and a migrated database. Never use the example credentials in `.env.example` as production values.

Investor and landowner disbursements are recorded with a transfer reference and proof document after an external bank transfer. The current app does not initiate outbound bank payouts through a payment provider; do not present these recorded payouts as automatically transferred.
