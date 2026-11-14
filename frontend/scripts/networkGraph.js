/**
 * Interactive Account Coordination Network Graph
 * Accepts real detection data via window.SWARM_GRAPH_DATA
 * Adapted from Gemini-generated networkGraph.js
 */
(function () {
	const data = window.SWARM_GRAPH_DATA || { nodes: [], edges: [] };
	const graphNodes = data.nodes || [];
	const graphEdges = data.edges || [];

	let selectedNodeId = graphNodes.length ? graphNodes[0].id : null;
	let graphFilterMode = "all";

	function selectNode(id) {
		selectedNodeId = id;
		const node = graphNodes.find((n) => n.id === id);
		if (!node) return;

		const setText = (elId, value) => {
			const el = document.getElementById(elId);
			if (el) el.textContent = value;
		};

		setText("inspHandle", node.handle);
		setText("inspScore", node.score);
		setText("inspSummary", node.summary);
		setText("inspPeers", node.peers);
		setText("inspLag", node.cluster || "—");
		setText("inspPosts", String(node.posts ?? "—"));

		const badgeEl = document.getElementById("inspBadge");
		if (badgeEl) {
			badgeEl.textContent = node.role;
			badgeEl.className = "badge " + (node.badge || "badge-slate");
		}

		renderQuickList();
		drawNetworkGraph();
	}

	function renderQuickList() {
		const container = document.getElementById("suspiciousQuickList");
		if (!container) return;
		container.innerHTML = "";

		const top = [...graphNodes]
			.filter((n) => n.role !== "Other account")
			.sort((a, b) => (b.rawScore || 0) - (a.rawScore || 0))
			.slice(0, 6);

		if (!top.length) {
			container.innerHTML =
				'<div style="color:#64748B;font-size:12px;padding:8px;">No linked accounts in this analysis.</div>';
			return;
		}

		top.forEach((node) => {
			const isSel = node.id === selectedNodeId;
			const row = document.createElement("div");
			row.style.cssText = `
        display:flex; align-items:center; justify-content:space-between;
        padding:8px 10px; border-radius:8px; cursor:pointer; font-size:12px;
        background:${isSel ? "rgba(59,130,246,0.14)" : "rgba(5,8,17,0.45)"};
        border:1px solid ${isSel ? "rgba(59,130,246,0.45)" : "rgba(148,163,184,0.12)"};
      `;
			row.innerHTML = `
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="width:8px; height:8px; border-radius:50%; background:${node.color};"></span>
          <span class="mono" style="color:#F1F5F9; font-family:monospace;">${node.handle}</span>
        </div>
        <span class="mono" style="color:${node.color}; font-weight:600; font-family:monospace;">${node.score}</span>
      `;
			row.addEventListener("click", () => selectNode(node.id));
			container.appendChild(row);
		});
	}

	function drawNetworkGraph() {
		const canvas = document.getElementById("networkCanvas");
		if (!canvas) return;
		const parent = canvas.parentElement;
		if (!parent) return;
		const rect = parent.getBoundingClientRect();
		if (rect.width === 0) return;

		const dpr = window.devicePixelRatio || 1;
		canvas.width = rect.width * dpr;
		canvas.height = rect.height * dpr;
		const ctx = canvas.getContext("2d");
		ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

		const W = rect.width;
		const H = rect.height;
		ctx.clearRect(0, 0, W, H);

		ctx.strokeStyle = "rgba(148, 163, 184, 0.04)";
		ctx.lineWidth = 1;
		for (let x = 0; x < W; x += 36) {
			ctx.beginPath();
			ctx.moveTo(x, 0);
			ctx.lineTo(x, H);
			ctx.stroke();
		}
		for (let y = 0; y < H; y += 36) {
			ctx.beginPath();
			ctx.moveTo(0, y);
			ctx.lineTo(W, y);
			ctx.stroke();
		}

		if (!graphNodes.length) {
			ctx.fillStyle = "#64748B";
			ctx.font = '13px sans-serif';
			ctx.textAlign = "center";
			ctx.fillText("No account relationships to display", W / 2, H / 2);
			return;
		}

		const visibleNodes =
			graphFilterMode === "swarm"
				? graphNodes.filter((n) => n.role !== "Other account")
				: graphNodes;
		const visibleIds = new Set(visibleNodes.map((n) => n.id));
		const byId = Object.fromEntries(graphNodes.map((n) => [n.id, n]));

		graphEdges.forEach((edge) => {
			const a = edge[0];
			const b = edge[1];
			const weight = edge[2] || 0.5;
			if (!visibleIds.has(a) || !visibleIds.has(b)) return;
			const na = byId[a];
			const nb = byId[b];
			if (!na || !nb) return;

			const highlighted = a === selectedNodeId || b === selectedNodeId;
			ctx.beginPath();
			ctx.moveTo(na.x * W, na.y * H);
			ctx.lineTo(nb.x * W, nb.y * H);
			if (highlighted) {
				ctx.strokeStyle = "rgba(56, 189, 248, 0.8)";
				ctx.lineWidth = 2.2;
			} else {
				ctx.strokeStyle =
					weight > 0.7
						? "rgba(239, 68, 68, 0.28)"
						: "rgba(148, 163, 184, 0.14)";
				ctx.lineWidth = weight > 0.7 ? 1.4 : 1;
			}
			ctx.stroke();
		});

		visibleNodes.forEach((node) => {
			const cx = node.x * W;
			const cy = node.y * H;
			const isSel = node.id === selectedNodeId;
			const r = node.r || 8;

			if (isSel || node.role !== "Other account") {
				const glow = ctx.createRadialGradient(cx, cy, 2, cx, cy, r * 2.6);
				glow.addColorStop(0, (node.color || "#3B82F6") + "55");
				glow.addColorStop(1, "transparent");
				ctx.fillStyle = glow;
				ctx.beginPath();
				ctx.arc(cx, cy, r * 2.6, 0, Math.PI * 2);
				ctx.fill();
			}

			ctx.beginPath();
			ctx.arc(cx, cy, r, 0, Math.PI * 2);
			ctx.fillStyle = node.color || "#3B82F6";
			ctx.fill();
			ctx.lineWidth = isSel ? 2.8 : 1.5;
			ctx.strokeStyle = isSel ? "#38BDF8" : "#050811";
			ctx.stroke();

			if (isSel || r >= 9) {
				ctx.font = '500 10.5px monospace';
				ctx.fillStyle = isSel ? "#FFFFFF" : "#CBD5E1";
				ctx.textAlign = "center";
				ctx.fillText(node.handle, cx, cy - r - 6);
			}
		});
	}

	function initNetworkGraph() {
		const canvas = document.getElementById("networkCanvas");
		const filterAllBtn = document.getElementById("filterAllBtn");
		const filterSwarmBtn = document.getElementById("filterSwarmBtn");

		if (filterAllBtn) {
			filterAllBtn.addEventListener("click", () => {
				graphFilterMode = "all";
				drawNetworkGraph();
			});
		}
		if (filterSwarmBtn) {
			filterSwarmBtn.addEventListener("click", () => {
				graphFilterMode = "swarm";
				drawNetworkGraph();
			});
		}

		if (canvas) {
			canvas.addEventListener("click", (e) => {
				const rect = canvas.getBoundingClientRect();
				const mx = e.clientX - rect.left;
				const my = e.clientY - rect.top;
				let closest = null;
				let minDist = 26;

				graphNodes.forEach((node) => {
					if (graphFilterMode === "swarm" && node.role === "Other account")
						return;
					const dx = node.x * rect.width - mx;
					const dy = node.y * rect.height - my;
					const dist = Math.hypot(dx, dy);
					if (dist < minDist) {
						minDist = dist;
						closest = node.id;
					}
				});
				if (closest !== null) selectNode(closest);
			});
		}

		window.addEventListener("resize", drawNetworkGraph);
		if (selectedNodeId !== null) selectNode(selectedNodeId);
		else {
			renderQuickList();
			drawNetworkGraph();
		}
		setTimeout(drawNetworkGraph, 80);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", initNetworkGraph);
	} else {
		initNetworkGraph();
	}
})();
