/**
 * Interactive Account Coordination Network Graph & Node Inspector
 */
const graphNodes = [
	{
		id: 0,
		handle: "@alpha_seed_01",
		role: "Seed Originator",
		badge: "badge-violet",
		color: "#8B5CF6",
		r: 12,
		x: 0.36,
		y: 0.42,
		score: "96/100",
		peers: "14 edges",
		lag: "0 sec (Origin)",
		posts: 84,
		summary:
			"Originates core crisis framing 40s before Swarm α amplification burst.",
	},
	{
		id: 1,
		handle: "@civic_pulse_884",
		role: "Core Amplifier",
		badge: "badge-red",
		color: "#EF4444",
		r: 10,
		x: 0.25,
		y: 0.28,
		score: "93/100",
		peers: "11 edges",
		lag: "38 sec",
		posts: 142,
		summary:
			"Synchronized with 11 peers across 6 burst windows. Shares identical syntactic framing and creation week (2024-W41).",
	},
	{
		id: 2,
		handle: "@metro_watch_019",
		role: "Core Amplifier",
		badge: "badge-red",
		color: "#EF4444",
		r: 9.5,
		x: 0.22,
		y: 0.56,
		score: "91/100",
		peers: "9 edges",
		lag: "36 sec",
		posts: 129,
		summary:
			"Paraphrases @alpha_seed_01 with 0.94 cosine similarity and identical hashtag suffix.",
	},
	{
		id: 3,
		handle: "@truth_ledger_x",
		role: "Core Amplifier",
		badge: "badge-red",
		color: "#EF4444",
		r: 9,
		x: 0.43,
		y: 0.23,
		score: "89/100",
		peers: "8 edges",
		lag: "44 sec",
		posts: 118,
		summary:
			"High temporal burstiness and repeated shortened-domain injection.",
	},
	{
		id: 4,
		handle: "@voice_north_77",
		role: "Core Amplifier",
		badge: "badge-red",
		color: "#EF4444",
		r: 9,
		x: 0.38,
		y: 0.68,
		score: "88/100",
		peers: "8 edges",
		lag: "49 sec",
		posts: 104,
		summary:
			"Part of October 2024 account creation cohort with automated UTC shift cadence.",
	},
	{
		id: 5,
		handle: "@state_audit_now",
		role: "Core Amplifier",
		badge: "badge-red",
		color: "#EF4444",
		r: 8.5,
		x: 0.16,
		y: 0.4,
		score: "85/100",
		peers: "7 edges",
		lag: "52 sec",
		posts: 97,
		summary: "Co-posts within 60-second windows alongside 7 Swarm α peers.",
	},
	{
		id: 6,
		handle: "@beacon_relay_2",
		role: "Relay / Bridge",
		badge: "badge-amber",
		color: "#F59E0B",
		r: 10.5,
		x: 0.62,
		y: 0.48,
		score: "81/100",
		peers: "10 edges",
		lag: "2.1 min",
		posts: 76,
		summary:
			"Bridges Swarm α narratives into broader secondary quote-tweet clusters.",
	},
	{
		id: 7,
		handle: "@policy_echo_44",
		role: "Relay / Bridge",
		badge: "badge-amber",
		color: "#F59E0B",
		r: 9,
		x: 0.72,
		y: 0.3,
		score: "78/100",
		peers: "6 edges",
		lag: "2.4 min",
		posts: 65,
		summary: "Consistent quote-amplification of Swarm α seed accounts.",
	},
	{
		id: 8,
		handle: "@daily_brief_90",
		role: "Relay / Bridge",
		badge: "badge-amber",
		color: "#F59E0B",
		r: 8.5,
		x: 0.74,
		y: 0.66,
		score: "76/100",
		peers: "6 edges",
		lag: "2.6 min",
		posts: 58,
		summary:
			"Shares 11 shortened URLs with Swarm α despite distinct surface persona.",
	},
	{
		id: 9,
		handle: "@local_reader_12",
		role: "Organic Periphery",
		badge: "badge-slate",
		color: "#475569",
		r: 6.5,
		x: 0.86,
		y: 0.22,
		score: "19/100",
		peers: "1 edge",
		lag: "42 min",
		posts: 14,
		summary:
			"Organic bystander who interacted once with a bridged post; no coordination signals.",
	},
	{
		id: 10,
		handle: "@sarah_k_journal",
		role: "Organic Periphery",
		badge: "badge-slate",
		color: "#475569",
		r: 6.5,
		x: 0.88,
		y: 0.52,
		score: "12/100",
		peers: "1 edge",
		lag: "1.3 hr",
		posts: 9,
		summary:
			"Organic account with independent posting cadence and diverse topic history.",
	},
	{
		id: 11,
		handle: "@civic_debate_99",
		role: "Organic Periphery",
		badge: "badge-slate",
		color: "#475569",
		r: 6.5,
		x: 0.56,
		y: 0.82,
		score: "21/100",
		peers: "2 edges",
		lag: "29 min",
		posts: 18,
		summary:
			"Low similarity and non-synchronized activity; below suspicion threshold.",
	},
]

