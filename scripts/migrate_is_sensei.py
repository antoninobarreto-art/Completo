import sqlite3
import os

RIOAIKI_DB = r"C:\Users\DELL\OneDrive - Cerensa Tecnologia da Informação S A\Documentos\IA\Vibe Coding\TesteAplicacao\rioaiki.db"
DOJOCHO_DB = r"C:\DOJOCHO\FinanceiroAntigravity\dojocho_finance.db"

def migrate_rioaiki_db():
    if not os.path.exists(RIOAIKI_DB):
        print(f"Banco {RIOAIKI_DB} não encontrado.")
        return

    conn = sqlite3.connect(RIOAIKI_DB)
    cursor = conn.cursor()

    # Check if is_sensei column exists in users
    cursor.execute("PRAGMA table_info(users)")
    cols = [col[1] for col in cursor.fetchall()]
    
    if "is_sensei" not in cols:
        print("Adicionando coluna is_sensei na tabela users de rioaiki.db...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_sensei BOOLEAN DEFAULT 0")
        conn.commit()

    # Update is_sensei = 1 and role = 'SENSEI' for all Faixa Preta
    cursor.execute("""
        UPDATE users
        SET is_sensei = 1,
            role = CASE WHEN role = 'ADMIN' THEN 'ADMIN' ELSE 'SENSEI' END
        WHERE belt_rank LIKE '%Dan%' 
           OR belt_rank LIKE '%Shihan%' 
           OR belt_rank LIKE '%Shodan%'
           OR belt_rank LIKE '%Nidan%'
           OR belt_rank LIKE '%Sandan%'
           OR belt_rank LIKE '%Yondan%'
           OR role IN ('SENSEI', 'ADMIN')
    """)
    updated = cursor.rowcount
    conn.commit()

    cursor.execute("SELECT count(*) FROM users WHERE is_sensei = 1 OR role IN ('SENSEI', 'ADMIN')")
    total_senseis = cursor.fetchone()[0]
    print(f"rioaiki.db: {updated} registros atualizados. Total de Senseis/Faixas Pretas agora: {total_senseis}")
    conn.close()

def migrate_dojocho_db():
    if not os.path.exists(DOJOCHO_DB):
        print(f"Banco {DOJOCHO_DB} não encontrado.")
        return

    conn = sqlite3.connect(DOJOCHO_DB)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(alunos)")
    cols = [col[1] for col in cursor.fetchall()]

    if "is_sensei" not in cols:
        print("Adicionando coluna is_sensei na tabela alunos de dojocho_finance.db...")
        cursor.execute("ALTER TABLE alunos ADD COLUMN is_sensei INTEGER DEFAULT 0")
        conn.commit()

    cursor.execute("""
        UPDATE alunos
        SET is_sensei = 1
        WHERE faixa LIKE '%Dan%' 
           OR faixa LIKE '%Shihan%'
           OR faixa LIKE '%Shodan%'
           OR faixa LIKE '%Nidan%'
           OR faixa LIKE '%Sandan%'
           OR faixa LIKE '%Yondan%'
    """)
    updated = cursor.rowcount
    conn.commit()

    cursor.execute("SELECT count(*) FROM alunos WHERE is_sensei = 1")
    total_senseis = cursor.fetchone()[0]
    print(f"dojocho_finance.db: {updated} registros atualizados. Total de Senseis/Faixas Pretas agora: {total_senseis}")
    conn.close()

if __name__ == "__main__":
    migrate_rioaiki_db()
    migrate_dojocho_db()
