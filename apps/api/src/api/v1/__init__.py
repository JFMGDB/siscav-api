"""API v1 - Sistema de Controle de Acesso Veicular.

Este módulo contém toda a implementação da API v1, seguindo o padrão MVC
com separação clara de responsabilidades (SOLID, DRY).

Estrutura:
- controllers/: Lógica de negócio (Service Layer)
- repositories/: Acesso a dados (Data Access Layer)
- endpoints/: Roteamento HTTP (Views)
- models/: Modelos SQLAlchemy
- schemas/: Schemas Pydantic
- core/: Configurações e segurança
- db/: Setup do banco de dados
- utils/: Utilitários compartilhados
"""

__version__ = "1.0.0"

