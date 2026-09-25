import structlog
from sqlalchemy.orm import Session
from models import Task
# from event_publisher import publish_task_event

logger = structlog.get_logger()

VALID_TRANSITIONS = {
    "queued": {"running"},
    "running": {"completed", "failed"},
    "completed": set(),
    "failed": set(),
}


def create_task(db: Session, task_type: str, user_id: str | None = None, conversation_id: str | None = None) -> Task:
    task = Task(task_type=task_type, status="queued", user_id=user_id, conversation_id=conversation_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info("task_created", task_id=str(task.id), task_type=task_type)
    # publish_task_event("created", str(task.id), task.status)
    return task


def transition_task(db: Session, task_id: str, new_status: str, result: str | None = None, error: str | None = None) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise ValueError(f"Task {task_id} not found")

    if new_status not in VALID_TRANSITIONS.get(task.status, set()):
        raise ValueError(f"Invalid transition: {task.status} -> {new_status}")

    task.status = new_status
    if result is not None:
        task.result = result
    if error is not None:
        task.error = error

    db.commit()
    db.refresh(task)
    logger.info("task_transitioned", task_id=str(task.id), new_status=new_status)

    # event_type = "completed" if new_status in ("completed", "failed") else "updated"
    # publish_task_event(event_type, str(task.id), task.status)

    return task