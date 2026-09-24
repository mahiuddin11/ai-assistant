import structlog
from sqlalchemy.orm import Session
from models import Permission, PermissionAuditLog

logger = structlog.get_logger()


def _log_audit(db: Session, user_id: str, tool_name: str, action: str) -> None:
    """Audit log-এ একটা এন্ট্রি যোগ করে — এই ফাংশন ছাড়া কখনো সরাসরি permission_audit_log-এ লেখা হবে না।"""
    entry = PermissionAuditLog(user_id=user_id, tool_name=tool_name, action=action)
    db.add(entry)
    db.commit()


def grant_permission(db: Session, user_id: str, tool_name: str) -> Permission:
    permission = Permission(user_id=user_id, tool_name=tool_name, status="granted")
    db.add(permission)
    db.commit()
    db.refresh(permission)

    _log_audit(db, user_id, tool_name, "grant")
    logger.info("permission_granted", user_id=user_id, tool_name=tool_name)
    return permission


def revoke_permission(db: Session, user_id: str, tool_name: str) -> bool:
    permission = (
        db.query(Permission)
        .filter(Permission.user_id == user_id, Permission.tool_name == tool_name, Permission.status == "granted")
        .order_by(Permission.granted_at.desc())
        .first()
    )

    if permission is None:
        return False

    from datetime import datetime, timezone
    permission.status = "revoked"
    permission.revoked_at = datetime.now(timezone.utc)
    db.commit()

    _log_audit(db, user_id, tool_name, "revoke")
    logger.info("permission_revoked", user_id=user_id, tool_name=tool_name)
    return True


def is_permission_granted(db: Session, user_id: str, tool_name: str) -> bool:
    """coarse-grained check — এই user-এর জন্য এই টুল বর্তমানে granted কিনা।"""
    permission = (
        db.query(Permission)
        .filter(Permission.user_id == user_id, Permission.tool_name == tool_name)
        .order_by(Permission.granted_at.desc())
        .first()
    )

    allowed = permission is not None and permission.status == "granted"
    _log_audit(db, user_id, tool_name, "check_allowed" if allowed else "check_denied")
    return allowed