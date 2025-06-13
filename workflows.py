import collections
from datetime import timedelta
from typing import Deque

from temporalio import workflow
from models import User
from activities import process_user

@workflow.defn
class UserWorkflow:
    def __init__(self) -> None:
        # Cola para usuarios entrantes
        self._queue: Deque[User] = collections.deque()

    @workflow.signal
    async def submit(self, user: User) -> None:
        """Señal para encolar un nuevo User."""
        self._queue.append(user)

    @workflow.run
    async def run(self) -> None:
        """Loop infinito que procesa la cola de usuarios."""
        while True:
            await workflow.wait_condition(lambda: len(self._queue) > 0)
            next_user = self._queue.popleft()
            await workflow.execute_activity(
                process_user,
                next_user,
                schedule_to_close_timeout=timedelta(seconds=30),
            )

            