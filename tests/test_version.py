"""
DOJOCHO - Testes de Integridade e Automação do Sistema de Versionamento
"""

import subprocess
import sys
from fastapi.testclient import TestClient
from app.main import app
from app.version import VERSION, get_version_info, validate_db_schema_version
from app.database import SessionLocal


def test_version_info_structure():
    info = get_version_info()
    assert "version" in info
    assert info["version"] == VERSION
    assert "db_schema_version" in info
    assert info["db_schema_version"] == 1


def test_validate_db_schema_version():
    db = SessionLocal()
    try:
        res = validate_db_schema_version(db)
        assert res["valid"] is True
        assert res["expected_schema_version"] == 1
    finally:
        db.close()


def test_api_version_endpoint():
    client = TestClient(app)
    response = client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == VERSION
    assert "db_status" in data
    assert data["db_status"]["valid"] is True


def test_bump_version_script_dry_run():
    cmd = [sys.executable, "scripts/bump_version.py", "--type", "patch", "--dry-run"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert "[DRY-RUN]" in result.stdout
    assert "Iniciando Bump" in result.stdout


if __name__ == "__main__":
    print("Executando testes manuais de versionamento...")
    test_version_info_structure()
    print("[OK] test_version_info_structure ok")
    test_validate_db_schema_version()
    print("[OK] test_validate_db_schema_version ok")
    test_api_version_endpoint()
    print("[OK] test_api_version_endpoint ok")
    test_bump_version_script_dry_run()
    print("[OK] test_bump_version_script_dry_run ok")
    print("[SUCCESS] Todos os testes de versionamento passaram com sucesso!")
