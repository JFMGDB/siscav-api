# Documentação de Requisitos

Esta pasta contém a especificação de requisitos do projeto SISCAV.

## Índice

1. [Especificação de Projeto](./01-especificacao-projeto.md)
   - Visão geral e justificativa do projeto
   - Objetivos de negócio
   - Requisitos funcionais (RF)
   - Requisitos não funcionais (RNF)
   - Arquitetura do sistema proposta
   - Análise e seleção de tecnologias
   - Entregáveis e fases do projeto

## Descrição

A especificação de projeto define:

- **Problema**: Controle de acesso veicular manual/semi-automatizado com ineficiências
- **Solução**: Sistema automatizado usando IoT e IA para reconhecimento de placas
- **Objetivos**: Segurança, eficiência operacional, conveniência e geração de dados estratégicos

## Requisitos Funcionais Principais

- RF-001 a RF-003: Módulo de Reconhecimento de Placas (ALPR)
- RF-004 a RF-006: Módulo de Controle de Acesso
- RF-007 a RF-010: Painel de Administração

## Requisitos Não Funcionais Principais

- RNF-001: Latência de processamento (máximo 5 segundos)
- RNF-002: Precisão do ALPR (95% diurno, 85% noturno)
- RNF-003: Disponibilidade do sistema (99.5%)
- RNF-005: Comunicação criptografada (TLS)
- RNF-006: Segurança do painel (OWASP Top 10)
- RNF-007: Interface intuitiva
- RNF-008: Código modular e documentado

## Tecnologias Selecionadas

- **ALPR**: EasyOCR (Deep Learning)
- **Backend**: FastAPI (Python)
- **Banco de Dados**: PostgreSQL
- **Frontend**: React com MUI

