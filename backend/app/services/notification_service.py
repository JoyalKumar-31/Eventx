from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.enums import NotificationType


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    type: NotificationType = NotificationType.INFO,
    link: Optional[str] = None
) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        link=link,
        is_read=False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_user_notifications(
    db: Session,
    user_id: int,
    limit: int = 50,
    unread_only: bool = False
) -> List[Notification]:
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


def mark_notifications_read(
    db: Session,
    user_id: int,
    notification_ids: Optional[List[int]] = None
) -> int:
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if notification_ids:
        query = query.filter(Notification.id.in_(notification_ids))
    count = query.update({Notification.is_read: True}, synchronize_session=False)
    db.commit()
    return count


def get_unread_count(db: Session, user_id: int) -> int:
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()
