import httpx

AUTH_URL = "http://localhost:8001"
CONV_URL = "http://localhost:8002"


def run_e2e_test():
    print("1. Testing login...")
    login_res = httpx.post(f"{AUTH_URL}/v1/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123",
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    print("   ✅ Login successful")

    print("2. Creating conversation...")
    conv_res = httpx.post(f"{CONV_URL}/v1/conversations")
    assert conv_res.status_code == 200
    conversation_id = conv_res.json()["conversation_id"]
    print(f"   ✅ Conversation created: {conversation_id}")

    print("3. Sending message...")
    msg_res = httpx.post(
        f"{CONV_URL}/v1/conversations/{conversation_id}/messages",
        json={"message": "My favorite color is blue. Remember that."},
        timeout=30.0,
    )
    assert msg_res.status_code == 200, f"Message failed: {msg_res.text}"
    print(f"   ✅ Got reply via {msg_res.json()['provider_used']}")

    print("4. Sending follow-up message (testing working memory)...")
    followup_res = httpx.post(
        f"{CONV_URL}/v1/conversations/{conversation_id}/messages",
        json={"message": "What is my favorite color?"},
        timeout=30.0,
    )
    assert followup_res.status_code == 200
    reply = followup_res.json()["reply"].lower()
    assert "blue" in reply, f"Memory test failed — 'blue' not in reply: {reply}"
    print("   ✅ Working memory confirmed (recalled 'blue')")

    print("5. Verifying persistent history...")
    history_res = httpx.get(f"{CONV_URL}/v1/conversations/{conversation_id}/history")
    assert history_res.status_code == 200
    messages = history_res.json()["messages"]
    assert len(messages) == 4, f"Expected 4 messages, got {len(messages)}"
    print(f"   ✅ History persisted correctly ({len(messages)} messages)")

    print("\n🎉 ALL E2E TESTS PASSED")


if __name__ == "__main__":
    run_e2e_test()