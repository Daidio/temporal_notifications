from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Dict
from temporalio.client import Client
from models import User
import uvicorn

app = FastAPI()

# Almacena campos faltantes por email
missing_requests: Dict[str, List[str]] = {}

class MissingUser(BaseModel):
    email: str
    missing_fields: List[str]

@app.post("/notify_missing")
async def notify_missing(m: MissingUser) -> dict:
    """Almacena los campos faltantes y muestra una forma sencilla para completarlos."""
    missing_requests[m.email] = m.missing_fields
    print(f"Solicitar datos {m.missing_fields} para email={m.email}")
    return {"status": "notification_received"}

@app.get("/pending", response_class=HTMLResponse)
async def pending() -> str:
    """Lista simple de usuarios con datos incompletos."""
    items = [f"<li><a href='/fill/{email}'>{email}</a> - {', '.join(fields)}</li>" for email, fields in missing_requests.items()]
    return "<h3>Pendientes</h3><ul>" + "".join(items) + "</ul>"

@app.get("/fill/{email}", response_class=HTMLResponse)
async def fill_form(email: str) -> str:
    fields = missing_requests.get(email)
    if not fields:
        return "No pending fields for this email"
    inputs = "".join([f"{field}: <input name='{field}'/><br/>" for field in fields])
    form = f"<form method='post' action='/complete/{email}'>{inputs}<button type='submit'>Enviar</button></form>"
    return form

@app.post("/complete/{email}")
async def complete_form(email: str, request: Request) -> RedirectResponse:
    data = await request.form()
    user_data = {**data, 'email': email}
    cli = await Client.connect("localhost:7233")
    handle = cli.get_workflow_handle("user-listener")
    await handle.signal("update", user_data)
    missing_requests.pop(email, None)
    return RedirectResponse("/pending", status_code=303)

@app.post("/complete_user")
async def complete_user(user: User) -> dict:
    """Recibe el usuario completo vía JSON y lo envía al workflow."""
    cli = await Client.connect("localhost:7233")
    handle = cli.get_workflow_handle("user-listener")
    await handle.signal("update", user.__dict__)
    missing_requests.pop(user.email, None)
    return {"status": "submitted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
