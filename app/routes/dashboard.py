from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import re
import datetime

from app.database import get_db
from app.models import Dojo, User, GuestApproval, Classified, Event

from app.utils import get_required_attendances
from app.version import VERSION

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))
templates.env.filters["req_attendances"] = get_required_attendances
templates.env.globals["system_version"] = VERSION

@router.get("/")
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    current_user = getattr(request.state, "user", None)
    is_student = current_user and current_user.get("role") == "STUDENT"
    user_id = int(current_user.get("sub")) if current_user and current_user.get("sub") else None

    dojos = db.query(Dojo).all()
    active_students_count = db.query(User).filter(User.role == "STUDENT", User.is_active == True).count()
    inactive_students_count = db.query(User).filter(User.role == "STUDENT", User.is_active == False).count()
    
    if is_student and user_id:
        # Para ALUNOS: filtra apenas as suas próprias informações
        ready_for_exam = db.query(User).filter(User.id == user_id, User.ready_for_exam == True, User.is_active == True).all()
        pending_guests = db.query(GuestApproval).filter(GuestApproval.student_id == user_id, GuestApproval.status == "PENDING").all()
        pending_classifieds = db.query(Classified).filter(Classified.author_id == user_id, Classified.status == "PENDING_SENSEI").all()
        student_obj = db.query(User).filter(User.id == user_id).first()
    else:
        # Para SENSEI e ADMIN: visão gerencial completa
        ready_for_exam = db.query(User).filter(User.ready_for_exam == True, User.is_active == True).all()
        pending_guests = db.query(GuestApproval).filter(GuestApproval.status == "PENDING").all()
        pending_classifieds = db.query(Classified).filter(Classified.status == "PENDING_SENSEI").all()
        student_obj = None

    # Read graduacao.txt for class requirements per rank
    grad_requirements = {}
    grad_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "arquivos", "graduação.txt")
    if os.path.exists(grad_file):
        with open(grad_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "-" in line:
                    parts = re.split(r'\s*-\s*', line)
                    if len(parts) >= 2:
                        req_val = parts[-1].strip()
                        rank_key = " - ".join(parts[:-1]).strip().lower()
                        grad_requirements[rank_key] = req_val

    def get_req_for_rank(rank_str):
        if not rank_str:
            return None
        r_lower = rank_str.lower().replace("º", "").replace("°", "")
        for k, v in grad_requirements.items():
            k_clean = k.replace("º", "").replace("°", "")
            if k_clean in r_lower or r_lower in k_clean:
                return v
        for term in ['5 kyu', '4 kyu', '3 kyu', '2 kyu', '1 kyu', '6 kyu', 'shodan', 'nidan', 'sandan', 'yondan', 'godan', 'rokudan', '1 dan', '2 dan', '3 dan', '4 dan', '5 dan', '6 dan']:
            if term in r_lower:
                for k, v in grad_requirements.items():
                    k_clean = k.replace("º", "").replace("°", "")
                    if term in k_clean:
                        return v
        return None

    # Read Exames de Faixa Seimeikan.txt for detailed exam technique syllabus per rank
    syllabus_dict = {}
    exam_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "arquivos", "Exames de Faixa Seimeikan.txt")
    if os.path.exists(exam_file):
        with open(exam_file, encoding="utf-8", errors="ignore") as f:
            text = f.read()
        header_regex = re.compile(r'^(\d+\s*(?:Kyu|Dan).*)', re.IGNORECASE | re.MULTILINE)
        matches = list(header_regex.finditer(text))
        for i in range(len(matches)):
            start_pos = matches[i].end()
            end_pos = matches[i+1].start() if i + 1 < len(matches) else len(text)
            header_text = matches[i].group(1).strip()
            body_text = text[start_pos:end_pos].strip()
            syllabus_dict[header_text.lower()] = body_text

    def get_syllabus_for_rank(rank_str):
        r_lower = rank_str.lower()
        for k, v in syllabus_dict.items():
            if r_lower in k or k in r_lower:
                return v
            for term in ['5 kyu', '5º kyu', '4 kyu', '4º kyu', '3 kyu', '3º kyu', '2 kyu', '2º kyu', '1 kyu', '1º kyu', '1 dan', '1º dan', '2 dan', '2º dan', '3 dan', '3º dan', '4 dan', '4º dan']:
                term_clean = term.replace('º', '')
                r_clean = r_lower.replace('º', '')
                if term_clean in r_clean and term_clean in k.replace('º', ''):
                    return v
        return ""

    BELT_VIDEOS = {
        "amarela": "https://youtu.be/9WzlyxkNfGk?si=0hdtoFr1fzoQ76FL",
        "roxa": "https://youtu.be/vhFXjsgAYAM?si=Rw9zlGSbiNH5tiCg",
        "verde": "https://youtu.be/PaAW_EuTaNA?si=fWuRtH2kyrTJ38JT",
        "azul": "https://youtu.be/e8et5X3L5fw?si=JdOGdTkRjJEnBmob",
        "marrom": "https://youtu.be/dM2VWw1WQpI?si=wfntqdtgSgHlj4Bl"
    }

    def get_video_for_rank(color_str):
        c_lower = color_str.lower()
        for k, v in BELT_VIDEOS.items():
            if k in c_lower:
                return v
        return ""

    # Read cores da faixa.txt
    belt_colors_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "arquivos", "cores da faixa.txt")
    belt_colors_list = []
    if os.path.exists(belt_colors_file):
        with open(belt_colors_file, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            for line in lines[1:]:  # Skip header line
                if "-" in line:
                    parts = re.split(r'\s*-\s*', line, maxsplit=1)
                    if len(parts) == 2:
                        rank = parts[0].strip()
                        color = parts[1].strip()
                        req = get_req_for_rank(rank)
                        syll = get_syllabus_for_rank(rank)
                        vid = get_video_for_rank(color)
                        belt_colors_list.append({"rank": rank, "color": color, "requirements": req, "syllabus": syll, "video_url": vid})

    for student in ready_for_exam:
        req_num = get_required_attendances(student.belt_rank)
        setattr(student, "req_attendances", req_num)

    events = db.query(Event).all()

    # Aniversariantes do mês
    mes_atual = f"/{datetime.date.today().strftime('%m')}"
    aniversariantes = (
        db.query(User)
        .filter(
            User.birth_date.isnot(None),
            User.birth_date != "",
            User.birth_date.like(f"%{mes_atual}"),
            User.is_active == True
        )
        .order_by(User.birth_date)
        .all()
    )

    return templates.TemplateResponse(request=request, name="page1_dashboard.html", context={
        "active_page": "dashboard",
        "dojos_count": len(dojos),
        "active_students_count": active_students_count,
        "inactive_students_count": inactive_students_count,
        "ready_for_exam": ready_for_exam,
        "pending_guests": pending_guests,
        "pending_classifieds": pending_classifieds,
        "pending_guests_count": len(pending_guests),
        "pending_classifieds_count": len(pending_classifieds),
        "events": events,
        "dojos": dojos,
        "belt_colors_list": belt_colors_list,
        "student_obj": student_obj,
        "aniversariantes": aniversariantes,
        "current_user": getattr(request.state, "user", None)
    })
