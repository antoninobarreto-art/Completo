import sqlite3
import pandas as pd
from urllib.parse import quote
import os
import sys

# Ensure app package can be imported for hash_password if available, or fall back to bcrypt
BASE_DIR = r"C:\Users\DELL\OneDrive - Cerensa Tecnologia da Informação S A\Documentos\IA\Vibe Coding\TesteAplicacao"
sys.path.insert(0, BASE_DIR)

try:
    from app.security.auth import hash_password
except ImportError:
    import bcrypt
    def hash_password(password: str) -> str:
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

DB_PATH = os.path.join(BASE_DIR, "rioaiki.db")
EXCEL_PATH = r"C:\DOJOCHO\Arquivos originais\Alunos Dojoweb.xlsx"

def format_faixa(raw_grad):
    if pd.isna(raw_grad) or not str(raw_grad).strip():
        return "Mukyo (Branca)"
    
    val = str(raw_grad).strip()
    if "Amarela" in val:
        return "5º Kyu (Amarela)"
    elif "Roxa" in val:
        return "4º Kyu (Roxa)"
    elif "Verde" in val:
        return "3º Kyu (Verde)"
    elif "Azul" in val:
        return "2º Kyu (Azul)"
    elif "Marron" in val or "Marrom" in val:
        return "1º Kyu (Marrom)"
    elif "Shodan" in val or "1º dan" in val or "1° dan" in val:
        return "Shodan (1º Dan)"
    elif "Nidan" in val or "2º dan" in val or "2° dan" in val:
        return "Nidan (2º Dan)"
    elif "Sandan" in val or "3º dan" in val or "3° dan" in val:
        return "Sandan (3º Dan)"
    elif "Yondan" in val or "4º dan" in val or "4° dan" in val:
        return "Yondan (4º Dan)"
    elif "Mukyo" in val:
        return "Mukyo (Branca)"
    else:
        return val.replace("Aikidô: ", "")

def format_dojo_name(raw_grade, cidade):
    if not pd.isna(raw_grade) and str(raw_grade).strip():
        # Get primary dojo name from schedule string
        first_dojo = str(raw_grade).split(" e ")[0].split(",")[0].strip()
        return first_dojo
    elif not pd.isna(cidade) and str(cidade).strip():
        return f"RioAiki {str(cidade).strip()}"
    return "RioAiki Central - Botafogo"

def is_black_belt(raw_grad):
    if pd.isna(raw_grad) or not str(raw_grad).strip():
        return False
    val = str(raw_grad).upper()
    return "DAN" in val or "PRETA" in val or "SHIHAN" in val

