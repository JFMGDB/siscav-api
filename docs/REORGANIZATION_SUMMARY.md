# Resumo da Reorganização da Documentação

## Data: 06 de dezembro de 2025

## Objetivo

Reorganizar a documentação do projeto SISCAV para melhorar a organização, reduzir redundâncias e manter a documentação próxima ao código-fonte de cada aplicação.

## Decisões Tomadas

### 1. Estrutura por Aplicação

**Decisão**: Criar pastas `docs/` dentro de cada aplicação (`apps/api/` e `apps/iot-device/`) para manter a documentação próxima ao código-fonte.

**Justificativa**:
- Facilita localização da documentação relevante
- Reduz navegação entre pastas distantes
- Alinha com princípios de organização de código (documentação próxima ao código)
- Melhora a manutenibilidade

### 2. Documentos Movidos para `apps/iot-device/docs/`

#### Documentos Principais
- `INSTALACAO.md` → `apps/iot-device/docs/installation.md`
- `docs/getting-started/installation-guide.md` → `apps/iot-device/docs/demo-guide.md`
- `docs/operations/installation-troubleshooting.md` → `apps/iot-device/docs/troubleshooting.md`
- `docs/iot/iot-device-refactoring.md` → `apps/iot-device/docs/refactoring.md`
- `docs/iot/iot-device-summary.md` → `apps/iot-device/docs/README.md`
- `docs/operations/demo-evaluation-guide.md` → `apps/iot-device/docs/demo-evaluation-guide.md`

#### Hardware/Arduino
- `arduino/README.md` → `apps/iot-device/docs/hardware/arduino.md`
- `docs/hardware/arduino-project-definition.md` → `apps/iot-device/docs/hardware/project-definition.md`
- `docs/hardware/assembly-demo-guide.md` → `apps/iot-device/docs/hardware/assembly-guide.md`

#### Documentos Arquivados
- `INSTALAR_PYTHON312.md` → `apps/iot-device/docs/archive/python312-installation.md`
- `docs/operations/python312-regression.md` → `apps/iot-device/docs/archive/python312-regression.md`
- `docs/operations/python314-final-solution.md` → `apps/iot-device/docs/archive/python314-final-solution.md`
- `docs/operations/numpy-error-solution.md` → `apps/iot-device/docs/archive/numpy-error-solution.md`

### 3. Documentos Movidos para `apps/api/docs/`

#### Documentos Principais
- `docs/api/technical-documentation.md` → `apps/api/docs/technical-documentation.md`

#### Database
- `docs/database/data-model.md` → `apps/api/docs/database/data-model.md`
- `docs/database/supabase-migration.md` → `apps/api/docs/database/supabase-migration.md`

### 4. Documentos Excluídos

#### Duplicados Identificados
- `docs/operations/demo-guide.md` - Duplicado idêntico de `demo-evaluation-guide.md` (mesmo hash SHA256)
  - Excluído após verificação de duplicação

### 5. Documentos Mantidos em `/docs`

Os seguintes documentos permanecem em `/docs` por serem de escopo geral do projeto:

- **Architecture**: Documentação arquitetural geral do sistema
- **Development**: Padrões de código e convenções gerais
- **Requirements**: Especificações funcionais e não funcionais
- **Project Management**: Gerenciamento de projeto
- **Presentation**: Materiais de apresentação
- **Assets**: Recursos visuais
- **Archive**: Documentos históricos gerais

## Estrutura Final

```
siscav-api/
├── apps/
│   ├── api/
│   │   └── docs/
│   │       ├── README.md
│   │       ├── technical-documentation.md
│   │       ├── database/
│   │       │   ├── data-model.md
│   │       │   └── supabase-migration.md
│   │       └── archive/
│   │           └── README.md
│   └── iot-device/
│       └── docs/
│           ├── README.md
│           ├── installation.md
│           ├── troubleshooting.md
│           ├── refactoring.md
│           ├── demo-guide.md
│           ├── demo-evaluation-guide.md
│           ├── hardware/
│           │   ├── arduino.md
│           │   ├── project-definition.md
│           │   └── assembly-guide.md
│           └── archive/
│               ├── README.md
│               ├── python312-installation.md
│               ├── python312-regression.md
│               ├── python314-final-solution.md
│               └── numpy-error-solution.md
└── docs/
    ├── README.md (atualizado com referências)
    ├── architecture/
    ├── development/
    ├── requirements/
    ├── project-management/
    ├── presentation/
    └── assets/
```

## Referências Atualizadas

Todos os READMEs foram atualizados para refletir as novas localizações:

- `docs/README.md` - Índice principal atualizado
- `docs/api/README.md` - Referências atualizadas
- `docs/database/README.md` - Referências atualizadas
- `docs/iot/README.md` - Nota sobre reorganização
- `docs/hardware/README.md` - Nota sobre reorganização
- `docs/operations/README.md` - Nota sobre reorganização
- `docs/getting-started/README.md` - Referências atualizadas
- `README.md` (raiz) - Referências atualizadas

## Benefícios

1. **Organização Melhorada**: Documentação próxima ao código-fonte
2. **Redução de Redundâncias**: Documentos duplicados identificados e removidos
3. **Manutenibilidade**: Estrutura mais clara e fácil de manter
4. **Navegação Simplificada**: Menos saltos entre pastas distantes
5. **Histórico Preservado**: Documentos obsoletos arquivados, não excluídos

## Próximos Passos Recomendados

1. Revisar referências em documentos de código (comentários, docstrings)
2. Atualizar links em apresentações se necessário
3. Verificar se há scripts ou ferramentas que referenciam caminhos antigos
4. Considerar criar um script de migração para atualizar referências automaticamente

## Notas Importantes

- Documentos arquivados são mantidos apenas para referência histórica
- Sempre consulte a documentação principal, não os documentos arquivados
- READMEs em cada pasta `docs/` fornecem índices atualizados
- A estrutura `/docs` ainda contém documentação de escopo geral do projeto

