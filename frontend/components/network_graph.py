"""Build and render the interactive account network graph from real API data."""

from __future__ import annotations

import json
import math
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from services.paths import SCRIPTS_DIR


ROLE_COLORS = {
    "Swarm member": ("#EF4444", "badge-red"),
    "Bridge account": ("#F59E0B", "badge-amber"),
    "Other account": ("#475569", "badge-slate"),
}


def _layout_positions(n: int) -> list[tuple[float, float]]:
    """Deterministic circular-ish layout in [0.12, 0.88] space."""
    if n <= 0:
        return []
    if n == 1:
        return [(0.5, 0.5)]

    positions = []
    for i in range(n):
        angle = (2 * math.pi * i / n) - math.pi / 2
        radius = 0.32 if n < 8 else 0.36
        x = 0.5 + radius * math.cos(angle)
        y = 0.5 + radius * math.sin(angle)
        positions.append((0.12 + 0.76 * ((x - 0.12) / 0.76), y))
        # Clamp
        positions[-1] = (
            min(0.88, max(0.12, x)),
            min(0.88, max(0.12, y)),
        )
    return positions


def build_graph_data(swarms: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Convert swarm evidence edges into nodes/edges for the canvas graph.
    Only creates links that appear in detection evidence.
    """
    account_meta: dict[str, dict[str, Any]] = {}
    edges: list[tuple[str, str, float, dict]] = []

    for swarm in swarms:
        swarm_id = swarm.get("id", "swarm")
        swarm_score = float(swarm.get("score", 0))
        accounts = [str(a) for a in (swarm.get("accounts") or [])]

        for account in accounts:
            meta = account_meta.setdefault(
                account,
                {
                    "clusters": set(),
                    "max_score": 0.0,
                    "edge_count": 0,
                    "signals": set(),
                },
            )
            meta["clusters"].add(swarm_id)
            meta["max_score"] = max(meta["max_score"], swarm_score)

        for edge in swarm.get("evidence") or []:
            if not isinstance(edge, dict):
                continue
            a1 = edge.get("account_1")
            a2 = edge.get("account_2")
            if not a1 or not a2:
                continue
            a1, a2 = str(a1), str(a2)
            score = float(edge.get("score", 0) or 0)
            signals = edge.get("signals") or {}
            signal_keys = (
                set(signals.keys())
                if isinstance(signals, dict)
                else set()
            )

            for account in (a1, a2):
                meta = account_meta.setdefault(
                    account,
                    {
                        "clusters": set(),
                        "max_score": 0.0,
                        "edge_count": 0,
                        "signals": set(),
                    },
                )
                meta["clusters"].add(swarm_id)
                meta["max_score"] = max(meta["max_score"], score)
                meta["edge_count"] += 1
                meta["signals"].update(signal_keys)

            edges.append((a1, a2, score, signals if isinstance(signals, dict) else {}))

    accounts = sorted(account_meta.keys())
    positions = _layout_positions(len(accounts))
    id_map = {account: idx for idx, account in enumerate(accounts)}

    nodes = []
    for idx, account in enumerate(accounts):
        meta = account_meta[account]
        clusters = sorted(meta["clusters"])
        if meta["edge_count"] >= 3 or meta["max_score"] >= 0.75:
            role = "Swarm member"
        elif meta["edge_count"] >= 1:
            role = "Bridge account"
        else:
            role = "Other account"

        color, badge = ROLE_COLORS[role]
        raw = meta["max_score"]
        signal_list = sorted(meta["signals"])
        summary_parts = []
        if clusters:
            summary_parts.append(f"Cluster(s): {', '.join(clusters)}")
        if signal_list:
            summary_parts.append(f"Signals: {', '.join(signal_list)}")
        if not summary_parts:
            summary_parts.append("Account appeared in a detected swarm.")

        x, y = positions[idx] if idx < len(positions) else (0.5, 0.5)
        nodes.append({
            "id": idx,
            "handle": account,
            "role": role,
            "badge": badge,
            "color": color,
            "r": 7 + min(6, meta["edge_count"]),
            "x": x,
            "y": y,
            "score": f"{raw:.2f}",
            "rawScore": raw,
            "peers": f"{meta['edge_count']} evidence edge(s)",
            "cluster": ", ".join(clusters) or "—",
            "posts": "—",
            "summary": " · ".join(summary_parts),
        })

    graph_edges = []
    seen = set()
    for a1, a2, score, _signals in edges:
        if a1 not in id_map or a2 not in id_map:
            continue
        i, j = id_map[a1], id_map[a2]
        key = tuple(sorted((i, j)))
        if key in seen:
            continue
        seen.add(key)
        graph_edges.append([i, j, score])

    return {"nodes": nodes, "edges": graph_edges}


def render_network_graph(swarms: list[dict[str, Any]], height: int = 520) -> None:
    graph = build_graph_data(swarms)
    js_path = SCRIPTS_DIR / "networkGraph.js"
    js_code = js_path.read_text(encoding="utf-8") if js_path.exists() else ""

    if not graph["nodes"]:
        st.info(
            "No account relationship edges are available in the "
            "current analysis response. The graph only shows links "
            "present in detection evidence."
        )
        return

    payload = json.dumps(graph)
    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    body {{
      margin: 0;
      background: #0B1120;
      color: #F1F5F9;
      font-family: "IBM Plex Sans", -apple-system, sans-serif;
    }}
    .wrap {{
      display: grid;
      grid-template-columns: 1.6fr 1fr;
      gap: 14px;
      padding: 4px;
    }}
    .panel {{
      background: #0B1120;
      border: 1px solid rgba(148,163,184,0.12);
      border-radius: 12px;
      padding: 12px;
    }}
    .canvas-box {{
      height: 420px;
      position: relative;
      border-radius: 10px;
      overflow: hidden;
      background: #050811;
      border: 1px solid rgba(148,163,184,0.1);
    }}
    canvas {{ width: 100%; height: 100%; display: block; cursor: pointer; }}
    .toolbar {{ display:flex; gap:8px; margin-bottom:10px; }}
    button {{
      background: rgba(15,23,42,0.7);
      border: 1px solid rgba(148,163,184,0.18);
      color: #94A3B8;
      border-radius: 8px;
      padding: 6px 10px;
      font-size: 12px;
      cursor: pointer;
    }}
    button:hover {{ color: #F1F5F9; border-color: rgba(148,163,184,0.35); }}
    .badge {{
      display:inline-flex; padding:3px 8px; border-radius:6px;
      font-size:11px; font-family: monospace;
    }}
    .badge-red {{ background:rgba(239,68,68,.12); color:#FCA5A5; border:1px solid rgba(239,68,68,.25); }}
    .badge-amber {{ background:rgba(245,158,11,.12); color:#FCD34D; border:1px solid rgba(245,158,11,.25); }}
    .badge-slate {{ background:rgba(148,163,184,.1); color:#CBD5E1; border:1px solid rgba(148,163,184,.2); }}
    .insp-title {{ font-size:14px; font-weight:600; margin:0 0 6px; }}
    .insp-meta {{ font-size:12px; color:#94A3B8; margin: 6px 0; }}
    .insp-grid {{
      display:grid; grid-template-columns:1fr 1fr; gap:8px;
      margin-top:10px; font-size:12px; color:#94A3B8;
    }}
    .insp-grid strong {{ display:block; color:#F1F5F9; margin-top:2px; font-family:monospace; }}
    #suspiciousQuickList {{ display:flex; flex-direction:column; gap:6px; margin-top:12px; }}
    @media (max-width: 820px) {{
      .wrap {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="panel">
      <div class="toolbar">
        <button id="filterAllBtn" type="button">All accounts</button>
        <button id="filterSwarmBtn" type="button">Linked only</button>
      </div>
      <div class="canvas-box">
        <canvas id="networkCanvas"></canvas>
      </div>
    </div>
    <div class="panel">
      <div class="insp-title" id="inspHandle">Select an account</div>
      <span class="badge badge-slate" id="inspBadge">—</span>
      <div class="insp-meta" id="inspSummary">Click a node to inspect evidence-backed relationships.</div>
      <div class="insp-grid">
        <div>Score<strong id="inspScore">—</strong></div>
        <div>Evidence links<strong id="inspPeers">—</strong></div>
        <div>Cluster<strong id="inspLag">—</strong></div>
        <div>Posts<strong id="inspPosts">—</strong></div>
      </div>
      <div style="margin-top:14px;font-size:11px;color:#64748B;text-transform:uppercase;
        letter-spacing:.08em;font-family:monospace;">Top linked accounts</div>
      <div id="suspiciousQuickList"></div>
    </div>
  </div>
  <script>
    window.SWARM_GRAPH_DATA = {payload};
  </script>
  <script>
  {js_code}
  </script>
</body>
</html>
"""
    components.html(html, height=height, scrolling=False)
