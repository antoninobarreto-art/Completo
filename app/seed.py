import logging
from app.database import engine, Base, SessionLocal
from app.models import Dojo, User, ClassSchedule, ClassSession, Attendance, GuestApproval, Classified, Event, EventPresence, FinancialTransaction
from app.security.auth import hash_password
import datetime

logger = logging.getLogger(__name__)

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 1. Dojos
    dojo1 = Dojo(
        name="RioAiki Central - Botafogo",
        address="Rua Voluntários da Pátria, 210 - Botafogo, RJ",
        city="Rio de Janeiro",
        photo_url="https://images.unsplash.com/photo-1555597673-b21d5c935865?w=800",
        description="Sede central do Grupo RioAiki. Tatame de 150m², excelente ventilação e infraestrutura completa."
    )
    dojo2 = Dojo(
        name="RioAiki Norte - Tijuca",
        address="Rua Conde de Bonfim, 450 - Tijuca, RJ",
        city="Rio de Janeiro",
        photo_url="https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800",
        description="Dojo tradicional na Zona Norte. Foco em treinamento básico, avançado e armas (Bukitori)."
    )
    dojo3 = Dojo(
        name="RioAiki Oeste - Barra da Tijuca",
        address="Av. das Américas, 3500 - Barra da Tijuca, RJ",
        city="Rio de Janeiro",
        photo_url="https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800",
        description="Espaço amplo e moderno na Zona Oeste. Treinos matutinos, noturnos e aulas infantis."
    )

    db.add_all([dojo1, dojo2, dojo3])
    db.commit()

    # 2. Senseis & Usuários
    sensei1 = User(
        name="Carlos Wagner",
        email="carlos.wagner@rioaiki.com.br",
        role="SENSEI",
        belt_rank="6º Dan (Shihan)",
        dojo_id=dojo1.id,
        is_active=True,
        phone="(21) 99887-1122",
        cpf_masked="***.451.890-**",
        lgpd_consent=True,
        photo_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
        total_attendances=1450,
        last_exam_date="2020-11-15",
        ready_for_exam=False
    )
    sensei2 = User(
        name="Renata Lima",
        email="renata.lima@rioaiki.com.br",
        role="SENSEI",
        belt_rank="4º Dan",
        dojo_id=dojo2.id,
        is_active=True,
        phone="(21) 99776-3344",
        cpf_masked="***.210.778-**",
        lgpd_consent=True,
        photo_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80",
        total_attendances=980,
        last_exam_date="2022-05-10",
        ready_for_exam=False
    )
    sensei3 = User(
        name="Marcelo Santos",
        email="marcelo.santos@rioaiki.com.br",
        role="SENSEI",
        belt_rank="3º Dan",
        dojo_id=dojo3.id,
        is_active=True,
        phone="(21) 98822-5566",
        cpf_masked="***.889.334-**",
        lgpd_consent=True,
        photo_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
        total_attendances=720,
        last_exam_date="2023-01-20",
        ready_for_exam=False
    )

    db.add_all([sensei1, sensei2, sensei3])
    db.commit()

    # Link sensei1 as supervisor for senseis
    sensei2.supervisor_sensei_id = sensei1.id
    sensei3.supervisor_sensei_id = sensei1.id

    # Set responsible sensei for each dojo
    dojo1.responsible_sensei_id = sensei1.id
    dojo2.responsible_sensei_id = sensei2.id
    dojo3.responsible_sensei_id = sensei3.id

    db.commit()

    # Admin
    admin = User(
        name="Administrador RioAiki",
        email="admin@rioaiki.com.br",
        role="ADMIN",
        belt_rank="2º Dan",
        dojo_id=dojo1.id,
        supervisor_sensei_id=sensei1.id,
        is_active=True,
        phone="(21) 99000-0000",
        cpf_masked="***.000.111-**",
        lgpd_consent=True,
        photo_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=300&q=80",
        total_attendances=400,
        last_exam_date="2023-06-12",
        ready_for_exam=False
    )
    db.add(admin)
    db.commit()

    # Alunos (Botafogo, Tijuca, Barra)
    students = [
        # Botafogo Students
        User(
            name="Lucas Almeida",
            email="lucas.almeida@gmail.com",
            role="STUDENT",
            belt_rank="2º Kyu (Azul)",
            dojo_id=dojo1.id,
            supervisor_sensei_id=sensei1.id,
            is_active=True,
            phone="(21) 98111-2233",
            cpf_masked="***.321.654-**",
            lgpd_consent=True,
            photo_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
            total_attendances=142,
            last_exam_date="2025-06-10",
            ready_for_exam=True  # APTO A EXAME DE 1º KYU!
        ),
        User(
            name="Juliana Costa",
            email="juliana.costa@hotmail.com",
            role="STUDENT",
            belt_rank="5º Kyu (Amarela)",
            dojo_id=dojo1.id,
            supervisor_sensei_id=sensei1.id,
            is_active=True,
            phone="(21) 98222-3344",
            cpf_masked="***.987.123-**",
            lgpd_consent=True,
            photo_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80",
            total_attendances=48,
            last_exam_date="2025-11-20",
            ready_for_exam=True  # APTO A EXAME DE 4º KYU!
        ),
        User(
            name="Gabriel Oliveira",
            email="gabriel.oliveira@outlook.com",
            role="STUDENT",
            belt_rank="6º Kyu (Branca)",
            dojo_id=dojo1.id,
            supervisor_sensei_id=sensei1.id,
            is_active=True,
            phone="(21) 98333-4455",
            cpf_masked="***.654.789-**",
            lgpd_consent=True,
            photo_url="https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=300&q=80",
            total_attendances=15,
            last_exam_date=None,
            ready_for_exam=False
        ),
        
        # Tijuca Students
        User(
            name="Mariana Rocha",
            email="mariana.rocha@yahoo.com.br",
            role="STUDENT",
            belt_rank="1º Kyu (Marrom)",
            dojo_id=dojo2.id,
            supervisor_sensei_id=sensei2.id,
            is_active=True,
            phone="(21) 98444-5566",
            cpf_masked="***.112.334-**",
            lgpd_consent=True,
            photo_url="https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=80",
            total_attendances=210,
            last_exam_date="2024-12-01",
            ready_for_exam=True  # APTO A EXAME DE SHODAN (1º DAN)!
        ),
        User(
            name="Rodrigo Fernandes",
            email="rodrigo.fernandes@gmail.com",
            role="STUDENT",
            belt_rank="4º Kyu (Roxa)",
            dojo_id=dojo2.id,
            supervisor_sensei_id=sensei2.id,
            is_active=True,
            phone="(21) 98555-6677",
            cpf_masked="***.554.332-**",
            lgpd_consent=True,
            photo_url="https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=300&q=80",
            total_attendances=62,
            last_exam_date="2025-08-14",
            ready_for_exam=False
        ),
        User(
            name="Thiago Martins",
            email="thiago.martins@gmail.com",
            role="STUDENT",
            belt_rank="3º Kyu (Verde)",
            dojo_id=dojo2.id,
            supervisor_sensei_id=sensei2.id,
            is_active=False,  # ALUNO INATIVO
            phone="(21) 98666-7788",
            cpf_masked="***.776.554-**",
            lgpd_consent=True,
            photo_url="https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?auto=format&fit=crop&w=300&q=80",
            total_attendances=85,
            last_exam_date="2025-01-10",
            ready_for_exam=False
        ),

        # Barra Students
        User(
            name="Camila Silveira",
            email="camila.silveira@uol.com.br",
            role="STUDENT",
            belt_rank="3º Kyu (Verde)",
            dojo_id=dojo3.id,
            supervisor_sensei_id=sensei3.id,
            is_active=True,
            phone="(21) 98777-8899",
            cpf_masked="***.998.776-**",
            lgpd_consent=True,
            photo_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
            total_attendances=95,
            last_exam_date="2025-03-22",
            ready_for_exam=True  # APTO A EXAME DE 2º KYU!
        ),
        User(
            name="Bruno Mendonça",
            email="bruno.mendonca@gmail.com",
            role="STUDENT",
            belt_rank="6º Kyu (Branca)",
            dojo_id=dojo3.id,
            supervisor_sensei_id=sensei3.id,
            is_active=True,
            phone="(21) 98888-9900",
            cpf_masked="***.334.556-**",
            lgpd_consent=True,
            photo_url="https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=300&q=80",
            total_attendances=8,
            last_exam_date=None,
            ready_for_exam=False
        )
    ]

    db.add_all(students)
    db.commit()

    # 3. Grade Semanal de Aulas (ClassSchedules)
    schedules = [
        # Botafogo
        ClassSchedule(dojo_id=dojo1.id, instructor_sensei_id=sensei1.id, weekday="Segunda", start_time="07:00", end_time="08:15", title="Aikido Matutino", level="Todos os Níveis"),
        ClassSchedule(dojo_id=dojo1.id, instructor_sensei_id=sensei1.id, weekday="Segunda", start_time="19:30", end_time="21:00", title="Aikido Geral & Kihon", level="Todos os Níveis"),
        ClassSchedule(dojo_id=dojo1.id, instructor_sensei_id=sensei1.id, weekday="Quarta", start_time="19:30", end_time="21:00", title="Armas (Bokken & Jo)", level="Intermediário / Avançado"),
        ClassSchedule(dojo_id=dojo1.id, instructor_sensei_id=sensei1.id, weekday="Sábado", start_time="10:00", end_time="12:00", title="Treino Geral do Grupo RioAiki", level="Todos os Níveis"),
        
        # Tijuca
        ClassSchedule(dojo_id=dojo2.id, instructor_sensei_id=sensei2.id, weekday="Terça", start_time="19:00", end_time="20:30", title="Aikido Fundamentos", level="Iniciantes & Intermediários"),
        ClassSchedule(dojo_id=dojo2.id, instructor_sensei_id=sensei2.id, weekday="Quinta", start_time="19:00", end_time="20:30", title="Aikido Waza & Kaeshiwaza", level="Todos os Níveis"),
        ClassSchedule(dojo_id=dojo2.id, instructor_sensei_id=sensei2.id, weekday="Sábado", start_time="09:00", end_time="10:30", title="Aikido & Bukiwaza", level="Todos os Níveis"),

        # Barra
        ClassSchedule(dojo_id=dojo3.id, instructor_sensei_id=sensei3.id, weekday="Segunda", start_time="20:00", end_time="21:30", title="Aikido Zenshin", level="Todos os Níveis"),
        ClassSchedule(dojo_id=dojo3.id, instructor_sensei_id=sensei3.id, weekday="Quarta", start_time="20:00", end_time="21:30", title="Aikido & Jiyuwaza", level="Todos os Níveis"),
        ClassSchedule(dojo_id=dojo3.id, instructor_sensei_id=sensei3.id, weekday="Sexta", start_time="19:30", end_time="21:00", title="Armas & Preparatório Exames", level="Graduados")
    ]
    db.add_all(schedules)
    db.commit()

    # 4. Aulas Realizadas (ClassSession) & Presenças (Attendance)
    session1 = ClassSession(
        schedule_id=schedules[1].id, # Botafogo Segunda 19:30
        dojo_id=dojo1.id,
        date="2026-07-20",
        instructor_sensei_id=sensei1.id,
        notes="Treino focado em Katatetori Ikkyo e Shiho-nage. Excelente participação."
    )
    session2 = ClassSession(
        schedule_id=schedules[4].id, # Tijuca Terça 19:00
        dojo_id=dojo2.id,
        date="2026-07-21",
        instructor_sensei_id=sensei2.id,
        notes="Revisão detalhada de Ushiro Tekoritori e Kokiho."
    )
    db.add_all([session1, session2])
    db.commit()

    # Presenças da Session 1 (Botafogo)
    lucas = students[0]
    juliana = students[1]
    gabriel = students[2]
    mariana = students[3] # Convidada da Tijuca!

    att1 = Attendance(session_id=session1.id, user_id=lucas.id, is_guest=False, guest_approved=True)
    att2 = Attendance(session_id=session1.id, user_id=juliana.id, is_guest=False, guest_approved=True)
    att3 = Attendance(session_id=session1.id, user_id=gabriel.id, is_guest=False, guest_approved=True)
    att4 = Attendance(session_id=session1.id, user_id=mariana.id, is_guest=True, guest_approved=True)

    db.add_all([att1, att2, att3, att4])
    db.commit()

    # 5. Solicitações de Alunos Convidados (GuestApproval)
    # Exemplo: Mariana (da Tijuca) pediu autorização para fazer aula extra no Dojo Botafogo
    guest1 = GuestApproval(
        student_id=mariana.id,
        origin_dojo_id=dojo2.id,
        target_dojo_id=dojo1.id,
        sensei_id=sensei2.id, # Sensei Renata da Tijuca
        status="APPROVED",
        notes="Autorizada para treinos às segundas e quartas na sede.",
        requested_at=datetime.datetime.now() - datetime.timedelta(days=5)
    )
    
    # Exemplo PENDENTE: Lucas (de Botafogo) pediu autorização para treinar no Dojo Barra com o Sensei Marcelo
    guest2 = GuestApproval(
        student_id=lucas.id,
        origin_dojo_id=dojo1.id,
        target_dojo_id=dojo3.id,
        sensei_id=sensei1.id, # Sensei Carlos Wagner de Botafogo
        status="PENDING", # PENDENTE DE APROVAÇÃO DO SENSEI CARLOS WAGNER!
        notes="Treinos de Sexta à noite visando preparação para exame de 1º Kyu.",
        requested_at=datetime.datetime.now() - datetime.timedelta(days=1)
    )

    # Exemplo PENDENTE: Camila (da Barra) pediu autorização para treinar no Dojo Tijuca
    guest3 = GuestApproval(
        student_id=students[6].id, # Camila
        origin_dojo_id=dojo3.id,
        target_dojo_id=dojo2.id,
        sensei_id=sensei3.id, # Sensei Marcelo
        status="PENDING",
        notes="Ajuste de horário de trabalho.",
        requested_at=datetime.datetime.now() - datetime.timedelta(hours=6)
    )

    db.add_all([guest1, guest2, guest3])
    db.commit()

    # 6. Mural de Classificados (Classifieds)
    c1 = Classified(
        author_id=lucas.id,
        title="Dogi de Aikido Meiji Keikogi (Tamanho A3)",
        description="Dogi trançado reforçado para Aikido, pouquíssimo uso. Ideal para praticantes de 1,75m a 1,85m.",
        category="Dogi/Kimono",
        price=280.0,
        photo_url="https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=400&q=80",
        status="APPROVED",
        created_at=datetime.datetime.now() - datetime.timedelta(days=3)
    )
    c2 = Classified(
        author_id=sensei2.id,
        title="Bokken de Carvalho Vermelho Japonês + Saya",
        description="Espada de madeira importada para prática de Bukiwaza. Equilíbrio perfeito e excelente acabamento.",
        category="Armas (Bokken/Jo/Tanto)",
        price=350.0,
        photo_url="https://images.unsplash.com/photo-1595590424283-b8f17842773f?auto=format&fit=crop&w=400&q=80",
        status="APPROVED",
        created_at=datetime.datetime.now() - datetime.timedelta(days=2)
    )
    c3 = Classified(
        author_id=juliana.id,
        title="Hakama Azul Marinho Iwata (Tamanho 25)",
        description="Hakama tradicional de poliéster/algodão marca Iwata original. Usado poucas vezes, sem marcas.",
        category="Acessórios",
        price=420.0,
        photo_url="https://images.unsplash.com/photo-1583473848882-f9a5bc7fd2ee?auto=format&fit=crop&w=400&q=80",
        status="PENDING_SENSEI", # PENDENTE DE APROVAÇÃO DO SENSEI CARLOS WAGNER!
        created_at=datetime.datetime.now() - datetime.timedelta(hours=4)
    )
    c4 = Classified(
        author_id=students[4].id, # Rodrigo
        title="Livro 'O Espírito do Aikido' - Kisshomaru Ueshiba",
        description="Livro raro de fundamentação teórica e filosófica do Aikido. Edição em português conservada.",
        category="Livros/Mídia",
        price=60.0,
        photo_url="https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=400&q=80",
        status="PENDING_SENSEI", # PENDENTE DE APROVAÇÃO DA SENSEI RENATA!
        created_at=datetime.datetime.now() - datetime.timedelta(hours=12)
    )

    db.add_all([c1, c2, c3, c4])
    db.commit()

    # 7. Eventos (Events)
    e1 = Event(
        title="Seminário de Primavera RioAiki 2026",
        description="Seminário intensivo de primavera unindo todos os dojos do grupo RioAiki. Estudo aprofundado de Ukemi, Suwariwaza e aplicação prática de Aiki-jo.",
        date_time="2026-09-12 09:00",
        location="RioAiki Central - Botafogo (Rua Voluntários da Pátria, 210)",
        main_sensei_id=sensei1.id,
        assistant_senseis="Renata Lima (4º Dan), Marcelo Santos (3º Dan)",
        photo_url="https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80",
        price=150.0,
        status="UPCOMING"
    )
    e2 = Event(
        title="Exame Geral de Graduação Kyu & Dan",
        description="Sessão oficial de exames de graduação para alunos aptos pré-autorizados pelos seus respectivos Senseis de dojo.",
        date_time="2026-10-24 14:00",
        location="RioAiki Central - Botafogo",
        main_sensei_id=sensei1.id,
        assistant_senseis="Banca Examinadora RioAiki",
        photo_url="https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=800&q=80",
        price=80.0,
        status="UPCOMING"
    )
    e3 = Event(
        title="Gasshuku de Verão na Serra (Petrópolis)",
        description="Retiro de treinamento imersivo no final de semana na serra. Meditação zazen, treinos ao ar livre de armas e confraternização.",
        date_time="2026-11-20 08:00",
        location="Pousada Recanto da Serra - Petrópolis, RJ",
        main_sensei_id=sensei2.id,
        assistant_senseis="Carlos Wagner, Marcelo Santos",
        photo_url="https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=800&q=80",
        price=380.0,
        status="UPCOMING"
    )

    db.add_all([e1, e2, e3])
    db.commit()

    # Presença no evento e1
    p1 = EventPresence(event_id=e1.id, user_id=lucas.id, status="CONFIRMED")
    p2 = EventPresence(event_id=e1.id, user_id=mariana.id, status="CONFIRMED")
    p3 = EventPresence(event_id=e1.id, user_id=juliana.id, status="CONFIRMED")
    db.add_all([p1, p2, p3])
    db.commit()

    # Lançamentos Financeiros Seed
    financial_seeds = [
        FinancialTransaction(
            description="Mensalidade Julho/2026 - Lucas Almeida",
            amount=250.0,
            type="RECEITA",
            category="Mensalidade",
            dojo_id=dojo1.id,
            user_id=lucas.id,
            due_date="2026-07-10",
            payment_date="2026-07-08",
            status="PAID",
            payment_method="PIX",
            notes="Pago em dia via PIX com comprovante anexo."
        ),
        FinancialTransaction(
            description="Mensalidade Julho/2026 - Mariana Costa",
            amount=250.0,
            type="RECEITA",
            category="Mensalidade",
            dojo_id=dojo1.id,
            user_id=mariana.id,
            due_date="2026-07-10",
            payment_date="2026-07-10",
            status="PAID",
            payment_method="Cartão",
            notes="Mensalidade recorrente aprovada."
        ),
        FinancialTransaction(
            description="Mensalidade Julho/2026 - Juliana Mendes",
            amount=230.0,
            type="RECEITA",
            category="Mensalidade",
            dojo_id=dojo2.id,
            user_id=juliana.id,
            due_date="2026-07-15",
            payment_date=None,
            status="OVERDUE",
            payment_method=None,
            notes="Aguardando confirmação de transferência."
        ),
        FinancialTransaction(
            description="Mensalidade Julho/2026 - Gabriel Santos",
            amount=250.0,
            type="RECEITA",
            category="Mensalidade",
            dojo_id=dojo3.id,
            user_id=gabriel.id,
            due_date="2026-07-28",
            payment_date=None,
            status="PENDING",
            payment_method=None,
            notes="Vencimento próximo."
        ),
        FinancialTransaction(
            description="Aluguel de Tatame e Espaço - Botafogo",
            amount=1200.0,
            type="DESPESA",
            category="Aluguel Tatame",
            dojo_id=dojo1.id,
            user_id=None,
            due_date="2026-07-05",
            payment_date="2026-07-04",
            status="PAID",
            payment_method="PIX",
            notes="Aluguel mensal da sede Botafogo quitado."
        ),
        FinancialTransaction(
            description="Manutenção Tatames e Limpeza Especializada - Tijuca",
            amount=350.0,
            type="DESPESA",
            category="Equipamentos",
            dojo_id=dojo2.id,
            user_id=None,
            due_date="2026-07-12",
            payment_date="2026-07-12",
            status="PAID",
            payment_method="Transferência",
            notes="Higienização de tatames."
        ),
        FinancialTransaction(
            description="Taxa de Inscrição Exame de Faixa - Lucas Almeida",
            amount=150.0,
            type="RECEITA",
            category="Exame de Faixa",
            dojo_id=dojo1.id,
            user_id=lucas.id,
            due_date="2026-07-20",
            payment_date="2026-07-18",
            status="PAID",
            payment_method="PIX",
            notes="Taxa de exame para 2º Kyu."
        ),
        FinancialTransaction(
            description="Aquisição de Armas de Treino (Bokken & Jo)",
            amount=480.0,
            type="DESPESA",
            category="Equipamentos",
            dojo_id=dojo1.id,
            user_id=None,
            due_date="2026-07-25",
            payment_date=None,
            status="PENDING",
            payment_method="Boleto",
            notes="Pedido de 5 conjuntos de bokken e jo para o dojo central."
        )
    ]
    db.add_all(financial_seeds)
    db.commit()

    # Definir senha padrão para todos os usuários seeded
    default_admin_hash = hash_password("admin123")
    default_user_hash = hash_password("123456")
    all_users = db.query(User).all()
    for u in all_users:
        if not u.password_hash:
            u.password_hash = default_admin_hash if u.role == "ADMIN" else default_user_hash
    db.commit()

    db.close()
    logger.info("Database RioAiki populated successfully with initial seed data!")

if __name__ == "__main__":
    init_db()
    seed_data()
