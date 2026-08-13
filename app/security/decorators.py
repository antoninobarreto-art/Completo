from typing import List, Union
from fastapi import Request, HTTPException, status
from app.security.auth import decode_access_token

def get_current_user_from_request(request: Request) -> dict:
    """
    Hook de infraestrutura: Extrai e decodifica o usuário do Header Authorization ou do Cookie de Sessão.
    """
    token = None

    # 1. Verifica Header Bearer
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    # 2. Fallback para Cookie (para rotas que renderizam HTML no navegador)
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado. Token não fornecido."
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado."
        )

    return payload

def requer_permissao(permissoes_requeridas: Union[str, List[str]]):
    """
    Dependency Plugável de RBAC/IAM para rotas FastAPI.

    Uso FastAPI:
        @router.post("/rota")
        def minha_rota(user=Depends(requer_permissao(['ADMIN', 'SENSEI']))):
            ...
    """
    if isinstance(permissoes_requeridas, str):
        permissoes_requeridas = [permissoes_requeridas]

    # Normaliza permissões requeridas para caixa alta
    permissoes_requeridas = [p.upper() for p in permissoes_requeridas]

    def dependency(request: Request):
        user = get_current_user_from_request(request)
        user_role = str(user.get("role", "")).upper()
        user_permissions = [p.upper() for p in user.get("permissions", [])]

        # Verifica se o usuário tem a Role/Perfil ou a Permissão explícita
        tem_acesso = (
            user_role in permissoes_requeridas or 
            any(p in user_permissions for p in permissoes_requeridas) or
            user_role == "ADMIN"  # Admin tem bypass pleno
        )

        if not tem_acesso:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Requer permissão: {', '.join(permissoes_requeridas)}"
            )

        return user

    return dependency

