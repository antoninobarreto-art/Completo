"""
DOJOCHO - Módulo de Controle de Versão e Informações de Release
"""

VERSION = "2.2.1"
RELEASE_DATE = "2026-08-13"
RELEASE_NAME = "Mobile UX, Botão de Tema & Correções Visuais"
SYSTEM_NAME = "DOJOCHO - Sistema de Gerenciamento de Dojos de Aikido"
ORGANIZATION = "Grupo RioAiki"
MIN_DB_VERSION = "2.2.1"

def get_version_info() -> dict:
    return {
        "version": VERSION,
        "release_date": RELEASE_DATE,
        "release_name": RELEASE_NAME,
        "system_name": SYSTEM_NAME,
        "organization": ORGANIZATION,
        "min_db_version": MIN_DB_VERSION,
    }
