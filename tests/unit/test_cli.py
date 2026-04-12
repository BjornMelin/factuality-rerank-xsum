from __future__ import annotations

from typing import TYPE_CHECKING

from typer.testing import CliRunner

import factuality_rerank_xsum.cli.main as cli_main

if TYPE_CHECKING:
    from collections.abc import Callable

    import pytest

runner = CliRunner()


def test_score_command_runs_all_required_scoring_stages(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def record(name: str) -> Callable[[], None]:
        def _inner() -> None:
            calls.append(name)

        return _inner

    monkeypatch.setattr(cli_main, "run_score_candidates_summac", record("summac"))
    monkeypatch.setattr(cli_main, "run_score_candidates_factcc", record("factcc"))
    monkeypatch.setattr(cli_main, "run_score_candidates_entity_support", record("entity"))
    monkeypatch.setattr(cli_main, "run_merge_candidate_scores", record("merge"))

    result = runner.invoke(cli_main.app, ["score"])

    assert result.exit_code == 0
    assert calls == ["summac", "factcc", "entity", "merge"]


def test_package_command_runs_reporting_then_packaging(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def record(name: str) -> Callable[[], None]:
        def _inner() -> None:
            calls.append(name)

        return _inner

    monkeypatch.setattr(cli_main, "run_make_tables_and_figures", record("figures"))
    monkeypatch.setattr(cli_main, "run_build_results_summary", record("summary"))
    monkeypatch.setattr(cli_main, "run_package_repo", record("package"))

    result = runner.invoke(cli_main.app, ["package"])

    assert result.exit_code == 0
    assert calls == ["figures", "summary", "package"]
