from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import uuid
from app.database import get_db
from app.models import Classified, User, GuestApproval
from app.utils import validate_image_upload, decode_and_validate_image

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))

MAX_IMAGE_SIZE = 5 * 1024 * 1024

@router.get("/classifieds")
def classifieds_page(request: Request, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "user", None)
    
    classifieds = db.query(Classified).filter(Classified.status == "APPROVED").all()
    pending_classifieds = db.query(Classified).filter(Classified.status == "PENDING_SENSEI").all()
    
    my_classifieds = []
    if current_user:
        user_id = int(current_user.get("sub"))
        my_classifieds = db.query(Classified).filter(Classified.author_id == user_id).all()

    users = db.query(User).all()
    pending_guests_count = db.query(GuestApproval).filter(GuestApproval.status == "PENDING").count()

    return templates.TemplateResponse(request=request, name="page4_classifieds.html", context={
        "active_page": "classifieds",
        "classifieds": classifieds,
        "pending_classifieds": pending_classifieds,
        "my_classifieds": my_classifieds,
        "users": users,
        "pending_guests_count": pending_guests_count,
        "pending_classifieds_count": len(pending_classifieds),
        "current_user": current_user
    })

@router.post("/api/classifieds/create")
async def create_classified(
    request: Request,
    title: str = Form(...),
    category: str = Form(...),
    price: str = Form("0.0"),
    description: str = Form(...),
    photo_url: str = Form(None),
    photo_file: UploadFile = File(None),
    photo_base64: str = Form(None),
    author_id: str = Form(None),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    user_id = int(current_user.get("sub"))
    user_role = current_user.get("role")

    parsed_author_id = int(author_id) if author_id and str(author_id).isdigit() else user_id
    if user_role == "STUDENT":
        parsed_author_id = user_id

    try:
        parsed_price = float(price) if price else 0.0
    except ValueError:
        parsed_price = 0.0

    author = db.query(User).filter(User.id == parsed_author_id).first()
    initial_status = "APPROVED" if (author and author.role in ["SENSEI", "ADMIN"]) else "PENDING_SENSEI"

    final_photo_url = photo_url
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads", "classifieds")
    os.makedirs(upload_dir, exist_ok=True)

    if photo_base64:
        raw, ext = decode_and_validate_image(photo_base64, MAX_IMAGE_SIZE)
        if raw and ext:
            unique_filename = f"prod_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(raw)
            final_photo_url = f"/static/uploads/classifieds/{unique_filename}"
    elif photo_file and photo_file.filename:
        content = await photo_file.read()
        ext = validate_image_upload(photo_file.filename, content, MAX_IMAGE_SIZE)
        if ext:
            unique_filename = f"prod_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(content)
            final_photo_url = f"/static/uploads/classifieds/{unique_filename}"

    new_classified = Classified(
        author_id=parsed_author_id,
        title=title,
        category=category,
        price=parsed_price,
        description=description,
        photo_url=final_photo_url or "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=400",
        status=initial_status,
        rejection_reason=None
    )
    db.add(new_classified)
    db.commit()
    return RedirectResponse(url="/classifieds", status_code=303)

@router.post("/api/classifieds/{classified_id}/update")
async def update_classified(
    classified_id: int,
    request: Request,
    title: str = Form(...),
    category: str = Form(...),
    price: str = Form("0.0"),
    description: str = Form(...),
    photo_url: str = Form(None),
    photo_file: UploadFile = File(None),
    photo_base64: str = Form(None),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        return JSONResponse({"error": "Não autenticado"}, status_code=401)

    user_id = int(current_user.get("sub"))
    user_role = current_user.get("role")

    item = db.query(Classified).filter(Classified.id == classified_id).first()
    if not item:
        return JSONResponse({"error": "Anúncio não encontrado"}, status_code=404)

    if user_role == "STUDENT" and item.author_id != user_id:
        return JSONResponse({"error": "Acesso negado. Você só pode editar seus próprios anúncios."}, status_code=403)

    try:
        parsed_price = float(price) if price else item.price
    except ValueError:
        parsed_price = item.price

    item.title = title
    item.category = category
    item.price = parsed_price
    item.description = description

    if user_role == "STUDENT":
        item.status = "PENDING_SENSEI"
        item.rejection_reason = None

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads", "classifieds")
    os.makedirs(upload_dir, exist_ok=True)

    if photo_base64:
        raw, ext = decode_and_validate_image(photo_base64, MAX_IMAGE_SIZE)
        if raw and ext:
            unique_filename = f"prod_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(raw)
            item.photo_url = f"/static/uploads/classifieds/{unique_filename}"
    elif photo_file and photo_file.filename:
        content = await photo_file.read()
        ext = validate_image_upload(photo_file.filename, content, MAX_IMAGE_SIZE)
        if ext:
            unique_filename = f"prod_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(content)
            item.photo_url = f"/static/uploads/classifieds/{unique_filename}"
    elif photo_url and photo_url.strip():
        item.photo_url = photo_url.strip()

    db.commit()
    return RedirectResponse(url="/classifieds", status_code=303)

@router.post("/api/classifieds/{classified_id}/status")
async def update_classified_status(
    classified_id: int,
    request: Request,
    status: str = Form(None),
    rejection_reason: str = Form(None),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        return JSONResponse({"error": "Não autenticado"}, status_code=401)

    user_role = current_user.get("role")
    if user_role not in ["ADMIN", "SENSEI"]:
        return JSONResponse({"error": "Acesso negado. Apenas Senseis e Administradores podem aprovar ou reprovar anúncios."}, status_code=403)

    if not status:
        status = request.query_params.get("status")

    if not status:
        return JSONResponse({"error": "Status não fornecido"}, status_code=400)

    item = db.query(Classified).filter(Classified.id == classified_id).first()
    if not item:
        return JSONResponse({"error": "Anúncio não encontrado"}, status_code=404)

    item.status = status
    if status == "REJECTED":
        item.rejection_reason = rejection_reason or "Anúncio não atende aos requisitos do dojo."
    else:
        item.rejection_reason = None

    db.commit()
    return JSONResponse({"status": "success", "classified_status": item.status, "rejection_reason": item.rejection_reason})

@router.post("/api/classifieds/{classified_id}/delete")
def delete_classified(classified_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    user_id = int(current_user.get("sub"))
    user_role = current_user.get("role")

    item = db.query(Classified).filter(Classified.id == classified_id).first()
    if not item:
        return JSONResponse({"error": "Anúncio não encontrado"}, status_code=404)

    if user_role == "STUDENT" and item.author_id != user_id:
        return JSONResponse({"error": "Acesso negado. Você só pode excluir seus próprios anúncios."}, status_code=403)

    db.delete(item)
    db.commit()
    return RedirectResponse(url="/classifieds", status_code=303)
