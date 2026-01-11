from fastapi import FastAPI
from core.database import Base, engine, SessionLocal
from core.seed import seed_roles
from api.routes import users, roles

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()

app.include_router(users.router)
app.include_router(roles.router)
