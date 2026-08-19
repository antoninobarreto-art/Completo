import os, datetime, secrets, logging
from fastapi import APIRouter, Request, Depends, Form, HTTPException, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security.auth import verify_password, create_access_token, hash_password, decode_access_token
from app.security.rate_limiter import login_rate_limiter
from app.version import VERSION

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))
templates.env.globals["system_version"] = VERSION

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, msg: str = None, error: str = None):
    # Se já tem token VÁLIDO, redireciona para a home
    token = request.cookies.get("access_token")
    if token and not msg and not error:
        user = decode_access_token(token)
        if user:
            return RedirectResponse(url="/", status_code=303)

    response = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": error, "msg": msg}
    )
    if token and not decode_access_token(token):
        response.delete_cookie("access_token", path="/")
    return response

@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    client_ip = request.client.host if request.client else "127.0.0.1"

    if not login_rate_limiter.is_allowed(client_ip):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Muitas tentativas malsucedidas. Aguarde 60 segundos antes de tentar novamente."},
            status_code=429
        )

    user = db.query(User).filter(User.email == email.strip()).first()
    if not user or not user.is_active:
        # Mensagem genérica proposital: não revela se o e-mail existe nem se a conta está inativa
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "E-mail ou senha incorretos."},
            status_code=401
        )

    if not user.password_hash or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "E-mail ou senha incorretos."},
            status_code=401
        )

    login_rate_limiter.reset(client_ip)

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "belt_rank": user.belt_rank,
        "photo_url": user.photo_url
    })

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 8, # 8 horas
        path="/",
        samesite="lax"
    )
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token", path="/")
    return response

# REQUISIÇÃO DE RECUPERAÇÃO DE SENHA ("Esqueceu a senha?")
@router.post("/api/forgot-password")
def forgot_password(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    # Resposta ÚNICA e genérica: idêntica para e-mail existente ou não (anti-enumeração)
    generic_msg = "Se o e-mail estiver cadastrado, enviamos um link de redefinição para a sua caixa de entrada."

    user = db.query(User).filter(User.email == email.strip()).first()
    if user:
        # Gera Token Único e Expiração de 1 hora
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        db.commit()

        reset_link = f"{request.base_url}reset-password?token={token}"
        # TODO(P2): substituir por envio real de e-mail (SMTP transacional).
        # O link NUNCA deve ser exibido na tela (risco de sequestro de conta).
        logger.info(f"[E-MAIL SIMULADO DE RECUPERAÇÃO DE SENHA] Para: {user.email} | Link: {reset_link}")

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"msg": generic_msg}
    )

# TELA DE REDEFINIÇÃO DE SENHA (Acessada via link do e-mail)
@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request, token: str = None, db: Session = Depends(get_db)):
    if not token:
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={"error": "Token de redefinição inválido ou não fornecido.", "token_valid": False}
        )

    user = db.query(User).filter(User.reset_token == token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.datetime.utcnow():
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={"error": "O link de redefinição é inválido ou já expirou. Solicite um novo link.", "token_valid": False}
        )

    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={"token": token, "token_valid": True, "error": None}
    )

# AÇÃO DE SALVAR A NOVA SENHA
@router.post("/api/reset-password")
def reset_password_submit(
    request: Request,
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if new_password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={"error": "As senhas digitadas não coincidem. Tente novamente.", "token": token, "token_valid": True}
        )

    if len(new_password) < 4:
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={"error": "A nova senha deve ter no mínimo 4 caracteres.", "token": token, "token_valid": True}
        )

    user = db.query(User).filter(User.reset_token == token).first()
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.datetime.utcnow():
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={"error": "O link de redefinição expirou. Solicite um novo.", "token_valid": False}
        )

    # Atualiza a Senha Bcrypt e Invalida o Token
    user.password_hash = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"msg": "Sua senha foi alterada com sucesso! Você já pode fazer login com a nova senha."}
    )
