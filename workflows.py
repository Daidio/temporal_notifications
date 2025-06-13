import collections
from datetime import timedelta
from typing import Deque, Dict, List

from temporalio import workflow
from models import User
from activities import process_user, notify_missing_data

REQUIRED_FIELDS = [
    "first_name",
    "rut",
    "address",
    "region",
    "commune",
    "annual_payment",
    "start_date",
    "end_date",
    "type_payment_source",
    "amount",
    "plan_name",
    "es_empresa",
    "email",
    "created_at",
]

@workflow.defn
class UserWorkflow:
    def __init__(self) -> None:
        # Cola para usuarios entrantes
        self._queue: Deque[User] = collections.deque()
        # Futures que esperan actualizaciones por email
        self._waiting: Dict[str, workflow.Future] = {}

    @workflow.signal
    async def submit(self, user_data: dict) -> None:
        """Señal para encolar un nuevo User."""
        # Convertir los datos recibidos en una instancia de User. Recibimos un
        # diccionario para evitar problemas de deserialización de dataclasses
        # cuando la señal proviene de distintos entornos de Python.
        self._queue.append(User(**user_data))

    @workflow.signal
    async def update(self, user_data: dict) -> None:
        """Actualiza datos de un usuario en espera."""
        email = user_data.get("email")
        fut = self._waiting.get(email)
        if fut:
            fut.set_result(user_data)
        else:
            self._queue.append(User(**user_data))

    def _missing_fields(self, user: User) -> List[str]:
        missing = []
        for field in REQUIRED_FIELDS:
            value = getattr(user, field)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(field)
        return missing

    @workflow.run
    async def run(self) -> None:
        """Loop infinito que procesa la cola de usuarios."""
        while True:
            await workflow.wait_condition(lambda: len(self._queue) > 0)
            user = self._queue.popleft()
            while True:
                missing = self._missing_fields(user)
                if missing:
                    await workflow.execute_activity(
                        notify_missing_data,
                        user,
                        missing,
                        schedule_to_close_timeout=timedelta(seconds=30),
                    )
                    fut = workflow.Future()
                    self._waiting[user.email] = fut
                    user_data = await fut
                    self._waiting.pop(user.email, None)
                    for k, v in user_data.items():
                        if k in REQUIRED_FIELDS or hasattr(user, k):
                            setattr(user, k, v)
                    continue
                await workflow.execute_activity(
                    process_user,
                    user,
                    schedule_to_close_timeout=timedelta(seconds=30),
                )
                break