def run_migration():
    print(f"=== INICIANDO MIGRAÇÃO DO DADOS PARA O SISTEMA DEFINITIVO (rioaiki.db) ===")
    print(f"Lendo planilha: {EXCEL_PATH}...")
    df = pd.read_excel(EXCEL_PATH)
    total_excel = len(df)
    print(f"Total de registros lidos no Excel: {total_excel}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")

    # 1. Obter ou Criar Dojos no rioaiki.db
    cursor.execute("SELECT id, name FROM dojos;")
    existing_dojos = {row[1].lower(): row[0] for row in cursor.fetchall()}

    # Check for sensei supervisor default
    cursor.execute("SELECT id FROM users WHERE role IN ('SENSEI', 'ADMIN') LIMIT 1;")
    sensei_row = cursor.fetchone()
    default_sensei_id = sensei_row[0] if sensei_row else 1

    # Default password hash for RioAiki@2026
    default_pwd_hash = hash_password("RioAiki@2026")

    # 2. Limpar registros dependentes e usuários importados anteriormente (id > 4)
    cursor.execute("DELETE FROM financial_transactions WHERE user_id > 4;")
    cursor.execute("DELETE FROM attendances WHERE user_id > 4;")
    cursor.execute("DELETE FROM event_presences WHERE user_id > 4;")
    cursor.execute("DELETE FROM guest_approvals WHERE student_id > 4 OR host_sensei_id > 4;")
    cursor.execute("DELETE FROM users WHERE id > 4;")
    cursor.execute("PRAGMA foreign_keys = ON;")
    print("Registros importados anteriores removidos com sucesso.")

    imported_count = 0
    active_count = 0
    inactive_count = 0
    sensei_imported_count = 0
    dojos_created = 0

    # Track used emails from base users (id <= 4)
    cursor.execute("SELECT LOWER(email) FROM users WHERE id <= 4 AND email IS NOT NULL;")
    used_emails = set(r[0] for r in cursor.fetchall() if r[0])

    # 3. Processar e Inserir os Alunos e Senseis
    for idx, row in df.iterrows():
        nome = str(row['Nome']).strip() if not pd.isna(row['Nome']) else f"Aluno {idx+1}"
        is_active = 1 if str(row.get('Situação')).strip() == "Ativo" else 0
        if is_active:
            active_count += 1
        else:
            inactive_count += 1

        faixa = format_faixa(row.get('Graduações'))
        dojo_name = format_dojo_name(row.get('Grade de Aulas'), row.get('Cidade'))
        role = "SENSEI" if is_black_belt(row.get('Graduações')) or is_black_belt(faixa) else "STUDENT"
        if role == "SENSEI":
            sensei_imported_count += 1

        # Check or insert Dojo
        dojo_key = dojo_name.lower()
        if dojo_key not in existing_dojos:
            cidade_dojo = str(row.get('Cidade', 'Rio de Janeiro')).strip() if not pd.isna(row.get('Cidade')) else "Rio de Janeiro"
            cursor.execute("""
                INSERT INTO dojos (name, address, city, description, responsible_sensei_id, created_at)
                VALUES (?, ?, ?, 'Dojo oficial filiado ao grupo RioAiki', ?, datetime('now'))
            """, (dojo_name, f"Endereço do {dojo_name}", cidade_dojo, default_sensei_id))
            new_dojo_id = cursor.lastrowid
            existing_dojos[dojo_key] = new_dojo_id
            dojos_created += 1

        dojo_id = existing_dojos[dojo_key]

        raw_email = str(row.get('Email')).strip().lower() if not pd.isna(row.get('Email')) else ""
        if not raw_email or "@" not in raw_email or raw_email in used_emails:
            prefix = "sensei" if role == "SENSEI" else "aluno"
            email = f"{prefix}_{idx+1}@rioaiki.com.br"
            counter = 1
            while email in used_emails:
                email = f"{prefix}_{idx+1}_{counter}@rioaiki.com.br"
                counter += 1
        else:
            email = raw_email

        used_emails.add(email)

        phone = str(row.get('Telefone')).strip() if not pd.isna(row.get('Telefone')) else None
        cpf = str(row.get('CPF')).strip() if not pd.isna(row.get('CPF')) else None
        birth = str(row.get('Nascimento', '2000-01-01'))[:10] if not pd.isna(row.get('Nascimento')) else "2000-01-01"
        photo = f"https://api.dicebear.com/7.x/avataaars/svg?seed={quote(nome)}"

        blood = str(row.get('Tipo Sanguineo')).strip() if not pd.isna(row.get('Tipo Sanguineo')) else None
        health_plan = str(row.get('Plano de Saúde')).strip() if not pd.isna(row.get('Plano de Saúde')) else None
        emerg_contact = str(row.get('Contato de emergência')).strip() if not pd.isna(row.get('Contato de emergência')) else None

        attendances = 45 if (is_active and "Kyu" in faixa) else 12
        ready_exam = 1 if (is_active and "Kyu" in faixa and idx % 3 == 0) else 0

        cursor.execute("""
            INSERT INTO users (
                name, email, role, belt_rank, dojo_id, supervisor_sensei_id,
                password_hash, is_active, phone, cpf_masked, photo_url,
                total_attendances, start_date, ready_for_exam, birth_date,
                blood_type, health_insurance, emergency_contact_name, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '2024-01-01', ?, ?, ?, ?, ?, datetime('now'))
        """, (
            nome, email, role, faixa, dojo_id, default_sensei_id,
            default_pwd_hash, is_active, phone, cpf, photo,
            attendances, ready_exam, birth, blood, health_plan, emerg_contact
        ))
        
        student_id = cursor.lastrowid
        imported_count += 1

        # 4. Gerar Mensalidade no Módulo Financeiro para Alunos ATIVOS
        if is_active:
            status_tx = "PAID" if (idx % 2 == 0) else "PENDING"
            desc_tx = f"Mensalidade 2026-08 - {nome}"
            cursor.execute("""
                INSERT INTO financial_transactions (
                    description, amount, type, category, dojo_id, user_id,
                    due_date, payment_date, status, payment_method, created_at
                ) VALUES (?, 350.00, 'INCOME', 'MENSALIDADE', ?, ?, '2026-08-10', ?, ?, 'PIX', datetime('now'))
            """, (desc_tx, dojo_id, student_id, '2026-08-05' if status_tx == 'PAID' else None, status_tx))

    conn.commit()
    conn.close()

    print(f"\n==================================================")
    print(f"=== MIGRAÇÃO CONCLUÍDA COM SUCESSO NO RIOAIKI.DB ===")
    print(f"==================================================")
    print(f"Total de Pessoas Importadas: {imported_count}")
    print(f" - Senseis (Faixa Preta / Dan): {sensei_imported_count}")
    print(f" - Alunos Regulares (Kyu / Branca): {imported_count - sensei_imported_count}")
    print(f" - Praticantes Ativos: {active_count}")
    print(f" - Praticantes Inativos: {inactive_count}")
    print(f"Novos Dojos Criados: {dojos_created}")
    print(f"Mensalidades Geradas (Praticantes Ativos): {active_count}")
    print(f"Senha Padrão Inicial definida para todos: RioAiki@2026")
    print(f"==================================================\n")

if __name__ == "__main__":
    run_migration()
