"""get_citations MCP Tool

获取论文的引用/被引关系图。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from sources import semantic_scholar

_CONFIG_PATH = Path.home() / ".nexus" / "global_config.json"
_VALID_DIRECTIONS = {"references", "citations", "both"}


def _get_s2_key() -> str | None:
    try:
        if _CONFIG_PATH.exists():
            config = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
            return config.get("semantic_scholar_key")
    except Exception:
        pass
    return None


def register(mcp_instance: FastMCP) -> None:
    @mcp_instance.tool()
    async def get_citations(
        identifier: str,
        direction: str = "both",
        limit: int = 50,
    ) -> dict[str, Any]:
        """获取论文引用/被引关系。

        Args:
            identifier: DOI (如 "DOI:10.xxx") 或 S2 Paper ID 或 arXiv ID (如 "ARXIV:2301.12345")
            direction: "references" (参考文献) | "citations" (被引) | "both"
            limit: 每个方向的最大数量

        Returns:
            {"references": [...], "citations": [...], "total_refs": int, "total_cites": int}
        """
        if direction not in _VALID_DIRECTIONS:
            raise ValueError(
                f"Invalid direction: {direction!r}. "
                "Expected one of: references, citations, both."
            )

        # 格式化 identifier
        if identifier.startswith("10."):
            identifier = f"DOI:{identifier}"

        s2_key = _get_s2_key()
        try:
            data = await semantic_scholar.get_citations(
                identifier,
                direction=direction,
                limit=limit,
                api_key=s2_key,
            )
        except Exception as e:
            return {
                "error": f"Semantic Scholar API 请求失败: {type(e).__name__}: {e}",
                "references": [],
                "citations": [],
                "total_refs": 0,
                "total_cites": 0,
            }

        return {
            "references": data.get("references", []),
            "citations": data.get("citations", []),
            "total_refs": len(data.get("references", [])),
            "total_cites": len(data.get("citations", [])),
        }
