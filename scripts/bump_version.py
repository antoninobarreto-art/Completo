#!/usr/bin/env python3
"""
DOJOCHO - Script de Automação de Release e Versionamento Semântico (SemVer)
Uso:
    python scripts/bump_version.py --type patch
    python scripts/bump_version.py --type minor --name "Nova Funcionalidade X"
    python scripts/bump_version.py --type major
    python scripts/bump_version.py --set 2.4.0
    python scripts/bump_version.py --dry-run
"""

import sys
import os
import re
import argparse
from datetime import datetime

# Garante que o diretório raiz do projeto esteja no sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

VERSION_FILE = os.path.join(PROJECT_ROOT, "app", "version.py")
CHANGELOG_FILE = os.path.join(PROJECT_ROOT, "CHANGELOG.md")


def parse_semver(version_str: str):
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_str.strip())
    if not match:
        raise ValueError(f"Versão inválida '{version_str}'. Deve seguir o formato MAJOR.MINOR.PATCH (ex: 2.3.0).")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(current_version: str, bump_type: str) -> str:
    major, minor, patch = parse_semver(current_version)
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Tipo de bump inválido: {bump_type}")


def update_version_py(new_version: str, release_name: str = None, dry_run: bool = False):
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    today = datetime.now().strftime("%Y-%m-%d")

    # Atualiza VERSION = "..."
    content = re.sub(r'VERSION\s*=\s*"[^"]+"', f'VERSION = "{new_version}"', content)
    # Atualiza RELEASE_DATE = "..."
    content = re.sub(r'RELEASE_DATE\s*=\s*"[^"]+"', f'RELEASE_DATE = "{today}"', content)

    if release_name:
        content = re.sub(r'RELEASE_NAME\s*=\s*"[^"]+"', f'RELEASE_NAME = "{release_name}"', content)

    if not dry_run:
        with open(VERSION_FILE, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"[{'DRY-RUN' if dry_run else 'OK'}] Atualizado app/version.py -> VERSION={new_version}, RELEASE_DATE={today}")


def update_changelog(new_version: str, dry_run: bool = False):
    if not os.path.exists(CHANGELOG_FILE):
        print(f"[AVISO] Changelog não encontrado em {CHANGELOG_FILE}")
        return

    with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    today = datetime.now().strftime("%Y-%m-%d")

    # Verifica se a versão já existe no changelog
    if f"## [{new_version}]" in content:
        print(f"[INFO] Versão [{new_version}] já registrada no CHANGELOG.md")
        return

    new_section = f"""## [{new_version}] - {today}

### Adicionado
- 

### Alterado / Refatorado
- 

### Corrigido
- 

---

"""

    # Insere logo após o cabeçalho inicial do CHANGELOG.md (primeira ocorrência de ## [)
    first_section_pos = content.find("## [")
    if first_section_pos != -1:
        new_content = content[:first_section_pos] + new_section + content[first_section_pos:]
    else:
        new_content = content + "\n\n" + new_section

    if not dry_run:
        with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)

    print(f"[{'DRY-RUN' if dry_run else 'OK'}] Nova seção criada no CHANGELOG.md -> ## [{new_version}] - {today}")


def git_commit_and_tag(new_version: str, release_name: str = None, push: bool = True, dry_run: bool = False):
    import subprocess
    commit_msg = f"release: v{new_version}"
    if release_name:
        commit_msg += f" - {release_name}"

    cmd_add = ["git", "add", "."]
    cmd_commit = ["git", "commit", "-m", commit_msg]
    cmd_tag = ["git", "tag", "-a", f"v{new_version}", "-m", f"Release v{new_version}"]
    cmd_push = ["git", "push", "origin", "main", "--tags"]

    if dry_run:
        print(f"[DRY-RUN] Executaria: {' '.join(cmd_add)}")
        print(f"[DRY-RUN] Executaria: {' '.join(cmd_commit)}")
        print(f"[DRY-RUN] Executaria: {' '.join(cmd_tag)}")
        if push:
            print(f"[DRY-RUN] Executaria: {' '.join(cmd_push)}")
        return

    try:
        subprocess.run(cmd_add, check=True, cwd=PROJECT_ROOT)
        subprocess.run(cmd_commit, check=True, cwd=PROJECT_ROOT)
        subprocess.run(cmd_tag, check=True, cwd=PROJECT_ROOT)
        print(f"[OK] Alterações commitadas e Tag v{new_version} criada no Git com sucesso!")
        
        if push:
            subprocess.run(cmd_push, check=True, cwd=PROJECT_ROOT)
            print(f"[OK] Commit e Tags enviados para o GitHub (origin/main) com sucesso!")
    except Exception as e:
        print(f"[AVISO] Não foi possível concluir a operação automática no Git/GitHub: {e}")


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="DOJOCHO - Ferramenta CLI para Versionamento Semântico")
    parser.add_argument("--type", choices=["major", "minor", "patch"], help="Tipo de incremento semântico")
    parser.add_argument("--set", dest="set_version", type=str, help="Definir uma versão específica diretamente (ex: 2.4.0)")
    parser.add_argument("--name", type=str, help="Nome do release ou descrição resumida")
    parser.add_argument("--commit", action="store_true", help="Realizar git add, commit e tag automaticamente")
    parser.add_argument("--dry-run", action="store_true", help="Simular alterações sem modificar arquivos")

    args = parser.parse_args()

    # Importa a versão atual
    from app.version import VERSION as CURRENT_VERSION

    if not args.type and not args.set_version:
        print(f"Versão Atual do DOJOCHO: v{CURRENT_VERSION}")
        print("Use --type (major|minor|patch) ou --set X.Y.Z para realizar um bump de versão.")
        sys.exit(0)

    if args.set_version:
        parse_semver(args.set_version) # Valida sintaxe
        new_version = args.set_version
    else:
        new_version = bump_version(CURRENT_VERSION, args.type)

    print(f"[BUMP] Iniciando Bump de Versão: v{CURRENT_VERSION} -> v{new_version}")

    update_version_py(new_version, release_name=args.name, dry_run=args.dry_run)
    update_changelog(new_version, dry_run=args.dry_run)

    if args.commit:
        git_commit_and_tag(new_version, release_name=args.name, dry_run=args.dry_run)

    print(f"[SUCCESS] Processo de versionamento para v{new_version} concluído com sucesso!")


if __name__ == "__main__":
    main()
