from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import datetime
from app.database import get_db
from app.models import FinancialTransaction, Dojo, User, GuestApproval, Classified
from app.utils import format_date_br
from app.version import VERSION

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))
templates.env.filters["date_br"] = format_date_br
templates.env.globals["system_version"] = VERSION

@router.get("/financial")
@router.get("/financial/students")
@router.get("/financial/dojo")
@router.get("/financial/my-tuition")
def financial_page(
    request: Request,
    view: str = "students",
    status_filter: str = None,
    type_filter: str = None,
    dojo_filter: str = None,
    category_filter: str = None,
    payment_method_filter: str = None,
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    user_role = current_user.get("role")
    user_id = current_user.get("sub")
    user_dojo_id = current_user.get("dojo_id")

    path = request.url.path

    # Visão de Aluno (STUDENT)
    if user_role == "STUDENT" or "/financial/my-tuition" in path or view == "my_tuition":
        active_view = "my_tuition"
        db_user = db.query(User).filter(User.id == user_id).first()
        my_txs = db.query(FinancialTransaction).filter(FinancialTransaction.user_id == user_id).order_by(FinancialTransaction.created_at.desc()).all()
        
        pending_txs = [t for t in my_txs if t.status in ["PENDING", "OVERDUE"]]
        paid_txs = [t for t in my_txs if t.status == "PAID"]
        
        has_overdue = any(t.status == "OVERDUE" for t in my_txs)
        has_pending = any(t.status == "PENDING" for t in my_txs)
        
        if has_overdue:
            my_status = "OVERDUE"
        elif has_pending:
            my_status = "PENDING"
        else:
            my_status = "PAID"
            
        pending_amount = sum(t.amount for t in pending_txs)
        total_paid = sum(t.amount for t in paid_txs)

        pending_guests_count = db.query(GuestApproval).filter(GuestApproval.status == "PENDING").count()
        pending_classifieds_count = db.query(Classified).filter(Classified.status == "PENDING_SENSEI").count()

        return templates.TemplateResponse(request=request, name="page6_financial.html", context={
            "active_page": "financial",
            "active_view": "my_tuition",
            "db_user": db_user,
            "my_txs": my_txs,
            "pending_txs": pending_txs,
            "paid_txs": paid_txs,
            "my_status": my_status,
            "pending_amount": pending_amount,
            "total_paid": total_paid,
            "dojos": db.query(Dojo).all(),
            "students": [db_user],
            "pending_guests_count": pending_guests_count,
            "pending_classifieds_count": pending_classifieds_count,
            "current_user": current_user
        })

    # Permissão restrita a ADMIN e SENSEI para visões gerais
    if user_role not in ["ADMIN", "SENSEI"]:
        return RedirectResponse(url="/", status_code=303)

    # Determinar a visão ativa para Admin / Sensei
    if "/financial/dojo" in path or view == "dojo":
        active_view = "dojo"
    else:
        active_view = "students"

    # Sensei visualiza APENAS o seu dojo
    if user_role == "SENSEI" and user_dojo_id:
        dojos = db.query(Dojo).filter(Dojo.id == user_dojo_id).all()
        students_query = db.query(User).filter(User.role == "STUDENT", User.is_active == True, User.dojo_id == user_dojo_id)
        tx_query = db.query(FinancialTransaction).filter((FinancialTransaction.dojo_id == user_dojo_id) | (FinancialTransaction.dojo_id == None))
    else:
        dojos = db.query(Dojo).all()
        students_query = db.query(User).filter(User.role == "STUDENT", User.is_active == True)
        tx_query = db.query(FinancialTransaction)

    students = students_query.all()
    all_txs = tx_query.all()

    # -------------------------------------------------------------
    # 1. DADOS DA VISÃO ALUNOS (Informações Financeiras dos Alunos)
    # -------------------------------------------------------------
    student_txs = [t for t in all_txs if t.user_id is not None or t.category == "Mensalidade"]
    
    if status_filter and status_filter != "ALL":
        student_txs = [t for t in student_txs if t.status == status_filter]
    if dojo_filter and dojo_filter != "ALL":
        student_txs = [t for t in student_txs if t.dojo_id == int(dojo_filter)]
    if category_filter and category_filter != "ALL":
        student_txs = [t for t in student_txs if t.category == category_filter]
    if payment_method_filter and payment_method_filter != "ALL":
        student_txs = [t for t in student_txs if t.payment_method == payment_method_filter]

    # Construção do resumo financeiro por Aluno
    student_summaries = []
    total_mensalidades_pagas = 0.0
    total_mensalidades_pendentes = 0.0
    adimplentes_count = 0
    inadimplentes_count = 0

    for student in students:
        # Transações do aluno
        u_txs = [t for t in all_txs if t.user_id == student.id]
        pending_txs = [t for t in u_txs if t.status in ["PENDING", "OVERDUE"]]
        paid_txs = [t for t in u_txs if t.status == "PAID"]
        
        has_overdue = any(t.status == "OVERDUE" for t in u_txs)
        has_pending = any(t.status == "PENDING" for t in u_txs)

        if has_overdue or has_pending:
            fin_status = "OVERDUE" if has_overdue else "PENDING"
            inadimplentes_count += 1
        else:
            fin_status = "PAID"
            adimplentes_count += 1

        last_payment = paid_txs[0].payment_date if paid_txs else "Nenhum registro"
        total_paid_user = sum(t.amount for t in paid_txs)
        total_pending_user = sum(t.amount for t in pending_txs)

        total_mensalidades_pagas += total_paid_user
        total_mensalidades_pendentes += total_pending_user

        student_summaries.append({
            "user": student,
            "financial_status": fin_status,
            "pending_amount": total_pending_user,
            "total_paid": total_paid_user,
            "last_payment_date": last_payment,
            "transactions": u_txs
        })

    if status_filter and status_filter != "ALL":
        student_summaries = [s for s in student_summaries if s["financial_status"] == status_filter]

    # -------------------------------------------------------------
    # 2. DADOS DA VISÃO DOJO (Gestão Financeira & Custos do Dojo)
    # -------------------------------------------------------------
    dojo_txs = all_txs
    if status_filter and status_filter != "ALL":
        dojo_txs = [t for t in dojo_txs if t.status == status_filter]
    if type_filter and type_filter != "ALL":
        dojo_txs = [t for t in dojo_txs if t.type == type_filter]
    if dojo_filter and dojo_filter != "ALL":
        dojo_txs = [t for t in dojo_txs if t.dojo_id == int(dojo_filter)]
    if category_filter and category_filter != "ALL":
        dojo_txs = [t for t in dojo_txs if t.category == category_filter]
    if payment_method_filter and payment_method_filter != "ALL":
        dojo_txs = [t for t in dojo_txs if t.payment_method == payment_method_filter]

    receita_bruta_dojo = sum(t.amount for t in all_txs if t.type == "RECEITA" and t.status == "PAID")
    despesas_operacionais_dojo = sum(t.amount for t in all_txs if t.type == "DESPESA" and t.status == "PAID")
    lucro_liquido_dojo = receita_bruta_dojo - despesas_operacionais_dojo
    despesas_pendentes_dojo = sum(t.amount for t in all_txs if t.type == "DESPESA" and t.status in ["PENDING", "OVERDUE"])

    # Demostrativo por Dojo
    dojo_financial_breakdown = []
    for d in dojos:
        d_txs = [t for t in all_txs if t.dojo_id == d.id and t.status == "PAID"]
        d_rec = sum(t.amount for t in d_txs if t.type == "RECEITA")
        d_desp = sum(t.amount for t in d_txs if t.type == "DESPESA")
        dojo_financial_breakdown.append({
            "dojo": d,
            "receitas": d_rec,
            "despesas": d_desp,
            "saldo": d_rec - d_desp
        })

    pending_guests_count = db.query(GuestApproval).filter(GuestApproval.status == "PENDING").count()
    pending_classifieds_count = db.query(Classified).filter(Classified.status == "PENDING_SENSEI").count()

    return templates.TemplateResponse(request=request, name="page6_financial.html", context={
        "active_page": "financial",
        "active_view": active_view,
        
        # Dados da visão Alunos
        "student_summaries": student_summaries,
        "student_txs": student_txs,
        "total_mensalidades_pagas": total_mensalidades_pagas,
        "total_mensalidades_pendentes": total_mensalidades_pendentes,
        "adimplentes_count": adimplentes_count,
        "inadimplentes_count": inadimplentes_count,
        "total_alunos_count": len(students),
        
        # Dados da visão Dojo
        "dojo_txs": dojo_txs,
        "receita_bruta_dojo": receita_bruta_dojo,
        "despesas_operacionais_dojo": despesas_operacionais_dojo,
        "lucro_liquido_dojo": lucro_liquido_dojo,
        "despesas_pendentes_dojo": despesas_pendentes_dojo,
        "dojo_financial_breakdown": dojo_financial_breakdown,
        
        "dojos": dojos,
        "students": students,
        "status_filter": status_filter or "ALL",
        "type_filter": type_filter or "ALL",
        "dojo_filter": dojo_filter or "ALL",
        "category_filter": category_filter or "ALL",
        "payment_method_filter": payment_method_filter or "ALL",
        "pending_guests_count": pending_guests_count,
        "pending_classifieds_count": pending_classifieds_count,
        "current_user": current_user
    })


@router.post("/api/financial/create")
async def create_transaction(
    request: Request,
    description: str = Form(...),
    amount: float = Form(...),
    type: str = Form("RECEITA"),
    category: str = Form("Mensalidade"),
    dojo_id: str = Form(None),
    user_id: str = Form(None),
    due_date: str = Form(...),
    status: str = Form("PENDING"),
    payment_method: str = Form(None),
    notes: str = Form(None),
    redirect_view: str = Form("students"),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") not in ["ADMIN", "SENSEI"]:
        return JSONResponse({"detail": "Permissão negada."}, status_code=403)

    payment_date = datetime.date.today().strftime("%Y-%m-%d") if status == "PAID" else None

    d_id = int(dojo_id) if dojo_id and dojo_id != "" else None
    u_id = int(user_id) if user_id and user_id != "" else None

    transaction = FinancialTransaction(
        description=description,
        amount=amount,
        type=type,
        category=category,
        dojo_id=d_id,
        user_id=u_id,
        due_date=due_date,
        payment_date=payment_date,
        status=status,
        payment_method=payment_method if payment_method != "" else None,
        notes=notes if notes != "" else None
    )

    db.add(transaction)
    db.commit()
    return RedirectResponse(url=f"/financial?view={redirect_view}", status_code=303)


@router.post("/api/financial/{id}/toggle-status")
async def toggle_financial_status(
    id: int,
    request: Request,
    redirect_view: str = "students",
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") not in ["ADMIN", "SENSEI"]:
        return JSONResponse({"detail": "Permissão negada."}, status_code=403)

    tx = db.query(FinancialTransaction).filter(FinancialTransaction.id == id).first()
    if not tx:
        return JSONResponse({"detail": "Lançamento não encontrado."}, status_code=404)

    if tx.status == "PAID":
        tx.status = "PENDING"
        tx.payment_date = None
    else:
        tx.status = "PAID"
        tx.payment_date = datetime.date.today().strftime("%Y-%m-%d")

    db.commit()
    return RedirectResponse(url=f"/financial?view={redirect_view}", status_code=303)


@router.post("/api/financial/{id}/delete")
async def delete_transaction(
    id: int,
    request: Request,
    redirect_view: str = "students",
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") not in ["ADMIN", "SENSEI"]:
        return JSONResponse({"detail": "Permissão negada."}, status_code=403)

    tx = db.query(FinancialTransaction).filter(FinancialTransaction.id == id).first()
    if not tx:
        return JSONResponse({"detail": "Lançamento não encontrado."}, status_code=404)

    db.delete(tx)
    db.commit()
    return RedirectResponse(url=f"/financial?view={redirect_view}", status_code=303)


@router.post("/api/financial/generate-monthly-fees")
async def generate_monthly_fees(
    request: Request,
    month_year: str = Form(None),
    amount: float = Form(250.0),
    dojo_id: str = Form(None),
    due_day: str = Form("10"),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") not in ["ADMIN", "SENSEI"]:
        return JSONResponse({"detail": "Permissão negada."}, status_code=403)

    today = datetime.date.today()
    target_date_str = month_year or today.strftime("%m/%Y")
    
    # Formatação da data de vencimento: YYYY-MM-DD
    try:
        m, y = target_date_str.split("/")
        day_padded = str(due_day).zfill(2)
        due_date_str = f"{y}-{m}-{day_padded}"
    except Exception:
        due_date_str = today.strftime("%Y-%m-10")

    query_students = db.query(User).filter(User.role == "STUDENT", User.is_active == True)
    if dojo_id and dojo_id != "ALL" and dojo_id != "":
        query_students = query_students.filter(User.dojo_id == int(dojo_id))

    students = query_students.all()

    created_count = 0
    for student in students:
        desc = f"Mensalidade {target_date_str} - {student.name}"
        
        existing = db.query(FinancialTransaction).filter(
            FinancialTransaction.user_id == student.id,
            FinancialTransaction.description == desc
        ).first()

        if not existing:
            tx = FinancialTransaction(
                description=desc,
                amount=amount,
                type="RECEITA",
                category="Mensalidade",
                dojo_id=student.dojo_id,
                user_id=student.id,
                due_date=due_date_str,
                status="PENDING",
                notes=f"Mensalidade gerada em lote para o ciclo {target_date_str}."
            )
            db.add(tx)
            created_count += 1

    db.commit()
    return RedirectResponse(url="/financial?view=students", status_code=303)


@router.post("/api/financial/{id}/update")
async def update_transaction(
    id: int,
    request: Request,
    description: str = Form(...),
    amount: float = Form(...),
    type: str = Form("RECEITA"),
    category: str = Form("Mensalidade"),
    dojo_id: str = Form(None),
    user_id: str = Form(None),
    due_date: str = Form(...),
    status: str = Form("PENDING"),
    payment_method: str = Form(None),
    notes: str = Form(None),
    redirect_view: str = Form("students"),
    db: Session = Depends(get_db)
):
    current_user = getattr(request.state, "user", None)
    if not current_user or current_user.get("role") not in ["ADMIN", "SENSEI"]:
        return JSONResponse({"detail": "Permissão negada."}, status_code=403)

    tx = db.query(FinancialTransaction).filter(FinancialTransaction.id == id).first()
    if not tx:
        return JSONResponse({"detail": "Lançamento não encontrado."}, status_code=404)

    tx.description = description
    tx.amount = amount
    tx.type = type
    tx.category = category
    tx.dojo_id = int(dojo_id) if dojo_id and dojo_id != "" else None
    tx.user_id = int(user_id) if user_id and user_id != "" else None
    tx.due_date = due_date
    tx.status = status
    if status == "PAID" and not tx.payment_date:
        tx.payment_date = datetime.date.today().strftime("%Y-%m-%d")
    elif status != "PAID":
        tx.payment_date = None
    tx.payment_method = payment_method if payment_method != "" else None
    tx.notes = notes if notes != "" else None

    db.commit()
    return RedirectResponse(url=f"/financial?view={redirect_view}", status_code=303)

