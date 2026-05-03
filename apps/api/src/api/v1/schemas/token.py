from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., description="Token de acesso JWT.")
    refresh_token: str = Field(..., description="Token de refresh JWT.")
    token_type: str = Field("bearer", description="Tipo do token (geralmente 'bearer').")


class TokenPayload(BaseModel):
    sub: str | None = None
    type: str | None = None
