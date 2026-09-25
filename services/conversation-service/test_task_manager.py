from database import SessionLocal
from task_manager import create_task, transition_task

db = SessionLocal()

task = create_task(db, task_type="chat_message")
print("Created:", task.id, task.status)

task = transition_task(db, str(task.id), "running")
print("Transitioned to:", task.status)

task = transition_task(db, str(task.id), "completed", result="Test successful")
print("Transitioned to:", task.status, "| result:", task.result)

try:
    transition_task(db, str(task.id), "running")
except ValueError as e:
    print("Correctly rejected invalid transition:", e)

db.close()