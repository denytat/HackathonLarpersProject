/**
 * Page Routing, Topbar Synchronization, and Application Bootstrap
 */
const pageMeta = {
	overview: {
		title: "Threat Intelligence Overview",
		desc: "Real-time posture of analyzed campaigns, coordinated swarms, and detection telemetry",
	},
	analyze: {
		title: "Campaign Analysis Workspace",
		desc: "Ingest CSV campaign datasets, configure forensic detectors, and launch swarm discovery",
	},
	results: {
		title: "Forensic Investigation Results",
		desc: "Swarm topology, synchronized timeline anomalies, similarity evidence, and AI threat synthesis",
	},
	benchmarks: {
		title: "Model Evaluation & Benchmarks",
		desc: "Illustrative evaluation metrics, adversarial challenge robustness, and confusion matrices",
	},
	about: {
		title: "About Swarmwatch",
		desc: "Methodology, multi-modal detection technologies, and responsible threat-intelligence principles",
	},
}

function navigateTo(pageId) {
	if (!pageMeta[pageId]) return

	document
		.querySelectorAll(".page-view")
		.forEach(view => view.classList.remove("active"))
	document.getElementById("page-" + pageId)?.classList.add("active")

	document.querySelectorAll(".nav-item").forEach(btn => {
		btn.classList.toggle("active", btn.dataset.page === pageId)
	})

	document.getElementById("pageTitle").textContent = pageMeta[pageId].title
	document.getElementById("pageDesc").textContent = pageMeta[pageId].desc

	if (pageId === "results") {
		setTimeout(drawNetworkGraph, 30)
	}
}

document.addEventListener("DOMContentLoaded", () => {
	// Sidebar links
	document.querySelectorAll(".nav-item").forEach(btn => {
		btn.addEventListener("click", () => navigateTo(btn.dataset.page))
	})

	// In-page navigation buttons (`data-nav="..."`)
	document.querySelectorAll("[data-nav]").forEach(btn => {
		btn.addEventListener("click", () => navigateTo(btn.dataset.nav))
	})

	initAnalyzeWorkspace()
	initNetworkGraph()
})
