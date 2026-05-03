"""Script para testar o endpoint de registro de usuário."""

import json
import sys

import requests

# URL base da API
BASE_URL = "http://localhost:8000"


def run_register():
    """Chama o endpoint de registro (uso manual; não é teste pytest)."""
    url = f"{BASE_URL}/api/v1/register"

    user_data = {
        "email": "teste@example.com",
        "password": "senha123456",
    }

    print(f"Testando registro em: {url}")
    print(f"Dados: {json.dumps(user_data, indent=2)}")
    print("-" * 60)

    try:
        response = requests.post(url, json=user_data, timeout=5)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")

        if response.status_code == 201:
            print("\n✅ SUCESSO! Usuário registrado com sucesso!")
            data = response.json()
            print(f"ID: {data.get('id')}")
            print(f"Email: {data.get('email')}")
            return True
        print(f"\n❌ ERRO! Status: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Detalhes: {json.dumps(error_data, indent=2)}")
        except Exception:
            print(f"Resposta: {response.text}")
        return False

    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar ao servidor!")
        print("Certifique-se de que o servidor está rodando em http://localhost:8000")
        print("\nPara iniciar o servidor:")
        print("  cd apps/api/src")
        print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE REGISTRO DE USUÁRIO")
    print("=" * 60)
    print()

    success = run_register()

    print()
    print("=" * 60)
    sys.exit(0 if success else 1)
