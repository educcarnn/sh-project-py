import pytest
from unittest.mock import Mock
from datetime import date
from models.user import User
from models.role import Role
from repositories.user_repository import UserRepository
from schemas.user_schema import UserCreate
from services.user_service import UserService


class TestUserService:

    @pytest.fixture
    def mock_repository(self):
        """Mock do UserRepository"""
        return Mock(spec=UserRepository)

    @pytest.fixture
    def service(self, mock_repository):
        """Instancia UserService com repository mockado"""
        return UserService(mock_repository)

    def test_generate_password(self, service):
        """Testa geração de senha aleatória"""
        password = service._generate_password()
        
        assert password is not None
        assert len(password) > 0
        assert isinstance(password, str)

    def test_hash_password(self, service):
        """Testa hash de senha"""
        password = "test_password_123"
        
        hashed = service._hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")

    def test_hash_password_truncates_long_passwords(self, service):
        """Testa truncamento de senhas longas (>72 bytes)"""
        long_password = "a" * 100
        
        hashed = service._hash_password(long_password)
        
        assert hashed is not None
        assert hashed.startswith("$2b$")

    def test_create_user_with_password(self, service, mock_repository, db):
        """Testa criação de usuário com senha fornecida"""
        user_data = UserCreate(
            name="Test User",
            email="test@example.com",
            role_id=1,
            password="my_password"
        )
        
        expected_user = User(
            id=1,
            name="Test User",
            email="test@example.com",
            role_id=1,
            password="hashed",
            created_at=date.today()
        )
        mock_repository.create.return_value = expected_user
        
        result = service.create_user(db, user_data)
        
        assert mock_repository.create.called
        created_user_arg = mock_repository.create.call_args[0][1]
        assert created_user_arg.name == "Test User"
        assert created_user_arg.email == "test@example.com"
        assert created_user_arg.password != "my_password" 

    def test_create_user_without_password(self, service, mock_repository, db):
        """Testa criação de usuário sem senha (auto-gerada)"""
        user_data = UserCreate(
            name="Test User",
            email="test@example.com",
            role_id=1
        )
        
        expected_user = User(
            id=1,
            name="Test User",
            email="test@example.com",
            role_id=1,
            password="hashed",
            created_at=date.today()
        )
        mock_repository.create.return_value = expected_user
        
        result = service.create_user(db, user_data)
        
        assert mock_repository.create.called
        created_user_arg = mock_repository.create.call_args[0][1]
        assert created_user_arg.password is not None
        assert len(created_user_arg.password) > 0

    def test_create_user_sets_created_at(self, service, mock_repository, db):
        """Testa se created_at é definido na criação"""
        user_data = UserCreate(
            name="Test User",
            email="test@example.com",
            role_id=1
        )
        
        expected_user = User(
            id=1,
            name="Test User",
            email="test@example.com",
            role_id=1,
            password="hashed",
            created_at=date.today()
        )
        mock_repository.create.return_value = expected_user
        
        result = service.create_user(db, user_data)
        
        created_user_arg = mock_repository.create.call_args[0][1]
        assert created_user_arg.created_at == date.today()
        assert created_user_arg.updated_at is None
