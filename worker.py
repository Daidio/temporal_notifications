import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import UserWorkflow
from activities import process_user, notify_missing_data

async def main() -> None:
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="user-queue",
        workflows=[UserWorkflow],
        activities=[process_user, notify_missing_data],
    )
    print("[Worker] Listening on 'user-queue'")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())