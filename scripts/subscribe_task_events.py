import asyncio
import nats


async def main():
    nc = await nats.connect("nats://localhost:4222")

    async def handler(msg):
        print(f"📩 {msg.subject}: {msg.data.decode()}")

    await nc.subscribe("task.*", cb=handler)
    print("👂 Listening for task.* events... (Ctrl+C to stop)")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())