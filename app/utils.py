def format_date_br(value) -> str:
    """Format dates to DD/MM/AAAA or DD/MM/AAAA HH:MM Brazilian format."""
    if not value:
        return ""
    val = str(value).strip()
    if not val or val == "None":
        return ""

    # Replace ISO T separator with space
    val_clean = val.replace("T", " ")
    parts = val_clean.split(" ")

    date_part = parts[0]
    time_part = parts[1][:5] if len(parts) > 1 else ""

    # If date_part is YYYY-MM-DD
    if "-" in date_part:
        subparts = date_part.split("-")
        if len(subparts) == 3 and len(subparts[0]) == 4:
            year, month, day = subparts[0], subparts[1], subparts[2]
            formatted_date = f"{day}/{month}/{year}"
            if time_part:
                return f"{formatted_date} {time_part}"
            return formatted_date

    return val


# ============================================================
# Validacao segura de uploads (auditoria P0 - itens A-02/A-03)
# Bloqueia arquivos com extensao falsa (.html, .exe) e ataques
# de double-extension usando magic bytes reais do conteudo.
# ============================================================
import base64 as _base64

ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_DOC_EXTS = {".pdf", ".txt", ".doc", ".docx"}


def _sniff_image_ext(content: bytes):
    """Detecta a extensao real de uma imagem pelos magic bytes.
    Retorna '.png' / '.jpg' / '.webp' ou None se nao for imagem valida."""
    if not content or len(content) < 12:
        return None
    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    # JPEG: FF D8 FF
    if content.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    # WebP: "RIFF" .... "WEBP"
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return ".webp"
    return None


def _sniff_doc_ext(content: bytes):
    """Detecta a extensao real de um documento (PDF/DOCX/DOC) pelos magic bytes.
    Retorna '.pdf' / '.docx' / '.doc' ou None. .txt nao tem assinatura, aceita pela extensao."""
    if not content or len(content) < 4:
        return None
    # PDF: "%PDF"
    if content.startswith(b"%PDF"):
        return ".pdf"
    # DOCX/XLSX (Office Open XML) sao arquivos ZIP: PK\x03\x04
    if content[:4] == b"PK\x03\x04":
        return ".docx"
    # DOC/XLS/PPT (Office legacy) sao OLE2: D0 CF 11 E0
    if content[:4] == b"\xd0\xcf\11\xe0":
        return ".doc"
    return None


def validate_image_upload(filename: str, content: bytes, max_size: int):
    """Valida um upload de imagem (file binario) por extensao declarada + magic bytes.
    Retorna a extensao REAL detectada ('.png'/'.'jpg'/'.webp') ou None se invalido.
    NUNCA confia na extensao declarada pelo cliente - usa o conteudo real."""
    if not content or len(content) > max_size:
        return None
    # extensao declarada apenas como sinal; a real vem dos magic bytes
    return _sniff_image_ext(content)


def validate_doc_upload(filename: str, content: bytes, max_size: int):
    """Valida um upload de documento por extensao declarada + magic bytes.
    Retorna a extensao REAL detectada ou None se invalido. .txt aceito pela extensao."""
    if not content or len(content) > max_size:
        return None
    declared = (filename or "").rsplit(".", 1)[-1].lower() if "." in (filename or "") else ""
    if declared == "txt":
        return ".txt"
    return _sniff_doc_ext(content)


def decode_and_validate_image(base64_data: str, max_size: int):
    """Decodifica data:image/...;base64,XXX e valida o conteudo.
    Retorna (bytes_content, ext) ou (None, None) se invalido.
    Substitui a logica antiga que confiava no header do data URI."""
    if not base64_data or "base64," not in base64_data:
        return None, None
    try:
        # aceita tanto "data:image/png;base64,XXX" quanto "data:image/...";base64,XXX"
        encoded = base64_data.split("base64,", 1)[1]
        raw = _base64.b64decode(encoded, validate=True)
    except (ValueError, _base64.binascii.Error):
        return None, None
    ext = _sniff_image_ext(raw)
    if not ext or len(raw) > max_size:
        return None, None
    return raw, ext


def get_required_attendances(belt_rank: str) -> int:
    """
    Retorna o número mínimo de treinos necessários para o exame de faixa.
    """
    if not belt_rank:
        return 60
    r_c = belt_rank.lower()

    # Dan ranks (verificados primeiro para evitar conflitos de '1º', '2º', '4º' com Kyus)
    if "yondan" in r_c or "4º dan" in r_c or "4 dan" in r_c or "godan" in r_c or "5º dan" in r_c or "rokudan" in r_c or "6º dan" in r_c:
        return 800
    elif "nidan" in r_c or "2º dan" in r_c or "2 dan" in r_c or "sandan" in r_c or "3º dan" in r_c or "3 dan" in r_c:
        return 600
    elif "shodan" in r_c or "1º dan" in r_c or "1 dan" in r_c:
        return 400

    # Kyu ranks
    elif "1º" in r_c or "1 kyu" in r_c or "marrom" in r_c or "castanha" in r_c:
        return 100
    elif "2º" in r_c or "2 kyu" in r_c or "azul" in r_c:
        return 90
    elif "3º" in r_c or "3 kyu" in r_c or "verde" in r_c:
        return 60
    elif "4º" in r_c or "4 kyu" in r_c or "roxa" in r_c:
        return 60
    elif "5º" in r_c or "5 kyu" in r_c or "amarela" in r_c:
        return 40

    return 60

