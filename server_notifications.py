from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from temporalio.client import Client
from models import User
import uvicorn

app = FastAPI()

class MissingUser(BaseModel):
    email: str
    missing_fields: List[str]

@app.post("/notify_missing")
async def notify_missing(m: MissingUser) -> dict:
    # Aquí implementas email/UI para solicitar datos faltantes
    print(f"Solicitar datos {m.missing_fields} para email={m.email}")
    return {"status": "notification_sent"}

@app.post("/complete_user")
async def complete_user(user: User) -> dict:
    # Envía datos completos al workflow
    cli = await Client.connect("localhost:7233")
    handle = cli.get_workflow_handle("user-listener")
    await handle.signal("update", user)
    return {"status": "submitted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)