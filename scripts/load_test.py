from locust import HttpUser, task, between


class ChatUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8002"

    def on_start(self):
        response = self.client.post("/v1/conversations")
        self.conversation_id = response.json()["conversation_id"]

    @task
    def send_message(self):
        self.client.post(
            f"/v1/conversations/{self.conversation_id}/messages",
            json={"message": "Hello, how are you?"},
        )