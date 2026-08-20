from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import os
import uuid

from app.database import get_db
from app.models import Dojo, User, ClassSchedule, ClassSession, Attendance, GuestApproval, Classified
from app.utils import format_date_br, validate_image_upload, validate_doc_upload, get_required_attendances
from app.version import VERSION

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))
templates.env.filters["date_br"] = format_date_br
templates.env.globals["system_version"] = VERSION

# Boas Práticas de Mercado para Limites de Upload
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5 MB para imagens (JPG, PNG, WEBP)
MAX_DOC_SIZE = 10 * 1024 * 1024    # 10 MB para documentos (PDF, TXT, DOCX)

from sqlalchemy import or_

@router.get("/schedule")
def schedule_page(request: Request, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "user", None)
    if current_user and current_user.get("role") == "STUDENT":
        return RedirectResponse(url="/", status_code=303)
    dojos = db.query(Dojo).all()
    schedules = db.query(ClassSchedule).all()
    sessions = db.query(ClassSession).order_by(ClassSession.id.desc()).all()
    senseis = db.query(User).filter(or_(User.role.in_(["SENSEI", "ADMIN"]), User.is_sensei == True)).all()
    students = db.query(User).filter(User.role == "STUDENT", User.is_active == True).all()

    # Map color stripes per dojo ID to replicate image model
    color_map = {
        1: "stripe-green",
        2: "stripe-red",
        3: "stripe-yellow",
        4: "stripe-blue",
        5: "stripe-purple"
    }

    # Structure by 7 Days of the Week
    weekdays_config = [
        {"code": "Segunda", "label": "20 - Segunda"},
        {"code": "Terça", "label": "21 - Terça"},
        {"code": "Quarta", "label": "22 - Quarta"},
        {"code": "Quinta", "label": "23 - Quinta"},
        {"code": "Sexta", "label": "24 - Sexta"},
        {"code": "Sábado", "label": "25 - Sábado"},
        {"code": "Domingo", "label": "26 - Domingo"}
    ]

    weekly_columns = []
    total_dojo_students = len(students) or 1

    for day in weekdays_config:
        day_schedules = [s for s in schedules if s.weekday == day["code"]]
        cards = []
        for sched in day_schedules:
            # Check if there is a session for this schedule
            matching_session = next((sess for sess in sessions if sess.schedule_id == sched.id), None)
            
            if matching_session:
                att_count = len(matching_session.attendances)
                ratio_pct = int((att_count / max(total_dojo_students, 1)) * 100)
                status = "Realizado"
                ratio_str = f"{att_count}/{total_dojo_students} ({ratio_pct}%)"
            else:
                status = "Pendente"
                ratio_str = None

            stripe = color_map.get(sched.dojo_id, "stripe-blue")

            cards.append({
                "schedule": sched,
                "session": matching_session,
                "status": status,
                "ratio_str": ratio_str,
                "stripe": stripe
            })

        weekly_columns.append({
            "label": day["label"],
            "code": day["code"],
            "cards": cards
        })

    pending_guests_count = db.query(GuestApproval).filter(GuestApproval.status == "PENDING").count()
    pending_classifieds_count = db.query(Classified).filter(Classified.status == "PENDING_SENSEI").count()

    return templates.TemplateResponse(request=request, name="page3_schedule.html", context={
        "active_page": "schedule",
        "dojos": dojos,
        "weekly_columns": weekly_columns,
        "schedules": schedules,
        "sessions": sessions,
        "senseis": senseis,
        "students": students,
        "pending_guests_count": pending_guests_count,
        "pending_classifieds_count": pending_classifieds_count,
        "current_user": getattr(request.state, "user", None)
    })

