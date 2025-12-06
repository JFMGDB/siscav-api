# Regressão para Python 3.12 - Concluída

## Resumo

A regressão do ambiente de desenvolvimento do dispositivo IoT de Python 3.14 para Python 3.12 foi concluída com sucesso. Todas as dependências foram instaladas e verificadas.

## Motivação

Python 3.14 é muito recente e muitas bibliotecas científicas (especialmente `scikit-image`, dependência do EasyOCR) ainda não possuem wheels pré-compilados para esta versão, causando erros de compilação durante a instalação.

Python 3.12 possui suporte completo de todas as dependências necessárias, incluindo:
- NumPy
- OpenCV
- EasyOCR (e suas dependências: scikit-image, torch, etc.)
- Requests

## Processo Executado

### 1. Instalação do Python 3.12

Python 3.12.10 foi instalado via winget:

```powershell
winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
```

### 2. Criação do Ambiente Virtual

Ambiente virtual recriado com Python 3.12:

```powershell
cd apps/iot-device
py -3.12 -m venv venv
```

### 3. Instalação de Dependências

Todas as dependências foram instaladas com sucesso:

```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install "numpy>=1.24.0,<2.0.0" "opencv-python>=4.8.0" "requests>=2.31.0"
.\venv\Scripts\python.exe -m pip install "easyocr>=1.7.0"
```

## Verificação Final

Todas as dependências foram verificadas e estão funcionando:

| Dependência | Versão Instalada | Status |
|------------|------------------|--------|
| Python | 3.12.10 | OK |
| NumPy | 2.2.6 | OK |
| OpenCV | 4.12.0 | OK |
| EasyOCR | 1.7.2 | OK |
| Requests | 2.32.5 | OK |

### Dependências Transitivas Instaladas

- torch 2.9.1
- torchvision 0.24.1
- scikit-image 0.25.2
- scipy 1.16.3
- Pillow 12.0.0
- E outras dependências do EasyOCR

## Scripts Criados

### setup_python312.ps1

Script automatizado para configurar o ambiente Python 3.12:

- Detecta se Python 3.12 está instalado
- Oferece instalação via winget
- Cria ambiente virtual
- Instala todas as dependências
- Verifica instalação completa

**Uso:**
```powershell
cd apps/iot-device
.\scripts\setup_python312.ps1
```

### INSTALAR_PYTHON312.md

Guia completo de instalação do Python 3.12 com múltiplos métodos:
- Método 1: Script Automático
- Método 2: Instalação Manual
- Método 3: Usar Winget

## Próximos Passos

1. **Ativar o ambiente virtual:**
   ```powershell
   cd apps/iot-device
   .\venv\Scripts\Activate.ps1
   ```

2. **Configurar variáveis de ambiente:**
   - Consulte `docs/GUIA_DEMONSTRACAO_E_AVALIACAO.md`

3. **Executar o sistema:**
   ```powershell
   python main.py
   ```

## Notas Importantes

- O ambiente virtual está localizado em `apps/iot-device/venv`
- Python 3.12.10 está sendo usado
- Todas as dependências foram instaladas usando wheels pré-compilados (sem necessidade de compilação)
- NumPy foi atualizado para 2.2.6 (compatível com Python 3.12 e todas as dependências)

## Problemas Resolvidos

1. **Erro de compilação do NumPy no Python 3.14:**
   - Resolvido: Python 3.12 possui wheels pré-compilados

2. **Erro de compilação do scikit-image:**
   - Resolvido: scikit-image possui wheels pré-compilados para Python 3.12

3. **Falha na instalação do EasyOCR:**
   - Resolvido: Todas as dependências do EasyOCR foram instaladas com sucesso

## Conclusão

A regressão para Python 3.12 foi concluída com sucesso. O ambiente está pronto para desenvolvimento e demonstração do sistema de reconhecimento automático de placas.

