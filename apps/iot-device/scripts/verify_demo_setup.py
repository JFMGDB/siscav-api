"""Script de verificação pré-demonstração.

Verifica se todos os componentes necessários estão configurados
e funcionando corretamente antes de uma demonstração.
"""

import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def check_python_version():
    """Verifica versão do Python."""
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3:
        print("  ERRO: Python 3 é necessário")
        return False
    
    if version.minor < 10:
        print("  ERRO: Python 3.10+ é necessário")
        return False
    
    if version.minor >= 13:
        print("  AVISO: Python 3.13+ pode ter problemas de compatibilidade")
        print("     Recomendado: Python 3.10, 3.11 ou 3.12")
        return False
    
    print("  OK: Versão compatível")
    return True


def check_dependencies():
    """Verifica se dependências estão instaladas."""
    required = {
        "cv2": "opencv-python",
        "numpy": "numpy",
        "easyocr": "easyocr",
        "requests": "requests",
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  OK: {package}")
        except ImportError:
            print(f"  ERRO: {package} não instalado")
            missing.append(package)
    
    return len(missing) == 0, missing


def check_camera():
    """Verifica se câmera está disponível."""
    try:
        import cv2
        camera_id = int(os.getenv("CAMERA_ID", "0"))
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"  ERRO: Câmera {camera_id} não encontrada")
            cap.release()
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print(f"  ERRO: Não foi possível ler frame da câmera {camera_id}")
            return False
        
        print(f"  OK: Câmera {camera_id} funcionando")
        return True
    except Exception as e:
        print(f"  ERRO: Erro ao verificar câmera: {e}")
        return False


def check_api_connection():
    """Verifica conexão com API."""
    try:
        import requests
        api_url = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
        health_url = f"{api_url}/health" if not api_url.endswith("/health") else api_url
        
        # Tentar health check
        if not health_url.endswith("/health"):
            if health_url.endswith("/"):
                health_url = f"{health_url}health"
            else:
                health_url = f"{health_url}/health"
        
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            print(f"  OK: API acessível em {api_url}")
            return True
        else:
            print(f"  AVISO: API respondeu com status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ERRO: Não foi possível conectar à API em {api_url}")
        print("     Certifique-se de que a API está rodando")
        return False
    except Exception as e:
        print(f"  ERRO: Erro ao verificar API: {e}")
        return False


def check_config():
    """Verifica configurações importantes."""
    configs = {
        "API_BASE_URL": os.getenv("API_BASE_URL", "http://localhost:8000/api/v1"),
        "CAMERA_ID": os.getenv("CAMERA_ID", "0"),
        "ENABLE_DISPLAY": os.getenv("ENABLE_DISPLAY", "true"),
        "ENABLE_SOUND": os.getenv("ENABLE_SOUND", "true"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    }
    
    print("\nConfigurações:")
    for key, value in configs.items():
        print(f"  {key}={value}")
    
    return True


def main():
    """Função principal."""
    print("=" * 60)
    print("VERIFICAÇÃO PRÉ-DEMONSTRAÇÃO - SISCAV IoT Device")
    print("=" * 60)
    
    all_ok = True
    
    print("\n1. Verificando versão do Python...")
    if not check_python_version():
        all_ok = False
    
    print("\n2. Verificando dependências...")
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        all_ok = False
        print(f"\n   Para instalar dependências faltantes:")
        print(f"   pip install {' '.join(missing)}")
    
    print("\n3. Verificando câmera...")
    if not check_camera():
        all_ok = False
        print("   Dica: Tente diferentes IDs (0, 1, 2...) com CAMERA_ID")
    
    print("\n4. Verificando conexão com API...")
    if not check_api_connection():
        all_ok = False
        print("   Dica: Inicie a API com: uvicorn main:app --reload")
    
    print("\n5. Verificando configurações...")
    check_config()
    
    print("\n" + "=" * 60)
    if all_ok:
        print("SUCESSO: TODAS AS VERIFICACOES PASSARAM")
        print("   Sistema pronto para demonstracao!")
    else:
        print("ERRO: ALGUMAS VERIFICACOES FALHARAM")
        print("   Corrija os problemas acima antes da demonstracao")
    print("=" * 60)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

