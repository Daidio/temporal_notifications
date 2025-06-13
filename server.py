from fastapi import FastAPI, Header, HTTPException
import uvicorn
from temporalio.client import Client
from temporalio.exceptions import WorkflowAlreadyStartedError
from models import User, UserModel
import config
from workflows import UserWorkflow
from datetime import datetime

app = FastAPI()
client: Client

@app.on_event("startup")
async def startup_event() -> None:
    global client
    # Conectar a Temporal
    client = await Client.connect("localhost:7233")
    try:
        # Iniciar el workflow listener si no existe aún
        await client.start_workflow(
            UserWorkflow.run,
            id="user-listener",
            task_queue="user-queue"
        )
        print("[Server] Workflow 'user-listener' iniciado.")
    except WorkflowAlreadyStartedError:
        pass

@app.post("/users")
async def receive_user(
    user_payload: UserModel,
    x_api_key: str = Header(..., alias="X-API-KEY")
) -> dict:
    # Validar API key
    if x_api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Convertir el modelo a diccionario
    user_dict = user_payload.model_dump()

    # Asegurarnos de que created_at sea un string ISO
    if not isinstance(user_dict.get('created_at'), str):
        user_dict['created_at'] = datetime.now().isoformat()

    # Convertir payload a dataclass
    user = User(**user_dict)

    # Obtener handle al workflow en ejecución
    handle = client.get_workflow_handle("user-listener")
    # Enviar señal 'submit' al workflow
    await handle.signal("submit", user)
    return {"status": "submitted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
