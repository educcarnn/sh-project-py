import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from core.database import Base
from models.role import Role
from tests.conftest import engine, TestingSessionLocal


def override_get_db():
    """Override da dependência get_db para usar banco de teste"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """Cliente de teste da API"""
    from api.routes.roles import get_db
    
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_with_role(client):
    """Cria um role no banco de teste"""
    db = TestingSessionLocal()
    try:
        role = Role(id=1, description="Admin")
        db.add(role)
        db.commit()
        db.refresh(role)
        yield db, role
    finally:
        db.close()


class TestRoleRoutes:

    def test_get_role_by_id_success(self, client, db_with_role):
        """Testa busca de role por ID com sucesso"""
        db, role = db_with_role
        
        response = client.get(f"/roles/{role.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == role.id
        assert data["description"] == "Admin"

    def test_get_role_by_id_not_found(self, client, db_with_role):
        """Testa busca de role inexistente"""
        response = client.get("/roles/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
