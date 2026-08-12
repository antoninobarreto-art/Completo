import os
import time
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any

def _load_env_file() -> None:
    """Carrega variaveis do arquivo .env da raiz do projeto (se existir), sem sobrescrever o ambiente."""
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except OSError:
        pass

_load_env_file()

# Chave de assinatura dos tokens JWT: OBRIGATORIA via ambiente ou .env (sem fallback inseguro)
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY nao configurada. Defina a variavel de ambiente ou crie o arquivo .env "
        "na raiz do projeto com JWT_SECRET_KEY=<chave-forte>."
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas de sessão

def hash_password(password: str) -> str:
    """Gera hash seguro utilizando bcrypt com salting automático."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Valida a senha aberta contra o hash bcrypt salvo no banco."""
    try:
        pwd_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Gera um JWT assinado contendo as claims de identificação e perfis/permissões."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({
        "exp": expire,
        "iat": now
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodifica e valida a assinatura e expiração do JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None
