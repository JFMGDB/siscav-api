"""Script wrapper para executar o dispositivo IoT com PYTHONPATH correto."""

import sys
import os
from pathlib import Path

# Diretório atual (iot-device)
current_dir = Path(__file__).parent.absolute()

# Diretório raiz do projeto
root_dir = current_dir.parent.parent

# Adicionar diretório raiz ao PYTHONPATH
sys.path.insert(0, str(root_dir))

# Adicionar diretório iot-device ao PYTHONPATH para imports locais
sys.path.insert(0, str(current_dir))

# Criar estrutura de módulos apps.iot_device
import types

# Criar módulo apps se não existir
if 'apps' not in sys.modules:
    apps_module = types.ModuleType('apps')
    apps_module.__path__ = [str(root_dir / 'apps')]
    sys.modules['apps'] = apps_module

# Criar módulo apps.iot_device apontando para o diretório atual
if 'apps.iot_device' not in sys.modules:
    iot_device_module = types.ModuleType('apps.iot_device')
    iot_device_module.__path__ = [str(current_dir)]
    iot_device_module.__file__ = str(current_dir / '__init__.py')
    sys.modules['apps.iot_device'] = iot_device_module
    
    # Vincular ao módulo apps
    sys.modules['apps'].iot_device = iot_device_module

# Função para registrar sub-módulos dinamicamente
def register_submodule(parent_name, submodule_name, submodule_path):
    """Registra um sub-módulo no sys.modules."""
    full_name = f"{parent_name}.{submodule_name}"
    if full_name not in sys.modules:
        module = types.ModuleType(full_name)
        module.__path__ = [str(submodule_path)]
        module.__file__ = str(submodule_path / '__init__.py')
        sys.modules[full_name] = module
        
        # Vincular ao módulo pai
        parent = sys.modules[parent_name]
        setattr(parent, submodule_name, module)

# Registrar sub-módulos
register_submodule('apps.iot_device', 'services', current_dir / 'services')
register_submodule('apps.iot_device', 'utils', current_dir / 'utils')

# Agora importar e executar main
if __name__ == '__main__':
    # Mudar para o diretório do iot-device
    os.chdir(current_dir)
    
    # Importar config primeiro (para garantir que está disponível)
    import config as local_config
    sys.modules['apps.iot_device.config'] = local_config
    
    # Importar serviços
    from services import api_client, camera, plate_detector, arduino
    from utils import debounce, plate_validator
    
    sys.modules['apps.iot_device.services.api_client'] = api_client
    sys.modules['apps.iot_device.services.camera'] = camera
    sys.modules['apps.iot_device.services.plate_detector'] = plate_detector
    sys.modules['apps.iot_device.services.arduino'] = arduino
    sys.modules['apps.iot_device.utils.debounce'] = debounce
    sys.modules['apps.iot_device.utils.plate_validator'] = plate_validator
    
    # Tentar importar OCR (pode não estar disponível)
    try:
        from services import ocr
        sys.modules['apps.iot_device.services.ocr'] = ocr
    except ImportError:
        pass
    
    # Executar main.py
    exec(open('main.py').read())
