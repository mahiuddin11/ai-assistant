import asyncio
from nats.aio.client import Client as NATS


async def main():
    nc = NATS()

    # NATS সার্ভারের সাথে কানেক্ট করা
    await nc.connect("nats://localhost:4222")
    print("✅ Connected to NATS server")

    received_messages = []

    # একটা subscriber বানানো - "foundation.test" টপিক শোনার জন্য
    async def message_handler(msg):
        subject = msg.subject
        data = msg.data.decode()
        print(f"📩 Received on '{subject}': {data}")
        received_messages.append(data)

    await nc.subscribe("foundation.test", cb=message_handler)
    print("👂 Subscribed to 'foundation.test'")

    # একটু অপেক্ষা করা যাতে subscription রেডি হয়
    await asyncio.sleep(1)

    # একটা মেসেজ পাবলিশ করা
    test_message = "Hello from AI Assistant Foundation phase!"
    await nc.publish("foundation.test", test_message.encode())
    print(f"📤 Published: {test_message}")

    # মেসেজ রিসিভ হওয়ার জন্য একটু অপেক্ষা
    await asyncio.sleep(1)

    # যাচাই করা
    if received_messages:
        print("\n✅ SMOKE TEST PASSED — publish/subscribe working correctly")
    else:
        print("\n❌ SMOKE TEST FAILED — no message received")

    await nc.close()


if __name__ == "__main__":
    asyncio.run(main())