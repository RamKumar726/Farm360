# Farm360 decisions

## Confirmed for the current implementation

1. Web application only for the present milestone; native delivery is deferred.
2. Razorpay is the current hosted payment provider.
3. INR is the only enabled checkout currency.
4. Money introduced by the new quote/invoice/payment flow is stored in integer paise.
5. Land sales and investments are disabled by default and displayed as Coming Soon.
6. Browser redirects never independently mark payment successful.
7. Exact quote-version acceptance is required before payment.
8. Quote creators cannot approve their own quotes.
9. Existing React/FastAPI/PostgreSQL stack is retained as a modular monolith.
10. Production authentication uses HttpOnly cookies and must not return tokens to browser JavaScript.

## Business decisions still required

- Tax registration, tax calculation and invoice numbering policy.
- Deposit/milestone/recurring billing rules per service.
- Refund authorization and chargeback operating procedure.
- Approval limits and second-approver assignments.
- Lease legal templates and professional review ownership.
- Data retention/deletion periods and audit exceptions.
- Customer evidence publication policy.
- Production contact details, privacy policy, terms and Telugu review.
- Recovery objectives, backup ownership and incident response contacts.
