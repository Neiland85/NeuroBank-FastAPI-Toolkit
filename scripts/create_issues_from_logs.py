#!/usr/bin/env python3
"""
Crea issues en GitHub a partir de un archivo de logs (p.ej., salida de terminal de ruff/mypy/pytest).
Requiere GitHub CLI autenticado: `gh auth login`.

Uso:
  python scripts/create_issues_from_logs.py --repo OWNER/REPO --log logs.txt --label lint --dry-run

Formato esperado (tolerante):
  - ruff: path/file.py:123:4: E123 Mensaje
  - mypy: path/file.py:123: error: Mensaje  [code]
  - pytest: FAILED tests/test_x.py::TestSuite::test_y - AssertionError: ...

Agrupa por herramienta y código si está disponible para evitar duplicados masivos.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
RUFF_RE = re.compile(r"^(?P<file>[^:]+):(?P<line>\d+)(?::\d+)?:\s*(?P<code>[A-Z]\d{3,4})\s+(?P<msg>.+)$")
MYPY_RE = re.compile(r"^(?P<file>[^:]+):(?P<line>\d+):\s*error:\s*(?P<msg>.+?)(?:\s*\[(?P<code>[^\]]+)\])?$")
PYTEST_FAIL_RE = re.compile(r"^FAILED\s+(?P<test>[^\s]+)\s+-\s+(?P<msg>.+)$")
CONTEXT_BAR_RE = re.compile(r"^\s*\d+\s*\|")  # ej: "32 |   return x"
BULLET_RULE_RE = re.compile(r"^-\s+[A-Z]{2,}\d{2,}")


@dataclass
class IssueItem:
    tool: str
    title: str
    body: str
    labels: List[str]
    fingerprint: str  # para deduplicación básica


def parse_log_lines(lines: Iterable[str]) -> List[IssueItem]:
    items: List[IssueItem] = []

    for raw in lines:
        line = ANSI_RE.sub("", raw).strip()
        if not line:
            continue
        if line.lower().startswith("warning: "):
            continue
        if BULLET_RULE_RE.match(line):
            continue
        if line in {"|", "^", "^", "| |_____________^"} or CONTEXT_BAR_RE.match(line):
            continue

        m = RUFF_RE.match(line)
        if m:
            file = m.group("file")
            line_no = m.group("line")
            code = m.group("code")
            msg = m.group("msg")
            title = f"lint: ruff {code} {Path(file).name}:{line_no}"
            body = (
                f"Herramienta: ruff\nArchivo: {file}:{line_no}\nCódigo: {code}\n\nMensaje:\n{msg}\n\nReproducción:\nruff check {file}\n"
            )
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
            body = (
                f"Herramienta: mypy\nArchivo: {file}:{line_no}\nCódigo: {code}\n\nMensaje:\n{msg}\n\nReproducción:\nmypy {file}\n"
            )
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
            body = (
                f"Herramienta: pytest\nTest: {test}\n\nMensaje:\n{msg}\n\nReproducción:\npytest -k {test}\n"
            )
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


def dedupe(items: List[IssueItem]) -> List[IssueItem]:
    seen: set[str] = set()
    unique: List[IssueItem] = []
    for it in items:
        if it.fingerprint in seen:
            continue
        seen.add(it.fingerprint)
        unique.append(it)
    return unique


def gh_issue_create(repo: str, item: IssueItem, dry_run: bool, template: str | None) -> None:
    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        repo,
        "--title",
        item.title,
        "--label",
        ",".join(item.labels),
        "--body",
        item.body,
    ]
    if template:
        cmd.extend(["--template", template])

    if dry_run:
        print("DRY-RUN:", " ".join(cmd))
        return

    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="OWNER/REPO")
    parser.add_argument("--log", required=True, help="Ruta al archivo de logs")
    parser.add_argument("--label", default="", help="Etiqueta adicional a aplicar a todos")
    parser.add_argument("--template", default="lint_error.yml", help="Issue form a usar si aplica")
    parser.add_argument("--dry-run", action="store_true", help="No crea issues, sólo imprime comandos")
    args = parser.parse_args()

    lines = Path(args.log).read_text(encoding="utf-8", errors="ignore").splitlines()
    items = parse_log_lines(lines)
    items = dedupe(items)

    extra_label = args.label.strip()
    if extra_label:
        for it in items:
            if extra_label not in it.labels:
                it.labels.append(extra_label)

    for it in items:
        template = args.template if it.tool in {"ruff", "mypy", "pytest"} else None
        gh_issue_create(args.repo, it, args.dry_run, template)


if __name__ == "__main__":
    main()
