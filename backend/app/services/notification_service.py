"""
Notification Service
Triggers WhatsApp + in-app notifications for all 15 business cycle events.
"""
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.notifications import Notification, NotificationType, NotificationChannel
from app.models.users import User


def create_notification(
    user_id: str,
    notif_type: NotificationType,
    message: str,
    channel: NotificationChannel = NotificationChannel.both,
    db: Session = None,
) -> Notification:
    notif = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=notif_type,
        message=message,
        channel=channel,
        sent_via_whatsapp=False,
    )
    if db:
        db.add(notif)
        db.commit()
        db.refresh(notif)
        # Attempt WhatsApp delivery
        if channel in [NotificationChannel.whatsapp, NotificationChannel.both]:
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.phone:
                _send_whatsapp(user.phone, message, notif, db)
    return notif


def _send_whatsapp(phone: str, message: str, notif: Notification, db: Session):
    """Send WhatsApp message via Twilio. Fail silently — notification is still stored."""
    try:
        from app.utils.twilio_client import send_whatsapp_message
        send_whatsapp_message(to_phone=phone, message=message)
        notif.sent_via_whatsapp = True
        db.commit()
    except Exception as e:
        # Log but don't fail the main flow
        print(f"[WhatsApp] Failed to send to {phone}: {e}")


# --- Convenience trigger functions for each business event ---

def notify_new_lead(employee_id: str, message: str, db: Session):
    create_notification(employee_id, NotificationType.new_lead, message, db=db)


def notify_work_order_created(user_id: str, work_order_id: str, db: Session):
    create_notification(
        user_id, NotificationType.work_order_created,
        f"New work order #{work_order_id[:8]} has been created and assigned.", db=db
    )


def notify_work_order_completed(customer_id: str, work_order_id: str, db: Session):
    create_notification(
        customer_id, NotificationType.work_order_completed,
        f"Work order #{work_order_id[:8]} has been completed. Please review proof.", db=db
    )


def notify_prescription_sent(recipient_id: str, prescription_id: str, db: Session):
    create_notification(
        recipient_id, NotificationType.prescription_sent,
        f"A new prescription #{prescription_id[:8]} has been sent for your review.", db=db
    )


def notify_investment_posted(user_id: str, project_name: str, db: Session):
    create_notification(
        user_id, NotificationType.investment_project_posted,
        f"New investment project '{project_name}' is now open for investment.", db=db
    )


def notify_land_sale_listed(user_id: str, location: str, db: Session):
    create_notification(
        user_id, NotificationType.land_sale_listed,
        f"A new land listing is available at {location}.", db=db
    )


def notify_partner_response(employee_id: str, partner_name: str, accepted: bool, db: Session):
    status_str = "accepted" if accepted else "rejected"
    notif_type = NotificationType.partner_accepted if accepted else NotificationType.partner_rejected
    create_notification(
        employee_id, notif_type,
        f"Work partner '{partner_name}' has {status_str} the assignment.", db=db
    )


def notify_incident_reported(admin_id: str, farm_id: str, db: Session):
    create_notification(
        admin_id, NotificationType.incident_reported,
        f"An incident has been reported on farm #{farm_id[:8]}. Please review.", db=db
    )


def notify_revenue_credited(customer_id: str, amount: float, db: Session):
    create_notification(
        customer_id, NotificationType.revenue_credited,
        f"₹{amount:,.2f} has been credited to your investment account.", db=db
    )


def notify_approval_required(user_id: str, context: str, db: Session):
    create_notification(
        user_id, NotificationType.approval_required,
        f"Your approval is required: {context}", db=db
    )
