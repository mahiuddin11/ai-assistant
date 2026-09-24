import sys
import os

# Pytest / direct script execution setup
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))

from database import SessionLocal
from models import Conversation
from main import create_conversation, send_conversation_message, SendMessageRequest


def test_rag_end_to_end():
    db = SessionLocal()
    try:
        # ১. নতুন কনভারসেশন তৈরি
        conv_res = create_conversation(db)
        conv_id = conv_res["conversation_id"]
        print(f"\n[Test 1] Created fresh conversation: {conv_id}")

        # ২. প্রথম প্রশ্ন: "What is my favorite programming language?" (হিস্ট্রিতে কোনো তথ্য নেই)
        query_1 = "What is my favorite programming language?"
        print(f"\n[Test 1] User query: '{query_1}'")
        res_1 = send_conversation_message(
            conversation_id=conv_id,
            payload=SendMessageRequest(message=query_1),
            db=db,
        )

        print(f"Retrieved memories: {res_1['retrieved_memories']}")
        print(f"LLM Provider: {res_1['provider_used']}")
        print(f"AI Reply: {res_1['reply']}")

        # Assertion: Memory-তে Python রিট্রিভ হয়েছে এবং উত্তরে পাইথনের কথা বলা হয়েছে
        has_python_memory = any("Python" in m for m in res_1["retrieved_memories"])
        has_python_in_reply = "python" in res_1["reply"].lower()

        assert has_python_memory, "RAG failed: Python memory fact was not retrieved from Qdrant!"
        assert has_python_in_reply, f"LLM failed to use RAG context! Reply: {res_1['reply']}"
        print("✅ Test 1 Passed: Semantic memory recalled and accurately used in LLM response!")

        # ৩. দ্বিতীয় প্রশ্ন: "What kind of platform am I building?"
        query_2 = "What kind of platform am I building?"
        print(f"\n[Test 2] User query: '{query_2}'")
        res_2 = send_conversation_message(
            conversation_id=conv_id,
            payload=SendMessageRequest(message=query_2),
            db=db,
        )

        print(f"Retrieved memories: {res_2['retrieved_memories']}")
        print(f"LLM Provider: {res_2['provider_used']}")
        print(f"AI Reply: {res_2['reply']}")

        has_ai_memory = any("AI assistant platform" in m for m in res_2["retrieved_memories"])
        has_ai_in_reply = "ai" in res_2["reply"].lower() or "assistant" in res_2["reply"].lower()

        assert has_ai_memory, "RAG failed: AI assistant platform memory fact was not retrieved!"
        assert has_ai_in_reply, f"LLM failed to use RAG context! Reply: {res_2['reply']}"
        print("✅ Test 2 Passed: Platform memory recalled and accurately used in LLM response!")

        print("\n🎉 ALL RAG END-TO-END VERIFICATION TESTS PASSED SUCCESSFULLY!")

    finally:
        db.close()


if __name__ == "__main__":
    test_rag_end_to_end()
