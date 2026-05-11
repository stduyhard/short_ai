from __future__ import annotations

import importlib
import os
import sys
from contextlib import contextmanager
from typing import Any, Callable, TypeVar

from app.core.config import Settings


F = TypeVar("F", bound=Callable[..., Any])


def configure_langsmith_environment(current_settings: Settings) -> None:
    if not current_settings.langsmith_tracing or not current_settings.langsmith_api_key:
        return

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = current_settings.langsmith_api_key

    if current_settings.langsmith_project:
        os.environ["LANGSMITH_PROJECT"] = current_settings.langsmith_project

    if current_settings.langsmith_endpoint:
        os.environ["LANGSMITH_ENDPOINT"] = current_settings.langsmith_endpoint

    if current_settings.langsmith_workspace_id:
        os.environ["LANGSMITH_WORKSPACE_ID"] = current_settings.langsmith_workspace_id


def maybe_traceable(
    current_settings: Settings,
    *,
    name: str,
    run_type: str = "chain",
) -> Callable[[F], F]:
    if not _langsmith_enabled(current_settings):
        return _identity_decorator

    configure_langsmith_environment(current_settings)
    traceable = _load_traceable()
    if traceable is None:
        return _identity_decorator

    return traceable(name=name, run_type=run_type)


@contextmanager
def maybe_tracing_context(
    current_settings: Settings,
    *,
    project_name: str | None = None,
) -> Any:
    if not _langsmith_enabled(current_settings):
        yield None
        return

    configure_langsmith_environment(current_settings)
    langsmith_module = _load_langsmith_module()
    if langsmith_module is None:
        yield None
        return

    tracing_context = getattr(langsmith_module, "tracing_context", None)
    if tracing_context is None:
        yield None
        return

    extra: dict[str, Any] = {}
    if project_name:
        extra["project_name"] = project_name

    with tracing_context(enabled=True, **extra):
        yield None


def _langsmith_enabled(current_settings: Settings) -> bool:
    return current_settings.langsmith_tracing and bool(current_settings.langsmith_api_key)


def inspect_langsmith_runtime(current_settings: Settings) -> dict[str, Any]:
    langsmith_module = _load_langsmith_module()
    return {
        "tracingEnabled": current_settings.langsmith_tracing,
        "apiKeyConfigured": bool(current_settings.langsmith_api_key),
        "project": current_settings.langsmith_project,
        "endpoint": current_settings.langsmith_endpoint,
        "workspaceConfigured": bool(current_settings.langsmith_workspace_id),
        "moduleImportable": langsmith_module is not None,
        "pythonExecutable": sys.executable,
        "pid": os.getpid(),
        "cwd": os.getcwd(),
    }


def _identity_decorator(func: F) -> F:
    return func


def _load_traceable() -> Callable[..., Callable[[F], F]] | None:
    langsmith_module = _load_langsmith_module()
    if langsmith_module is None:
        return None
    return getattr(langsmith_module, "traceable", None)


def _load_langsmith_module() -> Any | None:
    try:
        return importlib.import_module("langsmith")
    except ModuleNotFoundError:
        return None
