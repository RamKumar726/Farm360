import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.notifications import Notification, NotificationType, NotificationChannel
from app.models.users import User, UserRole
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


def success(data=None, message=""):
    return {"success": True, "data": data, "message": message}


class WhatsAppSend(BaseModel):
    user_id: str
    message: str


def notif_to_dict(n: Notification):
    return {
        "id": n.id, "type": n.type.value, "message": n.message,
        "channel": n.channel.value, "sent_via_whatsapp": n.sent_via_whatsapp,
        "is_read": n.is_read, "created_at": str(n.created_at),
    }


@router.get("")
def list_notifications(
    page: int = Query(1, ge=1), page_size: int = Query(30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    total = query.count()
    items = query.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(data={"total": total, "unread": query.filter(Notification.is_read == False).count(),
                         "items": [notif_to_dict(n) for n in items]})


@router.post("/send-whatsapp")
def send_whatsapp(
    body: WhatsAppSend,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user or not user.phone:
        raise HTTPException(400, "User has no phone number registered")
    from app.utils.twilio_client import send_whatsapp_message
    try:
        send_whatsapp_message(user.phone, body.message)
        return success(message=f"WhatsApp message sent to {user.phone}")
    except Exception as e:
        raise HTTPException(500, f"WhatsApp send failed: {str(e)}")


@router.patch("/{notif_id}/read")
def mark_read(notif_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == current_user.id).first()
    if not notif:
        raise HTTPException(404, "Notification not found")
    notif.is_read = True
    db.commit()
    return success(message="Marked as read")
