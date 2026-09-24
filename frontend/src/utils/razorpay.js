const SCRIPT_URL = "https://checkout.razorpay.com/v1/checkout.js";

export async function openRazorpayCheckout(order, description) {
  if (!window.Razorpay) {
    await new Promise((resolve, reject) => {
      const existing = document.querySelector(`script[src="${SCRIPT_URL}"]`);
      if (existing) {
        existing.addEventListener("load", resolve, { once: true });
        existing.addEventListener("error", reject, { once: true });
        return;
      }
      const script = document.createElement("script");
      script.src = SCRIPT_URL;
      script.onload = resolve;
      script.onerror = reject;
      document.body.appendChild(script);
    });
  }

  return new Promise((resolve, reject) => {
    const checkout = new window.Razorpay({
      key: order.key_id,
      amount: order.amount,
      currency: order.currency,
      order_id: order.order_id,
      name: "Prasad Farm Care 360°",
      description,
      handler: resolve,
      modal: { ondismiss: () => reject(new Error("Payment cancelled")) },
      theme: { color: "#c9a84c" },
    });
    checkout.on("payment.failed", (response) => reject(new Error(response.error?.description || "Payment failed")));
    checkout.open();
  });
}
