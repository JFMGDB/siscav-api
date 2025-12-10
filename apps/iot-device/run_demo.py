"""Script para executar a demonstração do dispositivo IoT."""

import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

# Criar mapeamento para apps.iot_device -> apps.iot-device
import importlib.util

# Criar módulo apps se não existir
if 'apps' not in sys.modules:
    import types
    apps_module = types.ModuleType('apps')
    sys.modules['apps'] = apps_module

# Criar módulo apps.iot_device apontando para iot-device
iot_device_dir = root_dir / 'apps' / 'iot-device'
if 'apps.iot_device' not in sys.modules:
    # Criar um loader customizado
    class IOTDeviceLoader:
        def __init__(self, path):
            self.path = path
        
        def load_module(self, name):
            # Adicionar o diretório ao sys.path para imports relativos
            if str(self.path) not in sys.path:
                sys.path.insert(0, str(self.path))
            return sys.modules.setdefault(name, types.ModuleType(name))
    
    # Criar módulo vazio
    import types
    iot_module = types.ModuleType('apps.iot_device')
    sys.modules['apps.iot_device'] = iot_module
    
    # Adicionar o diretório ao sys.path
    if str(iot_device_dir) not in sys.path:
        sys.path.insert(0, str(iot_device_dir))

# Configurar variáveis de ambiente se não estiverem definidas
if 'API_BASE_URL' not in os.environ:
    os.environ['API_BASE_URL'] = 'http://localhost:8000/api/v1'
if 'CAMERA_ID' not in os.environ:
    os.environ['CAMERA_ID'] = '0'
if 'ENABLE_DISPLAY' not in os.environ:
    os.environ['ENABLE_DISPLAY'] = 'true'
if 'ENABLE_SOUND' not in os.environ:
    os.environ['ENABLE_SOUND'] = 'true'
if 'LOG_LEVEL' not in os.environ:
    os.environ['LOG_LEVEL'] = 'INFO'

# Mudar para o diretório do iot-device
os.chdir(iot_device_dir)

# Importar e executar main
# Primeiro, precisamos fazer o import funcionar
# Vamos adicionar o diretório apps ao path e criar um __init__.py temporário
apps_dir = root_dir / 'apps'
if str(apps_dir) not in sys.path:
    sys.path.insert(0, str(apps_dir))

# Criar um link simbólico lógico no Python
# Como não podemos criar link simbólico real, vamos usar importlib
import importlib

# Tentar importar diretamente modificando o path
sys.path.insert(0, str(iot_device_dir.parent))
sys.path.insert(0, str(iot_device_dir))

# Agora tentar importar usando o caminho correto
# Vamos modificar o main.py para usar imports relativos ou executar diretamente
exec(open(iot_device_dir / 'main.py').read())













