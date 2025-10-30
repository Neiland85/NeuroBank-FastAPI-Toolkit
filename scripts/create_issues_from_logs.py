#!/usr/bin/env python3
"""
Crea issues en GitHub a partir de un archivo de logs (p.ej., salida de terminal de ruff/mypy/pytest).
Requiere GitHub CLI autenticado: `gh auth login`.

Uso:
  python scripts/create_issues_from_logs.py --repo OWNER/REPO --log logs.txt --label lint --dry-run

Formato esperado (tolerante):
  - ruff: path/file.py:123:4: E123 Mensaje (o JSON con --ruff-json)
  - mypy: path/file.py:123: error: Mensaje  [code]
  - pytest: FAILED tests/test_x.py::TestSuite::test_y - AssertionError: ...

Agrupa por herramienta y código si está disponible para evitar duplicados masivos.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

# cache global de etiquetas existentes por repo
_EXISTING_LABELS_CACHE: dict[str, set[str]] = {}


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
RUFF_RE = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+)(?::\d+)?:\s*(?P<code>[A-Z]\d{3,4})\s+(?P<msg>.+)$"
)
MYPY_RE = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+):\s*error:\s*(?P<msg>.+?)(?:\s*\[(?P<code>[^\]]+)\])?$"
)
PYTEST_FAIL_RE = re.compile(r"^FAILED\s+(?P<test>[^\s]+)\s+-\s+(?P<msg>.+)$")
CONTEXT_BAR_RE = re.compile(r"^\s*\d+\s*\|")  # ej: "32 |   return x"
BULLET_RULE_RE = re.compile(r"^-\s+[A-Z]{2,}\d{2,}")


@dataclass
class IssueItem:
    tool: str
    title: str
    body: str
    labels: list[str]
    fingerprint: str  # para deduplicación básica


def parse_log_lines(lines: Iterable[str]) -> list[IssueItem]:
    items: list[IssueItem] = []

    for raw in lines:
        line = ANSI_RE.sub("", raw).strip()
        if not line:
            continue
        if line.lower().startswith("warning: "):
            continue
        if BULLET_RULE_RE.match(line):
            continue
        if line in {"|", "^", "| |_____________^"} or CONTEXT_BAR_RE.match(line):
            continue

        m = RUFF_RE.match(line)
        if m:
            file = m.group("file")
            line_no = m.group("line")
            code = m.group("code")
            msg = m.group("msg")
            title = f"lint: ruff {code} {Path(file).name}:{line_no}"
            body = f"Herramienta: ruff\nArchivo: {file}:{line_no}\nCódigo: {code}\n\nMensaje:\n{msg}\n\nReproducción:\nruff check {file}\n"
            items.append(
                IssueItem(
                    tool="ruff",
                    title=title[:120],
                    body=body,
                    labels=["lint", "ruff"],
                    fingerprint=f"ruff|{file}|{line_no}|{code}",
                )
            )
            continue

        m = MYPY_RE.match(line)
        if m:
            file = m.group("file")
            line_no = m.group("line")
            code = m.group("code") or "mypy"
            msg = m.group("msg")
            title = f"lint: mypy {code} {Path(file).name}:{line_no}"
            body = f"Herramienta: mypy\nArchivo: {file}:{line_no}\nCódigo: {code}\n\nMensaje:\n{msg}\n\nReproducción:\nmypy {file}\n"
            items.append(
                IssueItem(
                    tool="mypy",
                    title=title[:120],
                    body=body,
                    labels=["lint", "mypy"],
                    fingerprint=f"mypy|{file}|{line_no}|{code}",
                )
            )
            continue

        m = PYTEST_FAIL_RE.match(line)
        if m:
            test = m.group("test")
            msg = m.group("msg")
            title = f"test: pytest fallo {test}"
            body = f"Herramienta: pytest\nTest: {test}\n\nMensaje:\n{msg}\n\nReproducción:\npytest -k {test}\n"
            items.append(
                IssueItem(
                    tool="pytest",
                    title=title[:120],
                    body=body,
                    labels=["test-failure", "pytest"],
                    fingerprint=f"pytest|{test}",
                )
            )
            continue

        # Fallback genérico
        title = f"terminal: {line[:80]}"
        body = f"Entrada de log sin parse específico:\n\n{line}\n"
        items.append(
            IssueItem(
                tool="unknown",
                title=title,
                body=body,
                labels=["from-terminal"],
                fingerprint=f"raw|{line}",
            )
        )

    return items


def parse_ruff_json(log_path: Path) -> list[IssueItem]:
    """Parsea salida JSON de ruff (--output-format json)."""
    text = log_path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return []
    # Ruff emite una lista JSON
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    items: list[IssueItem] = []
    for entry in data:
        file = entry.get("filename") or entry.get("file") or ""
        code = entry.get("code") or "RUFF"
        message = entry.get("message") or ""
        loc = entry.get("location") or {}
        line_no = str(loc.get("row") or loc.get("line") or 0)
        title = f"lint: ruff {code} {Path(file).name}:{line_no}"
        body = f"Herramienta: ruff\nArchivo: {file}:{line_no}\nCódigo: {code}\n\nMensaje:\n{message}\n\nReproducción:\nruff check {file}\n"
        items.append(
            IssueItem(
                tool="ruff",
                title=title[:120],
                body=body,
                labels=["lint", "ruff"],
                fingerprint=f"ruff|{file}|{line_no}|{code}",
            )
        )
    return items


def dedupe(items: list[IssueItem]) -> list[IssueItem]:
    seen: set[str] = set()
    unique: list[IssueItem] = []
    for it in items:
        if it.fingerprint in seen:
            continue
        seen.add(it.fingerprint)
        unique.append(it)
    return unique


def get_existing_labels(repo: str) -> set[str]:
    if repo in _EXISTING_LABELS_CACHE:
        return _EXISTING_LABELS_CACHE[repo]
    try:
        gh_bin = shutil.which("gh") or "gh"
        out = subprocess.check_output(  # noqa: S603
            [gh_bin, "label", "list", "--repo", repo], text=True
        )
        labels = set()
        for line in out.splitlines():
            name = line.split()[0].strip()
            if name:
                labels.add(name)
        _EXISTING_LABELS_CACHE[repo] = labels
        return labels
    except Exception:
        return set()


def gh_issue_create(
    repo: str,
    item: IssueItem,
    dry_run: bool,
    max_retries: int = 5,
) -> None:
    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        repo,
        "--title",
        item.title,
    ]
    if item.labels:
        cmd += ["--label", ",".join(item.labels)]
    cmd += ["--body", item.body]
    # Nota: --template no es compatible con --body; se omite para creación automática

    if dry_run:
        print("DRY-RUN:", " ".join(cmd))
        return

    attempt = 0
    delay = 2.0
    while True:
        attempt += 1
        try:
            gh_bin = shutil.which("gh") or "gh"
            cmd[0] = gh_bin
            subprocess.run(cmd, check=True)  # noqa: S603
            return
        except subprocess.CalledProcessError:
            if attempt >= max_retries:
                raise
            # Backoff y reintento para errores de red/transitorios
            time.sleep(delay)
            delay = min(delay * 2, 60.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="OWNER/REPO")
    parser.add_argument("--log", required=True, help="Ruta al archivo de logs")
    parser.add_argument(
        "--label", default="", help="Etiqueta adicional a aplicar a todos"
    )
    parser.add_argument(
        "--template", default="lint_error.yml", help="Issue form a usar si aplica"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="No crea issues, sólo imprime comandos"
    )
    parser.add_argument(
        "--ruff-json",
        action="store_true",
        help="Interpretar el log como salida JSON de ruff",
    )
    args = parser.parse_args()

    log_path = Path(args.log)
    if args.ruff_json:
        items = parse_ruff_json(log_path)
    else:
        lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        items = parse_log_lines(lines)

    items = dedupe(items)

    extra_label = args.label.strip()
    if extra_label:
        for it in items:
            if extra_label not in it.labels:
                it.labels.append(extra_label)

    # Filtrar etiquetas que no existan en el repo para evitar errores de gh
    existing = get_existing_labels(args.repo)
    for it in items:
        # Filtra siempre; si no conocemos etiquetas, deja la lista vacía
        it.labels = [lbl for lbl in it.labels if lbl in existing]
        # No forzar etiquetas por defecto si no existen

    for it in items:
        gh_issue_create(args.repo, it, args.dry_run)


if __name__ == "__main__":
    main()
