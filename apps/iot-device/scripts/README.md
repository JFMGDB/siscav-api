# Scripts Auxiliares - Dispositivo IoT

Este diretório contém scripts auxiliares para instalação, análise e teste do sistema.

## Scripts Disponíveis

### setup_python312.ps1 (Windows) - RECOMENDADO

Script completo para configurar ambiente Python 3.12 e instalar todas as dependências.

**Uso:**
```powershell
cd apps/iot-device
.\scripts\setup_python312.ps1
```

**Recursos:**
- Detecta se Python 3.12 está instalado
- Oferece instalação via winget
- Cria ambiente virtual com Python 3.12
- Instala todas as dependências automaticamente
- Verifica instalação completa

### install_dependencies.ps1 (Windows)

Script PowerShell para instalação automática de dependências com detecção de problemas.

**Uso:**
```powershell
cd apps/iot-device
.\scripts\install_dependencies.ps1
```

**Recursos:**
- Detecta versão do Python
- Alerta sobre Python 3.13+
- Força instalação de wheels pré-compilados quando necessário
- Verifica todas as dependências após instalação
- Fornece instruções claras em caso de erro

**Opções:**
```powershell
# Forçar uso de wheels pré-compilados
.\scripts\install_dependencies.ps1 -ForceWheel
```

### fix_numpy_install.ps1 (Windows)

Script para corrigir problemas específicos de instalação do NumPy no Python 3.14.

**Uso:**
```powershell
cd apps/iot-device
.\scripts\fix_numpy_install.ps1
```

**Oferece 3 soluções:**
1. Usar Python 3.12 (recomendado)
2. Tentar instalar wheel pré-compilado
3. Usar Conda

### collect_metrics.py

Analisa logs do sistema e gera relatório de desempenho.

**Uso:**
```bash
# Análise básica
python scripts/collect_metrics.py logs/siscav.log

# Salvar relatório em arquivo
python scripts/collect_metrics.py logs/siscav.log -o relatorio.txt

# Saída em JSON
python scripts/collect_metrics.py logs/siscav.log --json
```

**Métricas Extraídas:**
- Total de detecções
- Taxa de sucesso de OCR
- Taxa de sucesso da API
- Taxa de autorização
- Placas únicas detectadas
- Detecções por minuto
- Erros encontrados

## Exemplos de Uso

### Análise após Demonstração

```bash
# Executar sistema e salvar logs
python main.py > logs/demo_$(date +%Y%m%d_%H%M%S).log 2>&1

# Analisar logs
python scripts/collect_metrics.py logs/demo_*.log -o relatorio_demo.txt
```

### Análise Comparativa

```bash
# Gerar relatórios JSON para múltiplas sessões
for log in logs/test_*.log; do
    python scripts/collect_metrics.py "$log" --json > "${log%.log}_metrics.json"
done
```

