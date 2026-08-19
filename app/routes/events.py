from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import uuid
from app.database import get_db
from app.models import Event, User, EventPresence, EventTask, EventExternalParticipant, GuestApproval, Classified
from app.utils import format_date_br, validate_image_upload, decode_and_validate_image
from app.version import VERSION

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))
templates.env.filters["date_br"] = format_date_br
templates.env.globals["system_version"] = VERSION

MAX_IMAGE_SIZE = 5 * 1024 * 1024

@router.get("/events")
def events_page(request: Request, db: Session = Depends(get_db)):
    events = db.query(Event).all()
    senseis = db.query(User).filter(User.role.in_(["SENSEI", "ADMIN"])).all()
    all_users = db.query(User).all()

    pending_guests_count = db.query(GuestApproval).filter(GuestApproval.status == "PENDING").count()
    pending_classifieds_count = db.query(Classified).filter(Classified.status == "PENDING_SENSEI").count()

    return templates.TemplateResponse(request=request, name="page5_events.html", context={
        "active_page": "events",
        "events": events,
        "senseis": senseis,
        "all_users": all_users,
        "pending_guests_count": pending_guests_count,
        "pending_classifieds_count": pending_classifieds_count,
        "current_user": getattr(request.state, "user", None)
    })

@router.post("/api/events/create")
async def create_event(
    request: Request,
    title: str = Form(...),
    date_time: str = Form(...),
    location: str = Form(...),
    main_sensei_id: str = Form(None),
    assistant_senseis: str = Form(None),
    description: str = Form(...),
    price: str = Form("0.0"),
    photo_url: str = Form(None),
    photo_file: UploadFile = File(None),
    photo_base64: str = Form(None),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") not in ["ADMIN", "SENSEI"]:
        raise HTTPException(status_code=403, detail="Apenas Senseis e Administradores podem criar eventos.")

    parsed_sensei_id = int(main_sensei_id) if main_sensei_id and str(main_sensei_id).isdigit() else None
    try:
        parsed_price = float(price) if price else 0.0
    except ValueError:
        parsed_price = 0.0

    final_photo_url = photo_url
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads", "events")
    os.makedirs(upload_dir, exist_ok=True)

    if photo_base64:
        raw, ext = decode_and_validate_image(photo_base64, MAX_IMAGE_SIZE)
        if raw and ext:
            unique_filename = f"event_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(raw)
            final_photo_url = f"/static/uploads/events/{unique_filename}"
    elif photo_file and photo_file.filename:
        content = await photo_file.read()
        ext = validate_image_upload(photo_file.filename, content, MAX_IMAGE_SIZE)
        if ext:
            unique_filename = f"event_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(content)
            final_photo_url = f"/static/uploads/events/{unique_filename}"

    # Process multiple assistant senseis selection
    form_data = await request.form()
    assistants_list = form_data.getlist("assistant_senseis")
    if assistants_list:
        final_assistant_senseis = ", ".join([a for a in assistants_list if a and a.strip()])
    else:
        final_assistant_senseis = assistant_senseis or ""

    new_event = Event(
        title=title,
        date_time=date_time,
        location=location,
        main_sensei_id=parsed_sensei_id,
        assistant_senseis=final_assistant_senseis,
        description=description,
        price=parsed_price,
        photo_url=final_photo_url or "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800",
        status="UPCOMING"
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # Process Tasks from Form
    form_data = await request.form()
    task_descriptions = form_data.getlist("task_descriptions")
    task_dates = form_data.getlist("task_dates")
    task_assigned_ids = form_data.getlist("task_assigned_ids")

    for i, desc in enumerate(task_descriptions):
        if desc and desc.strip():
            due = task_dates[i] if i < len(task_dates) else None
            assigned_raw = task_assigned_ids[i] if i < len(task_assigned_ids) else None
            parsed_assigned_id = int(assigned_raw) if assigned_raw and str(assigned_raw).isdigit() else None

            task = EventTask(
                event_id=new_event.id,
                assigned_user_id=parsed_assigned_id,
                description=desc.strip(),
                due_date=due.strip() if due else None
            )
            db.add(task)

    # Process External Participants from Form
    external_names = form_data.getlist("external_names")
    external_dojos = form_data.getlist("external_dojos")
    external_associations = form_data.getlist("external_associations")
    external_ranks = form_data.getlist("external_ranks")

    for i, ext_name in enumerate(external_names):
        if ext_name and ext_name.strip():
            ext_dojo = external_dojos[i] if i < len(external_dojos) else None
            ext_assoc = external_associations[i] if i < len(external_associations) else None
            ext_rank = external_ranks[i] if i < len(external_ranks) else None

            ext_p = EventExternalParticipant(
                event_id=new_event.id,
                name=ext_name.strip(),
                dojo=ext_dojo.strip() if ext_dojo else None,
                association=ext_assoc.strip() if ext_assoc else None,
                belt_rank=ext_rank.strip() if ext_rank else None
            )
            db.add(ext_p)

    db.commit()

    return RedirectResponse(url="/events", status_code=303)

@router.post("/api/events/{event_id}/register")
def register_event(event_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        raise HTTPException(status_code=401, detail="Não autenticado.")

    # Inscrição é sempre do usuário autenticado (qualquer user_id enviado pelo cliente é ignorado)
    user_id = int(current_user.get("sub"))

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    existing = db.query(EventPresence).filter(
        EventPresence.event_id == event_id,
        EventPresence.user_id == user_id
    ).first()

    if not existing:
        presence = EventPresence(event_id=event_id, user_id=user_id, status="CONFIRMED")
        db.add(presence)
        db.commit()

    return RedirectResponse(url="/events", status_code=303)

@router.post("/api/events/{event_id}/delete")
def delete_event(event_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    user_role = current_user.get("role")
    user_id = int(current_user.get("sub"))

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    if user_role != "ADMIN" and (user_role != "SENSEI" or event.main_sensei_id != user_id):
        raise HTTPException(status_code=403, detail="Acesso negado para excluir este evento.")

    db.delete(event)
    db.commit()
    return RedirectResponse(url="/events", status_code=303)

@router.post("/api/events/{event_id}/update")
async def update_event(
    event_id: int,
    request: Request,
    title: str = Form(...),
    date_time: str = Form(...),
    location: str = Form(...),
    main_sensei_id: str = Form(None),
    assistant_senseis: str = Form(None),
    description: str = Form(...),
    price: str = Form("0.0"),
    photo_url: str = Form(None),
    photo_file: UploadFile = File(None),
    photo_base64: str = Form(None),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    user_role = current_user.get("role")
    user_id = int(current_user.get("sub"))

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    if user_role != "ADMIN" and (user_role != "SENSEI" or event.main_sensei_id != user_id):
        raise HTTPException(status_code=403, detail="Acesso negado para editar este evento.")

    parsed_sensei_id = int(main_sensei_id) if main_sensei_id and str(main_sensei_id).isdigit() else event.main_sensei_id
    try:
        parsed_price = float(price) if price else event.price
    except ValueError:
        parsed_price = event.price

    form_data = await request.form()
    assistants_list = form_data.getlist("assistant_senseis")
    if assistants_list:
        final_assistant_senseis = ", ".join([a for a in assistants_list if a and a.strip()])
    else:
        final_assistant_senseis = assistant_senseis or ""

    event.title = title
    event.date_time = date_time
    event.location = location
    event.main_sensei_id = parsed_sensei_id
    event.assistant_senseis = final_assistant_senseis
    event.description = description
    event.price = parsed_price

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads", "events")
    os.makedirs(upload_dir, exist_ok=True)

    if photo_base64:
        raw, ext = decode_and_validate_image(photo_base64, MAX_IMAGE_SIZE)
        if raw and ext:
            unique_filename = f"event_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(raw)
            event.photo_url = f"/static/uploads/events/{unique_filename}"
    elif photo_file and photo_file.filename:
        content = await photo_file.read()
        ext = validate_image_upload(photo_file.filename, content, MAX_IMAGE_SIZE)
        if ext:
            unique_filename = f"event_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(content)
            event.photo_url = f"/static/uploads/events/{unique_filename}"
    elif photo_url and photo_url.strip():
        event.photo_url = photo_url.strip()

    # Process Tasks on Update
    form_data = await request.form()
    task_descriptions = form_data.getlist("task_descriptions")
    task_dates = form_data.getlist("task_dates")
    task_assigned_ids = form_data.getlist("task_assigned_ids")

    # Replace existing tasks
    db.query(EventTask).filter(EventTask.event_id == event.id).delete()
    for i, desc in enumerate(task_descriptions):
        if desc and desc.strip():
            due = task_dates[i] if i < len(task_dates) else None
            assigned_raw = task_assigned_ids[i] if i < len(task_assigned_ids) else None
            parsed_assigned_id = int(assigned_raw) if assigned_raw and str(assigned_raw).isdigit() else None

            task = EventTask(
                event_id=event.id,
                assigned_user_id=parsed_assigned_id,
                description=desc.strip(),
                due_date=due.strip() if due else None
            )
            db.add(task)

    # Process Presences / Attendance confirmation
    present_user_ids_raw = form_data.getlist("present_user_ids")
    present_ids = set([int(x) for x in present_user_ids_raw if str(x).isdigit()])
    
    existing_presences = db.query(EventPresence).filter(EventPresence.event_id == event.id).all()
    for p in existing_presences:
        if p.user_id in present_ids:
            p.status = "ATTENDED"
        else:
            p.status = "CONFIRMED"

    # Process External Participants on Update
    external_names = form_data.getlist("external_names")
    external_dojos = form_data.getlist("external_dojos")
    external_associations = form_data.getlist("external_associations")
    external_ranks = form_data.getlist("external_ranks")
    present_external_ids_raw = form_data.getlist("present_external_ids")
    present_external_ids = set([int(x) for x in present_external_ids_raw if str(x).isdigit()])

    db.query(EventExternalParticipant).filter(EventExternalParticipant.event_id == event.id).delete()
    for i, ext_name in enumerate(external_names):
        if ext_name and ext_name.strip():
            ext_dojo = external_dojos[i] if i < len(external_dojos) else None
            ext_assoc = external_associations[i] if i < len(external_associations) else None
            ext_rank = external_ranks[i] if i < len(external_ranks) else None

            ext_p = EventExternalParticipant(
                event_id=event.id,
                name=ext_name.strip(),
                dojo=ext_dojo.strip() if ext_dojo else None,
                association=ext_assoc.strip() if ext_assoc else None,
                belt_rank=ext_rank.strip() if ext_rank else None,
                is_present=True
            )
            db.add(ext_p)

    db.commit()
    return RedirectResponse(url="/events", status_code=303)

@router.post("/api/events/{event_id}/tasks/{task_id}/toggle")
def toggle_event_task(event_id: int, task_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        raise HTTPException(status_code=401, detail="Não autenticado.")

    task = db.query(EventTask).filter(EventTask.id == task_id, EventTask.event_id == event_id).first()
    if not task:
        return RedirectResponse(url=f"/events#event-{event_id}", status_code=303)

    # Apenas ADMIN, o Sensei responsável pelo evento ou o responsável pela tarefa
    event = db.query(Event).filter(Event.id == event_id).first()
    user_id = int(current_user.get("sub"))
    allowed = (
        current_user.get("role") == "ADMIN" or
        (event and event.main_sensei_id == user_id) or
        task.assigned_user_id == user_id
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="Acesso negado para alterar esta tarefa.")

    task.is_completed = not task.is_completed
    db.commit()
    return RedirectResponse(url=f"/events#event-{event_id}", status_code=303)

@router.post("/api/events/{event_id}/tasks/{task_id}/delete")
def delete_event_task(event_id: int, task_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        raise HTTPException(status_code=401, detail="Não autenticado.")

    task = db.query(EventTask).filter(EventTask.id == task_id, EventTask.event_id == event_id).first()
    if not task:
        return RedirectResponse(url=f"/events#event-{event_id}", status_code=303)

    # Exclusão apenas por ADMIN ou pelo Sensei responsável pelo evento
    event = db.query(Event).filter(Event.id == event_id).first()
    user_id = int(current_user.get("sub"))
    allowed = (
        current_user.get("role") == "ADMIN" or
        (current_user.get("role") == "SENSEI" and event and event.main_sensei_id == user_id)
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="Apenas o Sensei responsável pelo evento ou Administradores podem excluir tarefas.")

    db.delete(task)
    db.commit()
    return RedirectResponse(url=f"/events#event-{event_id}", status_code=303)
