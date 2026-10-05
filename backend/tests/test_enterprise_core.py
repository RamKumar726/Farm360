import hashlib
import hmac
import os
import sys
import unittest
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import FEATURE_INVESTMENTS, FEATURE_LAND_SALES
from app.models.finance import Payment, PaymentPurpose
from app.database import Base, get_db
from app.main import app
from app.models.customers import Customer
from app.models.leads import Lead, LeadSource, LeadStatus, LeadType
from app.models.farms import Farm
from app.models.users import User, UserRole
from app.auth.jwt import create_access_token, hash_password
from app.routers.payments import _verify_provider_payment, verify_webhook_signature
from app.routers.quotes import rupees_to_paise


class EnterpriseCoreTests(unittest.TestCase):
    def test_out_of_scope_modules_default_off(self):
        self.assertFalse(FEATURE_INVESTMENTS)
        self.assertFalse(FEATURE_LAND_SALES)

    def test_money_conversion_uses_decimal_rounding(self):
        self.assertEqual(rupees_to_paise(Decimal("19.995")), 2000)
        self.assertEqual(rupees_to_paise(Decimal("0.01")), 1)

    def test_webhook_signature_uses_raw_body_hmac(self):
        raw = b'{"event":"payment.captured","amount":12500}'
        secret = "test-webhook-secret"
        signature = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
        self.assertTrue(verify_webhook_signature(raw, signature, secret))
        self.assertFalse(verify_webhook_signature(raw + b" ", signature, secret))
        self.assertFalse(verify_webhook_signature(raw, "bad", secret))

    def test_provider_payment_must_be_captured_and_match_order(self):
        payment = Payment(
            id="p-1", payer_user_id="u-1", purpose=PaymentPurpose.lead,
            amount_paise=12500, currency="INR", gateway_order_id="order-1",
        )
        _verify_provider_payment(payment, {
            "id": "pay-1", "order_id": "order-1", "status": "captured",
            "captured": True, "amount": 12500, "currency": "INR",
        })
        with self.assertRaises(HTTPException):
            _verify_provider_payment(payment, {
                "id": "pay-1", "order_id": "order-1", "status": "authorized",
                "captured": False, "amount": 12500, "currency": "INR",
            })
        with self.assertRaises(HTTPException):
            _verify_provider_payment(payment, {
                "id": "pay-1", "order_id": "order-1", "status": "captured",
                "captured": True, "amount": 12499, "currency": "INR",
            })


class QuotationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine, autoflush=False, autocommit=False)

        def override_db():
            db = cls.Session()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_db
        cls.client = TestClient(app)
        with cls.Session() as db:
            for user_id, role in (("ao-1", UserRole.agri_officer), ("office-1", UserRole.employee), ("customer-1", UserRole.customer), ("customer-2", UserRole.customer)):
                db.add(User(
                    id=user_id, name=user_id, email=f"{user_id}@example.test",
                    password_hash=hash_password("Safe-Test-Password-1"), role=role,
                ))
            db.add(Customer(id="customer-profile-1", user_id="customer-1"))
            db.add(Customer(id="customer-profile-2", user_id="customer-2"))
            db.add(Farm(id="farm-1", customer_id="customer-profile-1", location="Customer One Farm"))
            db.add(Farm(id="farm-2", customer_id="customer-profile-2", location="Customer Two Farm"))
            db.add(Lead(
                id="lead-quote-1", type=LeadType.one_time_service,
                source=LeadSource.customer_app, status=LeadStatus.decision_makers,
                customer_id="customer-1", assigned_ao_id="ao-1",
                employee_id="office-1", assigned_employee_id="office-1",
                contact_name="Demo Customer", services_needed="Irrigation setup",
            ))
            db.commit()

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        cls.engine.dispose()

    @staticmethod
    def auth(user_id: str):
        return {"Authorization": f"Bearer {create_access_token({'sub': user_id})}"}

    def test_exact_quote_acceptance_creates_invoice(self):
        response = self.client.post(
            "/leads/lead-quote-1/ao-quotation",
            headers=self.auth("ao-1"),
            json={
                "services_needed": "Drip irrigation installation",
                "price_to_complete": "12500.50",
                "solution_summary": "Includes installation and commissioning.",
            },
        )
        self.assertEqual(response.status_code, 200, response.text)

        response = self.client.post("/leads/lead-quote-1/review-quote?action=review", headers=self.auth("office-1"))
        self.assertEqual(response.status_code, 200, response.text)
        response = self.client.post("/leads/lead-quote-1/review-quote?action=send", headers=self.auth("office-1"))
        self.assertEqual(response.status_code, 200, response.text)

        response = self.client.get("/quotes/leads/lead-quote-1", headers=self.auth("customer-1"))
        self.assertEqual(response.status_code, 200, response.text)
        quote = response.json()["data"][0]
        self.assertEqual(quote["status"], "sent")
        self.assertEqual(quote["total"], 12500.5)

        response = self.client.post(f"/quotes/{quote['id']}/accept", headers=self.auth("customer-1"))
        self.assertEqual(response.status_code, 200, response.text)
        response = self.client.get("/invoices", headers=self.auth("customer-1"))
        self.assertEqual(response.status_code, 200, response.text)
        invoice = response.json()["data"]["items"][0]
        self.assertEqual(invoice["total"], 12500.5)
        self.assertEqual(invoice["balance"], 12500.5)
        self.assertEqual(invoice["status"], "issued")

    def test_customer_cannot_read_another_customers_farm(self):
        response = self.client.get("/farms", headers=self.auth("customer-1"))
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual([row["id"] for row in response.json()["data"]["items"]], ["farm-1"])
        response = self.client.get("/farms/farm-2", headers=self.auth("customer-1"))
        self.assertEqual(response.status_code, 404, response.text)


if __name__ == "__main__":
    unittest.main()
