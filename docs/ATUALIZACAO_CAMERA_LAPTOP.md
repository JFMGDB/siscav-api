# Atualização: Uso da Câmera do Laptop

## Informação Importante

**A demonstração utilizará a câmera integrada do laptop onde será realizada.**

## Documentação Atualizada

As seguintes documentações foram atualizadas para refletir o uso da câmera do laptop:

1. ✅ **GUIA_RAPIDO_DEMONSTRACAO.md**
   - Adicionada nota sobre uso da câmera do laptop
   - Instruções sobre permissões do Windows
   - Troubleshooting específico para câmera de laptop

2. ✅ **DEMONSTRACAO_COMPLETA.md**
   - Atualizada seção de pré-requisitos
   - Adicionadas instruções sobre permissões
   - Troubleshooting expandido

3. ✅ **NOTA_CAMERA_LAPTOP.md** (NOVO)
   - Documento dedicado com todas as informações sobre uso da câmera do laptop
   - Configuração e permissões
   - Problemas comuns e soluções
   - Dicas para demonstração

4. ✅ **README_DEMONSTRACAO.md**
   - Adicionada referência à nota sobre câmera do laptop

## Configuração Padrão

A configuração padrão já está adequada para uso da câmera do laptop:

```powershell
$env:CAMERA_ID=0  # Câmera do laptop (padrão)
```

## Permissões no Windows

**Importante**: Na primeira execução, o Windows solicitará permissão para acessar a câmera.

### Configuração Manual (se necessário)

1. Abrir **Configurações do Windows**
2. Ir em **Privacidade > Câmera**
3. Habilitar:
   - "Permitir que aplicativos acessem sua câmera"
   - "Permitir que aplicativos da área de trabalho acessem sua câmera"

### Verificação

Para verificar se a câmera está acessível:

```powershell
cd apps/iot-device
.\venv\Scripts\Activate.ps1
python -c "import cv2; cap = cv2.VideoCapture(0); print('Câmera OK' if cap.isOpened() else 'Câmera não encontrada'); cap.release()"
```

## Durante a Demonstração

1. **Posicionamento da Placa**:
   - Posicionar a placa na frente da câmera do laptop
   - Manter distância adequada (1-2 metros)
   - Garantir boa iluminação

2. **Área de Visão**:
   - A placa deve estar visível na tela do laptop
   - Evitar reflexos e sombras
   - Manter a placa reta (não inclinada)

3. **Feedback Visual**:
   - O sistema mostrará uma janela com o vídeo da câmera
   - Detecções aparecerão com retângulos coloridos
   - Status será exibido (Authorized/Denied)

## Referências

- **Documento Completo**: `docs/NOTA_CAMERA_LAPTOP.md`
- **Guia Rápido**: `docs/GUIA_RAPIDO_DEMONSTRACAO.md`
- **Guia Completo**: `docs/DEMONSTRACAO_COMPLETA.md`

