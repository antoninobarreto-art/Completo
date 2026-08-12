# -*- coding: utf-8 -*-
"""
Backup rotativo do banco SQLite do RioAiki DOJOCHO.

Caracteristicas:
- Usa a API de backup ONLINE do SQLite (segura mesmo com o app em execucao);
- Gera copia em backups/ com timestamp no nome;
- Verifica a integridade da copia gerada (quick_check + contagem de usuarios);
- Mantem apenas as N copias mais recentes (padrao: 30);
- Registra operacao em backups/backup.log.

Configuracao opcional via variaveis de ambiente:
  RIOAIKI_DB_PATH     caminho do banco origem
  RIOAIKI_BACKUP_DIR  pasta de destino dos backups
  RIOAIKI_BACKUP_KEEP quantidade de copias a manter (padrao: 30)
"""
import os
import sys
import sqlite3
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DB_PATH = Path(os.environ.get("RIOAIKI_DB_PATH", ROOT / "rioaiki.db"))
BACKUP_DIR = Path(os.environ.get("RIOAIKI_BACKUP_DIR", ROOT / "backups"))
KEEP = int(os.environ.get("RIOAIKI_BACKUP_KEEP", "30"))
LOG_FILE = BACKUP_DIR / "backup.log"


def log(message: str) -> None:
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def run_backup() -> int:
    if not DB_PATH.exists():
        log(f"ERRO: banco nao encontrado em {DB_PATH}")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    dest = BACKUP_DIR / f"rioaiki_backup_{stamp}.db"

    # Backup online (API nativa do SQLite): consistente mesmo com o app gravando
    try:
        src = sqlite3.connect(str(DB_PATH))
        dst = sqlite3.connect(str(dest))
        src.backup(dst)
        dst.close()
        src.close()
    except sqlite3.Error as e:
        log(f"ERRO ao copiar banco: {e}")
        return 1

    # Verificacao de integridade da copia gerada
    try:
        chk = sqlite3.connect(str(dest))
        quick = chk.execute("PRAGMA quick_check").fetchone()[0]
        users = chk.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        chk.close()
        if quick != "ok":
            log(f"ERRO: copia corrompida (quick_check={quick}). Arquivo: {dest.name}")
            dest.unlink(missing_ok=True)
            return 1
    except sqlite3.Error as e:
        log(f"ERRO ao validar copia: {e}")
        dest.unlink(missing_ok=True)
        return 1

    size_kb = dest.stat().st_size // 1024
    log(f"OK: {dest.name} criado ({size_kb} KB, {users} usuarios, integridade OK)")

    # Rotacao: mantem apenas as KEEP copias mais recentes
    backups = sorted(BACKUP_DIR.glob("rioaiki_backup_*.db"))
    excess = len(backups) - KEEP
    removed = 0
    for old in backups[:max(excess, 0)]:
        try:
            old.unlink()
            removed += 1
        except OSError as e:
            log(f"AVISO: nao foi possivel remover {old.name}: {e}")
    if removed:
        log(f"Rotacao: {removed} copia(s) antiga(s) removida(s). Total mantido: {len(backups) - removed}")

    return 0


if __name__ == "__main__":
    sys.exit(run_backup())