const graphEdges = [
	[0, 1, 0.94],
	[0, 2, 0.92],
	[0, 3, 0.89],
	[0, 4, 0.88],
	[0, 5, 0.85],
	[1, 2, 0.91],
	[1, 3, 0.84],
	[1, 5, 0.86],
	[2, 4, 0.82],
	[3, 4, 0.78],
	[0, 6, 0.87],
	[4, 6, 0.74],
	[6, 7, 0.88],
	[6, 8, 0.85],
	[7, 8, 0.79],
	[7, 9, 0.25],
	[6, 10, 0.22],
	[8, 11, 0.28],
	[4, 11, 0.24],
]

let selectedNodeId = 1
let graphFilterMode = "all"

function selectNode(id) {
	selectedNodeId = id
	const node = graphNodes.find(n => n.id === id)
	if (!node) return

	document.getElementById("inspHandle").textContent = node.handle
	document.getElementById("inspScore").textContent = node.score
	document.getElementById("inspSummary").textContent = node.summary
	document.getElementById("inspPeers").textContent = node.peers
	document.getElementById("inspLag").textContent = node.lag
	document.getElementById("inspPosts").textContent = node.posts

	const badgeEl = document.getElementById("inspBadge")
	badgeEl.textContent = node.role
	badgeEl.className = "badge " + node.badge

	renderQuickList()
	drawNetworkGraph()
}

function renderQuickList() {
	const container = document.getElementById("suspiciousQuickList")
	if (!container) return

	container.innerHTML = ""
	graphNodes.slice(0, 4).forEach(node => {
		const isSel = node.id === selectedNodeId
		const row = document.createElement("div")
		row.style.cssText = `
      display:flex; align-items:center; justify-content:space-between;
      padding:8px 10px; border-radius:8px; cursor:pointer; font-size:12px;
      background:${isSel ? "rgba(59,130,246,0.14)" : "rgba(5,8,17,0.45)"};
      border:1px solid ${isSel ? "rgba(59,130,246,0.45)" : "var(--border-subtle)"};
    `
		row.innerHTML = `
      <div style="display:flex; align-items:center; gap:8px;">
        <span style="width:8px; height:8px; border-radius:50%; background:${node.color};"></span>
        <span class="mono" style="color:var(--text-primary);">${node.handle}</span>
      </div>
      <span class="mono" style="color:${node.color}; font-weight:600;">${node.score}</span>
    `
		row.addEventListener("click", () => selectNode(node.id))
		container.appendChild(row)
	})
}

