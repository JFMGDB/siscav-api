"""Controllers - Camada de lógica de negócio (Service Layer).

Esta camada contém a lógica de negócio da aplicação, seguindo os princípios SOLID.
Os controllers orquestram operações entre repositories e aplicam regras de negócio.
"""

from apps.api.src.api.v1.controllers.access_log_controller import AccessLogController
from apps.api.src.api.v1.controllers.auth_controller import AuthController
from apps.api.src.api.v1.controllers.device_controller import DeviceController
from apps.api.src.api.v1.controllers.gate_controller import GateController
from apps.api.src.api.v1.controllers.plate_controller import PlateController

__all__ = [
    "AuthController",
    "PlateController",
    "AccessLogController",
    "GateController",
    "DeviceController",
]

