# Solução Rápida: Erro de Compilação do NumPy no Python 3.14

## Problema

Ao tentar instalar dependências, você encontra o erro:

```
fatal error C1083: Não é possível abrir arquivo incluir: 'stdalign.h': No such file or directory
error: metadata-generation-failed
```

## Causa

Python 3.14 (e 3.13) são muito recentes e não têm wheels pré-compilados do NumPy disponíveis. O pip tenta compilar do código-fonte e falha.

## Solução Rápida (3 passos)

### Passo 1: Execute o Script de Correção

```powershell
cd apps/iot-device
.\scripts\fix_numpy_install.ps1
```

### Passo 2: Escolha a Opção 1 (Python 3.12)

O script detectará o problema e oferecerá 3 opções. Escolha a **Opção 1** para usar Python 3.12.

### Passo 3: Siga as Instruções

O script fornecerá comandos específicos. Geralmente:

```powershell
# Se Python 3.12 já estiver instalado
py -3.12 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install --only-binary :all: numpy
python -m pip install opencv-python requests easyocr
```

## Solução Alternativa: Script de Instalação Automática

```powershell
cd apps/iot-device
.\scripts\install_dependencies.ps1
```

Este script detecta automaticamente problemas e instala todas as dependências.

## Se Python 3.12 Não Estiver Instalado

1. Baixe Python 3.12: https://www.python.org/downloads/
2. Instale (marque "Add Python to PATH")
3. Execute os scripts acima novamente

## Verificação

Após instalação, verifique:

```powershell
python -c "import numpy, cv2, easyocr, requests; print('OK!')"
```

## Mais Informações

- Guia completo: `docs/TROUBLESHOOTING_INSTALACAO.md`
- Guia de instalação: `apps/iot-device/INSTALACAO.md`