function drawNetworkGraph() {
	const canvas = document.getElementById("networkCanvas")
	if (!canvas) return
	const rect = canvas.parentElement.getBoundingClientRect()
	if (rect.width === 0) return

	const dpr = window.devicePixelRatio || 1
	canvas.width = rect.width * dpr
	canvas.height = rect.height * dpr
	const ctx = canvas.getContext("2d")
	ctx.scale(dpr, dpr)

	const W = rect.width
	const H = rect.height
	ctx.clearRect(0, 0, W, H)

	// Background grid
	ctx.strokeStyle = "rgba(148, 163, 184, 0.04)"
	ctx.lineWidth = 1
	for (let x = 0; x < W; x += 36) {
		ctx.beginPath()
		ctx.moveTo(x, 0)
		ctx.lineTo(x, H)
		ctx.stroke()
	}
	for (let y = 0; y < H; y += 36) {
		ctx.beginPath()
		ctx.moveTo(0, y)
		ctx.lineTo(W, y)
		ctx.stroke()
	}

	const visibleNodes =
		graphFilterMode === "swarm"
			? graphNodes.filter(n => n.role !== "Organic Periphery")
			: graphNodes
	const visibleIds = new Set(visibleNodes.map(n => n.id))

	// Edges
	graphEdges.forEach(([a, b, weight]) => {
		if (!visibleIds.has(a) || !visibleIds.has(b)) return
		const na = graphNodes[a]
		const nb = graphNodes[b]
		const highlighted = a === selectedNodeId || b === selectedNodeId

		ctx.beginPath()
		ctx.moveTo(na.x * W, na.y * H)
		ctx.lineTo(nb.x * W, nb.y * H)
		if (highlighted) {
			ctx.strokeStyle = "rgba(56, 189, 248, 0.8)"
			ctx.lineWidth = 2.2
		} else {
			ctx.strokeStyle =
				weight > 0.7 ? "rgba(239, 68, 68, 0.28)" : "rgba(148, 163, 184, 0.14)"
			ctx.lineWidth = weight > 0.7 ? 1.4 : 1
		}
		ctx.stroke()
	})

	// Nodes
	visibleNodes.forEach(node => {
		const cx = node.x * W
		const cy = node.y * H
		const isSel = node.id === selectedNodeId

		if (isSel || node.role !== "Organic Periphery") {
			const glow = ctx.createRadialGradient(cx, cy, 2, cx, cy, node.r * 2.6)
			glow.addColorStop(0, node.color + "55")
			glow.addColorStop(1, "transparent")
			ctx.fillStyle = glow
			ctx.beginPath()
			ctx.arc(cx, cy, node.r * 2.6, 0, Math.PI * 2)
			ctx.fill()
		}

		ctx.beginPath()
		ctx.arc(cx, cy, node.r, 0, Math.PI * 2)
		ctx.fillStyle = node.color
		ctx.fill()
		ctx.lineWidth = isSel ? 2.8 : 1.5
		ctx.strokeStyle = isSel ? "#38BDF8" : "#050811"
		ctx.stroke()

		if (isSel || node.r >= 9) {
			ctx.font = '500 10.5px "JetBrains Mono", monospace'
			ctx.fillStyle = isSel ? "#FFFFFF" : "#CBD5E1"
			ctx.textAlign = "center"
			ctx.fillText(node.handle, cx, cy - node.r - 6)
		}
	})
}

function initNetworkGraph() {
	const canvas = document.getElementById("networkCanvas")
	const filterAllBtn = document.getElementById("filterAllBtn")
	const filterSwarmBtn = document.getElementById("filterSwarmBtn")

	if (filterAllBtn) {
		filterAllBtn.addEventListener("click", () => {
			graphFilterMode = "all"
			drawNetworkGraph()
		})
	}

	if (filterSwarmBtn) {
		filterSwarmBtn.addEventListener("click", () => {
			graphFilterMode = "swarm"
			drawNetworkGraph()
		})
	}

	if (canvas) {
		canvas.addEventListener("click", e => {
			const rect = canvas.getBoundingClientRect()
			const mx = e.clientX - rect.left
			const my = e.clientY - rect.top

			let closest = null
			let minDist = 26
			graphNodes.forEach(node => {
				if (graphFilterMode === "swarm" && node.role === "Organic Periphery")
					return
				const dx = node.x * rect.width - mx
				const dy = node.y * rect.height - my
				const dist = Math.hypot(dx, dy)
				if (dist < minDist) {
					minDist = dist
					closest = node.id
				}
			})
			if (closest !== null) selectNode(closest)
		})
	}

	window.addEventListener("resize", () => {
		if (document.getElementById("page-results")?.classList.contains("active")) {
			drawNetworkGraph()
		}
	})

	renderQuickList()
}
