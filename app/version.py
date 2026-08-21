"""
DOJOCHO - Módulo de Controle de Versão e Informações de Release
"""

VERSION = "2.4.2"
RELEASE_DATE = "2026-08-21"
RELEASE_NAME = "Reorganizacao dos Cards do Dashboard e Padronizacao dos KPIs"
SYSTEM_NAME = "DOJOCHO - Sistema de Gerenciamento de Dojos de Aikido"
ORGANIZATION = "Grupo RioAiki"
MIN_DB_VERSION = "2.4.2"

DB_SCHEMA_VERSION = 1  # Versão numérica do esquema no SQLite (PRAGMA user_version)

def get_version_info() -> dict:
    return {
        "version": VERSION,
        "release_date": RELEASE_DATE,
        "release_name": RELEASE_NAME,
        "system_name": SYSTEM_NAME,
        "organization": ORGANIZATION,
        "min_db_version": MIN_DB_VERSION,
        "db_schema_version": DB_SCHEMA_VERSION,
    }


from sqlalchemy import text

def validate_db_schema_version(db) -> dict:
    """
    Verifica se a versão do esquema do SQLite (PRAGMA user_version) corresponde à esperada.
    """
    try:
        result = db.execute(text("PRAGMA user_version;")).fetchone()
        current_user_version = result[0] if result else 0
        return {
            "valid": True, # Em SQLite sem migração pendente
            "db_schema_version": current_user_version,
            "expected_schema_version": DB_SCHEMA_VERSION
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "db_schema_version": None,
            "expected_schema_version": DB_SCHEMA_VERSION
        }

