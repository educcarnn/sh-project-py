
---

## 🚀 Como Executar Localmente

### Pré-requisitos:
- Docker
- Docker Compose

### Passos:

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd sh-project-py/app

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env se necessário (opcional para desenvolvimento local)

# 3. Iniciar containers
docker-compose up --build

# 4. Acessar a API
# http://localhost:8000/docs
```

### Configuração do Ambiente (.env):

O arquivo `.env` contém as configurações do banco de dados e da aplicação:

```env
# Database Configuration
POSTGRES_DB=shipay_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Application Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/shipay_db
```

**Nota:** Para desenvolvimento local, as configurações padrão já funcionam. Altere apenas se necessário.

### Executar Testes:

```bash
# Com containers em execução
docker-compose exec api pytest --cov=. --cov-report=term-missing

# Testes específicos
docker-compose exec api pytest tests/test_repositories/ -v
```

### Parar containers:

```bash
docker-compose down
```

---

## 🚀 Deploy em Produção (AWS Fargate)

### Arquitetura Recomendada:

```
Internet → ALB → ECS Fargate (API FastAPI) → RDS PostgreSQL
                                 ↓
                           AWS Secrets Manager
```

### Pré-requisitos AWS:

- Conta AWS com permissões para ECS, ECR, RDS, VPC e ALB
- AWS CLI configurado
- Terraform ou Console AWS para criação de recursos

---

### **Criar repositório ECR**

```bash
aws ecr create-repository --repository-name shipay-api --region us-east-1
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com
```

---

### **Build e Push da Imagem Docker**

```bash
docker build -t shipay-api:latest .
docker tag shipay-api:latest <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/shipay-api:latest
docker push <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/shipay-api:latest
```

---

### **Criar RDS PostgreSQL**

**Configuração:**
- Engine: PostgreSQL 15
- Classe: db.t3.small (produção mínima)
- Storage: 20 GB SSD
- Multi-AZ recomendado

**Via AWS CLI:**

```bash
aws rds create-db-instance \
  --db-instance-identifier shipay-db-prod \
  --db-instance-class db.t3.small \
  --engine postgres \
  --master-username postgres \
  --master-user-password <senha-segura> \
  --allocated-storage 20 \
  --vpc-security-group-ids <sg-id> \
  --db-subnet-group-name <subnet-group> \
  --publicly-accessible false \
  --backup-retention-period 7
```

---

### **Armazenar Credenciais no Secrets Manager**

```bash
aws secretsmanager create-secret \
  --name shipay-db-credentials \
  --description "Database credentials for Shipay API" \
  --secret-string '{
    "username":"postgres",
    "password":"<senha-segura>",
    "host":"<rds-endpoint>",
    "port":"5432",
    "dbname":"shipay_db"
  }'
```

---

### **Task Definition ECS**

**Características:**
- Configura container FastAPI com porta 8000
- Usa secrets do Secrets Manager para a base de dados
- Logs no CloudWatch
- Health check em `/docs`

Criar arquivo `task-definition.json`:

```json
{
  "family": "shipay-api-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "shipay-api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/shipay-api:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:shipay-db-credentials:DATABASE_URL::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/shipay-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/docs || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

**Registrar:**

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

---

### **Criar Cluster ECS**

```bash
aws ecs create-cluster --cluster-name shipay-cluster --region us-east-1
```

---

### **Criar Serviço ECS Fargate**

```bash
aws ecs create-service \
  --cluster shipay-cluster \
  --service-name shipay-api-service \
  --task-definition shipay-api-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<subnet-1>,<subnet-2>],securityGroups=[<sg-id>],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=<target-group-arn>,containerName=shipay-api,containerPort=8000" \
  --health-check-grace-period-seconds 60
```



---

### **🔄 CI/CD com GitHub Actions (Opcional)**

Criar `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS ECS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: shipay-api
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster shipay-cluster \
            --service shipay-api-service \
            --force-new-deployment
```




---

## 📚 Documentação da API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🗄️ Estrutura do Banco

As tabelas são criadas automaticamente ao iniciar o Docker:
- `roles` - Papéis de usuários
- `claims` - Permissões/Claims
- `users` - Usuários do sistema
- `user_claims` - Relação muitos-para-muitos entre users e claims

---

## 📦 Tecnologias Utilizadas

- **Python 3.11**
- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **PostgreSQL 15** - Banco de dado
- **Pydantic v2** - Validação de dados
- **Passlib + Bcrypt** - Hash de senhas
- **Pytest** - Framework de testes
- **Pytest-cov** - Cobertura de código
- **Docker** - Containerização
