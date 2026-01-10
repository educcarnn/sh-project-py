from fastapi import FastAPI
from app.api.routes import users, roles

app = FastAPI(title="Shipay Back-end Challenge")

app.include_router(users.router)
app.include_router(roles.router)