@router.post("/api/schedules/create")
def create_schedule(
    request: Request,
    dojo_id: int = Form(...),
    instructor_sensei_id: int = Form(...),
    weekday: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    title: str = Form(...),
    level: str = Form("Todos os Níveis"),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") not in ["ADMIN", "SENSEI"]:
        raise HTTPException(status_code=403, detail="Apenas Senseis e Administradores podem cadastrar turmas e horários.")

    new_schedule = ClassSchedule(
        dojo_id=dojo_id,
        instructor_sensei_id=instructor_sensei_id,
        weekday=weekday,
        start_time=start_time,
        end_time=end_time,
        title=title,
        level=level
    )
    db.add(new_schedule)
    db.commit()
    return RedirectResponse(url="/schedule", status_code=303)

@router.post("/api/schedules/{schedule_id}/update")
def update_schedule(
    schedule_id: int,
    request: Request,
    dojo_id: int = Form(...),
    instructor_sensei_id: int = Form(...),
    weekday: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    title: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") not in ["ADMIN", "SENSEI"]:
        raise HTTPException(status_code=403, detail="Apenas Senseis e Administradores podem alterar horários da grade.")

    schedule = db.query(ClassSchedule).filter(ClassSchedule.id == schedule_id).first()
    if schedule:
        schedule.dojo_id = dojo_id
        schedule.instructor_sensei_id = instructor_sensei_id
        schedule.weekday = weekday
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.title = title
        db.commit()
    return RedirectResponse(url="/schedule", status_code=303)

@router.post("/api/sessions/create-with-attendance")
async def create_session_attendance(
    request: Request,
    schedule_id: int = Form(...),
    date: str = Form(...),
    notes: str = Form(None),
    student_ids: List[int] = Form([]),
    single_class_guest_student_id: int = Form(None),
    single_class_guest_name: str = Form(None),
    photo_file: UploadFile = File(None),
    doc_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") not in ["ADMIN", "SENSEI"]:
        raise HTTPException(status_code=403, detail="Apenas Senseis e Administradores podem registrar aulas e presenças.")

    schedule = db.query(ClassSchedule).filter(ClassSchedule.id == schedule_id).first()
    if not schedule:
        return RedirectResponse(url="/schedule", status_code=303)

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads", "sessions")
    os.makedirs(upload_dir, exist_ok=True)

    photo_url = None
    document_url = None

    # Processing Photo Upload (Max 5MB)
    if photo_file and photo_file.filename:
        content = await photo_file.read()
        ext = validate_image_upload(photo_file.filename, content, MAX_IMAGE_SIZE)
        if ext:
            unique_filename = f"photo_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(content)
            photo_url = f"/static/uploads/sessions/{unique_filename}"

    # Processing Document Upload (Max 10MB)
    if doc_file and doc_file.filename:
        content = await doc_file.read()
        ext = validate_doc_upload(doc_file.filename, content, MAX_DOC_SIZE)
        if ext:
            unique_filename = f"doc_{uuid.uuid4().hex[:8]}{ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            with open(file_path, "wb") as f:
                f.write(content)
            document_url = f"/static/uploads/sessions/{unique_filename}"

    # If single class guest student selected from dropdown -> include in student_ids
    if single_class_guest_student_id and single_class_guest_student_id not in student_ids:
        student_ids.append(single_class_guest_student_id)

    # Process Aluno Avulso por Texto Livre
    if single_class_guest_name and single_class_guest_name.strip():
        guest_str = f"[Aluno Somente Esta Aula: {single_class_guest_name.strip()}]"
        notes = f"{notes}\n{guest_str}" if notes else guest_str

    session = ClassSession(
        schedule_id=schedule.id,
        dojo_id=schedule.dojo_id,
        date=date,
        instructor_sensei_id=schedule.instructor_sensei_id,
        notes=notes,
        photo_url=photo_url,
        document_url=document_url
    )
    db.add(session)
    db.commit()

    # Process attendance for selected students
    for st_id in student_ids:
        st = db.query(User).filter(User.id == st_id).first()
        if st:
            is_guest = (st.dojo_id != schedule.dojo_id) or (st_id == single_class_guest_student_id)
            att = Attendance(
                session_id=session.id,
                user_id=st.id,
                is_guest=is_guest,
                guest_approved=True
            )
            db.add(att)
            # Increment total attendances for student evolution tracking!
            st.total_attendances += 1
            # Check if student is ready for exam based on their belt rank requirements
            req_att = get_required_attendances(st.belt_rank)
            if st.total_attendances >= req_att:
                st.ready_for_exam = True

    db.commit()
    return RedirectResponse(url="/schedule", status_code=303)

@router.post("/api/guest-approvals/create")
def create_guest_approval(
    request: Request,
    student_id: int = Form(...),
    target_dojo_id: int = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        raise HTTPException(status_code=401, detail="Não autenticado.")

    # Aluno só pode solicitar para si mesmo; Sensei/Admin podem solicitar para qualquer aluno
    if current_user.get("role") == "STUDENT":
        student_id = int(current_user.get("sub"))

    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        return RedirectResponse(url="/schedule", status_code=303)

    # Find student's supervisor sensei
    supervisor_id = student.supervisor_sensei_id
    if not supervisor_id:
        # Fallback to any sensei if not set
        first_sensei = db.query(User).filter(User.role == "SENSEI").first()
        supervisor_id = first_sensei.id if first_sensei else student_id

    approval = GuestApproval(
        student_id=student.id,
        origin_dojo_id=student.dojo_id or target_dojo_id,
        target_dojo_id=target_dojo_id,
        sensei_id=supervisor_id,
        status="PENDING",
        notes=notes
    )
    db.add(approval)
    db.commit()
    return RedirectResponse(url="/schedule", status_code=303)

ALLOWED_APPROVAL_STATUSES = {"PENDING", "APPROVED", "REJECTED"}

@router.post("/api/guest-approvals/{approval_id}/status")
def update_guest_approval_status(approval_id: int, request: Request, status: str, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") not in ["ADMIN", "SENSEI"]:
        raise HTTPException(status_code=403, detail="Apenas Senseis e Administradores podem aprovar ou rejeitar solicitações de convidados.")

    status = (status or "").strip().upper()
    if status not in ALLOWED_APPROVAL_STATUSES:
        return JSONResponse({"error": "Status inválido. Use PENDING, APPROVED ou REJECTED."}, status_code=400)

    approval = db.query(GuestApproval).filter(GuestApproval.id == approval_id).first()
    if approval:
        approval.status = status
        db.commit()
        return JSONResponse({"status": "success", "approval_status": approval.status})
    return JSONResponse({"error": "Approval not found"}, status_code=404)
