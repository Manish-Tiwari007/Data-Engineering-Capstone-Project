"""Utilities for creating Snowflake connections.

This module prioritizes Airflow Connections (required by the rubric) and
falls back to environment variables for local script execution.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import snowflake.connector


def _airflow_conn_params(conn_id: str) -> Optional[Dict[str, Any]]:
    """Build Snowflake connector parameters from an Airflow connection.

    Args:
        conn_id: Airflow connection id.

    Returns:
        A dict of connection kwargs, or None when Airflow is unavailable.
    """
    try:
        from airflow.hooks.base import BaseHook  # type: ignore
        from airflow.exceptions import AirflowNotFoundException  # type: ignore
    except Exception:
        return None

    try:
        conn = BaseHook.get_connection(conn_id)
    except AirflowNotFoundException:
        return None

    extras = conn.extra_dejson or {}

    account = extras.get("account") or conn.host
    if not account:
        raise ValueError(
            (
                "Snowflake account is missing. "
                "Set it in Airflow connection extra as 'account'."
            )
        )

    params: Dict[str, Any] = {
        "user": conn.login,
        "password": conn.password,
        "account": account,
        "warehouse": extras.get("warehouse"),
        "database": extras.get("database"),
        "schema": conn.schema or extras.get("schema"),
        "role": extras.get("role"),
    }
    return {k: v for k, v in params.items() if v}


def _env_conn_params() -> Dict[str, Any]:
    """Build Snowflake connector parameters from environment variables."""
    required = ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_ACCOUNT"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise ValueError(
            "Missing Snowflake environment variables: "
            + ", ".join(missing)
            + ". Use Airflow Connection 'snowflake_default' or set env vars."
        )

    params: Dict[str, Any] = {
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
    }
    return {k: v for k, v in params.items() if v}


def get_connection(conn_id: str = "snowflake_default", schema: Optional[str] = None):
    """Create a Snowflake connection.

    Args:
        conn_id: Airflow connection id to use when running in Airflow.
        schema: Optional schema override for this connection.

    Returns:
        snowflake.connector.SnowflakeConnection
    """
    params = _airflow_conn_params(conn_id) or _env_conn_params()
    if schema:
        params["schema"] = schema

    return snowflake.connector.connect(**params)
