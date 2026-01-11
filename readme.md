## 📋 Respostas do Desafio

### **1: Consulta SQL**

```sql
SELECT
    u.name        AS user_name,
    u.email       AS user_email,
    r.description AS role_description,
    c.description AS claim_description
FROM users u
INNER JOIN roles r
    ON u.role_id = r.id
LEFT JOIN user_claims uc
    ON uc.user_id = u.id
LEFT JOIN claims c
    ON c.id = uc.claim_id;

Mais detalhes em: App > list-query-users
```

### **2: Query com ORM (SQLAlchemy Expression Language)**

Implementado em: `repositories/user_repository.py`

```python
  def get_user_with_role_and_claims(self, db: Session, user_id: int):
        stmt = (
            select(
                User.name.label("user_name"),
                User.email.label("user_email"),
                Role.description.label("role_description"),
                Claim.description.label("claim_description")
            )
            .join(Role, Role.id == User.role_id)
            .join(UserClaim, UserClaim.user_id == User.id)
            .join(Claim, Claim.id == UserClaim.claim_id)
            .where(User.id == user_id)
        )
```

**Endpoint:** `GET /users/{user_id}/details`

### **3: API REST - Listar Role por ID**

**Endpoint:** `GET /roles/{role_id}`

Implementado em: `api/routes/roles.py`

### **4: API REST - Criar Usuário**

**Endpoint:** `POST /users/`

**Campos obrigatórios:** name, email, role_id  
**Campo opcional:** password (gerado automaticamente se não informado)

Implementado em: `api/routes/users.py` e `services/user_service.py`

**Recursos:**
- ✅ Geração automática de senha segura (12 caracteres)
- ✅ Hash bcrypt da senha
- ✅ Validação de email duplicado
- ✅ Retorno do usuário criado

### **5: Documentação como rodar o projeto e subir em ambiente produtivo**
Informações contidas em: 
App > doc.md

### **6: Resolução de erro**

**Problema:** `AttributeError: module 'core.settings' has no attribute 'WALLET_X_TOKEN_MAX_AGE'`

**Causa raiz:**
Inconsistência de configuração entre ambientes. A variável `WALLET_X_TOKEN_MAX_AGE` existe no ambiente de desenvolvimento, mas **não foi configurada no ambiente de Homologação**.

**Solução:**
Adicionar `WALLET_X_TOKEN_MAX_AGE` nas configurações do ambiente de Homologação (arquivo de configuração, variável de ambiente, etc).


### **7: Code review bot**
Arquivo de review presente em:
challenge > bot > CODE_REVIEW.md


### **8: Padrão de projeto**

**Normalização de serviços de terceiros (e-mail/SMS)**

**Padrões de Projeto recomendados:**

#### **1. Adapter Pattern (essencial)**

**Objetivo:** transformar múltiplas interfaces de fornecedores diferentes (SendGrid, AWS SES, Mailgun, Twilio, etc.) em uma interface comum.

**Benefícios:**
- Código cliente não conhece detalhes de cada fornecedor
- Facilita testes (mocking)
- Permite adicionar novos fornecedores facilmente

---

#### **2. Strategy Pattern (complementar)**

**Objetivo:** escolher dinamicamente qual fornecedor usar em runtime.

**Benefícios:**
- Permite fallback automático se um serviço falhar
- Possibilita alternar fornecedores com base em regras (custo, região, volume)

---

**Arquitetura resumida:**

```
Cliente
   ↓
EmailServiceContext (Strategy)
   ↓
EmailService (Interface comum)
   ↓
├── SendGridAdapter
├── SESAdapter
└── MailgunAdapter
```

**Conclusão:**
- **Adapter** garante normalização das interfaces
- **Strategy** adiciona flexibilidade e fallback
- **Combinação:** mudança fácil de fornecedor, manutenção simplificada e testes isolados