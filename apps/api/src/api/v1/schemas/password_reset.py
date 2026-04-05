from pydantic import BaseModel, EmailStr, Field


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="Email da conta a redefinir.")


class PasswordResetRequested(BaseModel):
    message: str = Field(
        ...,
        description="Mensagem genérica (evita enumeração de contas por email).",
    )
    reset_token: str | None = Field(
        None,
        description=(
            "JWT de redefinição (só preenchido quando "
            "PASSWORD_RESET_EXPOSE_TOKEN_IN_RESPONSE está ativo; nunca confiar em produção sem HTTPS)."
        ),
    )


class PasswordResetConfirm(BaseModel):
    token: str = Field(..., min_length=1, description="Token JWT devolvido pelo fluxo de pedido.")
    new_password: str = Field(..., min_length=8, description="Nova senha (mín. 8 caracteres).")


class PasswordResetConfirmed(BaseModel):
    detail: str = Field(default="Password has been reset successfully.")
