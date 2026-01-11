import pytest
from models.role import Role
from repositories.role_repository import RoleRepository


class TestRoleRepository:

    def test_create_role(self, db):
        """Testa criação de role"""
        repository = RoleRepository()
        role = Role(description="Test Role")
        
        created_role = repository.create(db, role)
        
        assert created_role.id is not None
        assert created_role.description == "Test Role"

    def test_get_by_id(self, db):
        """Testa busca de role por ID"""
        repository = RoleRepository()
        role = Role(description="Admin")
        created_role = repository.create(db, role)
        
        found_role = repository.get_by_id(db, created_role.id)
        
        assert found_role is not None
        assert found_role.id == created_role.id
        assert found_role.description == "Admin"

    def test_get_by_description(self, db):
        """Testa busca de role por description"""
        repository = RoleRepository()
        role = Role(description="Manager")
        repository.create(db, role)
        
        found_role = repository.get_by_description(db, "Manager")
        
        assert found_role is not None
        assert found_role.description == "Manager"

    def test_get_by_description_not_found(self, db):
        """Testa busca de role inexistente"""
        repository = RoleRepository()
        
        found_role = repository.get_by_description(db, "NonExistent")
        
        assert found_role is None
