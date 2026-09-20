from database import SessionLocal
from semantic_memory import store_memory, retrieve_relevant_memories

db = SessionLocal()
store_memory(db, "The user's favorite programming language is Python.")
store_memory(db, "The user is building an AI assistant platform.")
db.close()

results = retrieve_relevant_memories("What does the user like to code in?")
print("Retrieved:", results)
