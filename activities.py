import asyncio
from temporalio import activity
from models import User

@activity.defn
async def process_user(user: User) -> None:
    """Lógica principal de negocio: DB, emails, tercero, etc."""
    print(f"[Activity] Procesando: {user.first_name} {user.last_name or ''}")
    await asyncio.sleep(1)

@activity.defn
async def notify_missing_data(user: User, missing_fields: list[str]) -> None:
    """
    Notifica a `server_notifications` los campos faltantes.
    """
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:9000/notify_missing",
                json={
                    "email": user.email,
                    "missing_fields": missing_fields
                },
                timeout=5.0
            )
            response.raise_for_status()
            print(f"[Activity] Notificación enviada para {user.email}")
    except Exception as e:
        print(f"[Activity] Error al notificar: {str(e)}")
        raise