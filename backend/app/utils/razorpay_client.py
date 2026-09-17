import razorpay
from app.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET


def get_client():
    return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def create_order(amount_paise: int, currency: str = "INR", receipt: str = "order") -> dict:
    """Create a Razorpay order. amount_paise is in paise (1 INR = 100 paise)."""
    client = get_client()
    return client.order.create({
        "amount": amount_paise,
        "currency": currency,
        "receipt": receipt,
    })


def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Verify Razorpay payment signature to confirm payment authenticity."""
    client = get_client()
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })
        return True
    except Exception:
        return False
