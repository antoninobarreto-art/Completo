import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class Dojo(Base):
    __tablename__ = "dojos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    academy = Column(String, nullable=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False, default="Rio de Janeiro")
    photo_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    responsible_sensei_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    responsible_sensei = relationship("User", foreign_keys=[responsible_sensei_id])
    members = relationship("User", back_populates="dojo", foreign_keys="User.dojo_id")
    schedules = relationship("ClassSchedule", back_populates="dojo", cascade="all, delete-orphan")
    sessions = relationship("ClassSession", back_populates="dojo", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False, default="STUDENT")  # ADMIN, SENSEI, STUDENT
    is_sensei = Column(Boolean, default=False)
    belt_rank = Column(String, nullable=False, default="6º Kyu")  # Kyu or Dan
    dojo_id = Column(Integer, ForeignKey("dojos.id"), index=True, nullable=True)
    supervisor_sensei_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    
    password_hash = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    phone = Column(String, nullable=True)
    cpf_masked = Column(String, nullable=True)  # LGPD masked e.g. ***.123.456-**
    lgpd_consent = Column(Boolean, default=True)
    photo_url = Column(String, nullable=True)
    
    total_attendances = Column(Integer, default=0)
    start_date = Column(String, nullable=True)  # Data de Início no Dojo YYYY-MM-DD
    last_exam_date = Column(String, nullable=True)  # Data do Último Exame YYYY-MM-DD
    ready_for_exam = Column(Boolean, default=False)
    birth_date = Column(String, nullable=True)  # Data de Nascimento DD/MM

    # Informações Médicas e LGPD
    blood_type = Column(String, nullable=True, default="Não Informado")
    health_insurance = Column(String, nullable=True)
    medical_notes = Column(Text, nullable=True)
    blood_transfusion_approved = Column(Boolean, default=True)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)

    # Recuperação de Senha
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=utc_now)

    # Relationships
    dojo = relationship("Dojo", back_populates="members", foreign_keys=[dojo_id])
    supervisor_sensei = relationship("User", remote_side=[id], foreign_keys=[supervisor_sensei_id])
    
    attendances = relationship("Attendance", back_populates="user", cascade="all, delete-orphan")
    classifieds = relationship("Classified", back_populates="author", cascade="all, delete-orphan")
    guest_requests = relationship("GuestApproval", back_populates="student", foreign_keys="GuestApproval.student_id")


class ClassSchedule(Base):
    __tablename__ = "class_schedules"

    id = Column(Integer, primary_key=True, index=True)
    dojo_id = Column(Integer, ForeignKey("dojos.id"), index=True, nullable=False)
    instructor_sensei_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    weekday = Column(String, nullable=False)  # Segunda, Terça, Quarta, Quinta, Sexta, Sábado, Domingo
    start_time = Column(String, nullable=False)  # HH:MM
    end_time = Column(String, nullable=False)    # HH:MM
    title = Column(String, nullable=False)       # Aikido Geral, Aikido Infantil, Weapons/Bukiwaza, Advanced
    level = Column(String, default="Todos os Níveis")

    dojo = relationship("Dojo", back_populates="schedules")
    instructor = relationship("User", foreign_keys=[instructor_sensei_id])
    sessions = relationship("ClassSession", back_populates="schedule", cascade="all, delete-orphan")


