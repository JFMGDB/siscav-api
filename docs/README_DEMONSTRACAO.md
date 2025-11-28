# README - Demonstração do Sistema SISCAV

## Início Rápido

Para uma demonstração rápida, consulte: **[GUIA_RAPIDO_DEMONSTRACAO.md](GUIA_RAPIDO_DEMONSTRACAO.md)**

**Nota Importante**: A demonstração utilizará a **câmera integrada do laptop**. Consulte **[NOTA_CAMERA_LAPTOP.md](NOTA_CAMERA_LAPTOP.md)** para informações sobre configuração e permissões.

## Documentação Completa

### Para Demonstração

1. **[GUIA_RAPIDO_DEMONSTRACAO.md](GUIA_RAPIDO_DEMONSTRACAO.md)** - Guia rápido (5 minutos)
2. **[DEMONSTRACAO_COMPLETA.md](DEMONSTRACAO_COMPLETA.md)** - Guia completo e detalhado
3. **[NOTA_CAMERA_LAPTOP.md](NOTA_CAMERA_LAPTOP.md)** - Informações sobre uso da câmera do laptop

### Para Entendimento Técnico

3. **[ESTADO_ATUAL_E_DECISOES.md](ESTADO_ATUAL_E_DECISOES.md)** - Estado atual e decisões técnicas
4. **[RESUMO_ANALISE_E_PREPARACAO.md](RESUMO_ANALISE_E_PREPARACAO.md)** - Resumo da análise realizada
5. **[RESUMO_FINAL_PREPARACAO.md](RESUMO_FINAL_PREPARACAO.md)** - Resumo final do trabalho

## Scripts de Apoio

### Verificação Pré-Demonstração

```bash
cd apps/iot-device
python scripts/verify_demo_setup.py
```

Este script verifica:
- Versão do Python
- Dependências instaladas
- Câmera disponível
- Conexão com API
- Configurações de ambiente

### Coleta de Métricas

```bash
cd apps/iot-device
python scripts/collect_metrics.py logs/demo.log
```

## Estrutura do Projeto

```
siscav-api/
├── apps/
│   ├── api/src/          # API Backend (FastAPI)
│   └── iot-device/       # Dispositivo IoT
│       ├── main.py       # Aplicação principal
│       ├── services/     # Serviços (camera, ocr, etc)
│       └── scripts/      # Scripts de apoio
├── docs/                 # Documentação
│   ├── DEMONSTRACAO_COMPLETA.md
│   ├── GUIA_RAPIDO_DEMONSTRACAO.md
│   └── ...
└── README.md
```

## Status Atual

- ✅ API Backend: Funcional
- ✅ Dispositivo IoT: Funcional
- ✅ Detecção de Placas: Implementada
- ✅ OCR: Implementado (EasyOCR)
- ✅ Integração API: Funcional
- ✅ Documentação: Completa
- ✅ Scripts de Apoio: Criados

## Próximos Passos

1. Instalar EasyOCR (se ainda não instalado)
2. Iniciar API Backend
3. Executar dispositivo IoT
4. Realizar demonstração

## Suporte

Para problemas ou dúvidas:
1. Consultar documentação completa
2. Executar script de verificação
3. Verificar logs do sistema
4. Consultar equipe de desenvolvimento