class ClassSession(Base):
    __tablename__ = "class_sessions"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("class_schedules.id"), index=True, nullable=True)
    dojo_id = Column(Integer, ForeignKey("dojos.id"), index=True, nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD
    instructor_sensei_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    notes = Column(Text, nullable=True)
    photo_url = Column(String, nullable=True)      # Foto da aula/treino
    document_url = Column(String, nullable=True)   # Plano de aula / Documento PDF/TXT
    created_at = Column(DateTime, default=utc_now)

    schedule = relationship("ClassSchedule", back_populates="sessions")
    dojo = relationship("Dojo", back_populates="sessions")
    instructor = relationship("User", foreign_keys=[instructor_sensei_id])
    attendances = relationship("Attendance", back_populates="session", cascade="all, delete-orphan")


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    is_guest = Column(Boolean, default=False)
    guest_approved = Column(Boolean, default=True)  # If local student -> True, if guest -> requires approval
    created_at = Column(DateTime, default=utc_now)

    session = relationship("ClassSession", back_populates="attendances")
    user = relationship("User", back_populates="attendances")


class GuestApproval(Base):
    __tablename__ = "guest_approvals"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    origin_dojo_id = Column(Integer, ForeignKey("dojos.id"), index=True, nullable=False)
    target_dojo_id = Column(Integer, ForeignKey("dojos.id"), index=True, nullable=False)
    sensei_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)  # Student's sensei who approves
    status = Column(String, default="PENDING")  # PENDING, APPROVED, REJECTED
    notes = Column(Text, nullable=True)
    requested_at = Column(DateTime, default=utc_now)

    student = relationship("User", foreign_keys=[student_id], back_populates="guest_requests")
    origin_dojo = relationship("Dojo", foreign_keys=[origin_dojo_id])
    target_dojo = relationship("Dojo", foreign_keys=[target_dojo_id])
    sensei = relationship("User", foreign_keys=[sensei_id])


class Classified(Base):
    __tablename__ = "classifieds"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # Dogi/Kimono, Armas, Mídia, Outros
    price = Column(Float, nullable=False, default=0.0)
    photo_url = Column(String, nullable=True)
    status = Column(String, default="PENDING_SENSEI")  # PENDING_SENSEI, APPROVED, REJECTED
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    author = relationship("User", back_populates="classifieds")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    date_time = Column(String, nullable=False)  # YYYY-MM-DD HH:MM
    location = Column(String, nullable=False)
    main_sensei_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    assistant_senseis = Column(String, nullable=True)  # Comma separated names
    photo_url = Column(String, nullable=True)
    price = Column(Float, default=0.0)
    status = Column(String, default="UPCOMING")  # UPCOMING, COMPLETED, CANCELLED

    main_sensei = relationship("User", foreign_keys=[main_sensei_id])
    presences = relationship("EventPresence", back_populates="event", cascade="all, delete-orphan")
    tasks = relationship("EventTask", back_populates="event", cascade="all, delete-orphan")
    external_participants = relationship("EventExternalParticipant", back_populates="event", cascade="all, delete-orphan")


class EventPresence(Base):
    __tablename__ = "event_presences"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    status = Column(String, default="CONFIRMED")  # CONFIRMED, PENDING

    event = relationship("Event", back_populates="presences")
    user = relationship("User", foreign_keys=[user_id])


class EventTask(Base):
    __tablename__ = "event_tasks"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), index=True, nullable=False)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    description = Column(String, nullable=False)
    due_date = Column(String, nullable=True)  # Data e hora de realização
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    event = relationship("Event", back_populates="tasks")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])


class EventExternalParticipant(Base):
    __tablename__ = "event_external_participants"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    dojo = Column(String, nullable=True)
    association = Column(String, nullable=True)
    belt_rank = Column(String, nullable=True)
    is_present = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    event = relationship("Event", back_populates="external_participants")


class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    type = Column(String, nullable=False, default="RECEITA")  # RECEITA, DESPESA
    category = Column(String, nullable=False, default="Mensalidade")  # Mensalidade, Exame de Faixa, Aluguel Tatame, Equipamentos, Eventos, Outros
    
    dojo_id = Column(Integer, ForeignKey("dojos.id"), index=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    
    due_date = Column(String, nullable=False)        # YYYY-MM-DD
    payment_date = Column(String, nullable=True)     # YYYY-MM-DD
    status = Column(String, default="PENDING")       # PAID, PENDING, OVERDUE
    payment_method = Column(String, nullable=True)   # PIX, Cartão, Boleto, Dinheiro, Transferência
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    dojo = relationship("Dojo", foreign_keys=[dojo_id])
    user = relationship("User", foreign_keys=[user_id])


