/**
 * Analyze Workspace: CSV Drag-and-Drop, Detector Switches, & Pipeline Simulation
 */
function showSelectedFile(name, meta) {
	document.getElementById("fileNameLabel").textContent = name
	document.getElementById("fileMetaLabel").textContent = meta
	document.getElementById("fileInfoBox").style.display = "flex"
	document.getElementById("dropzoneTitle").textContent =
		"Dataset Loaded & Ready for Analysis"
}

function loadSampleFile() {
	showSelectedFile(
		"election_narrative_stream_05.csv",
		"48,210 posts • 1,420 unique accounts • 14.2 MB",
	)
}

function runSimulatedAnalysis() {
	if (document.getElementById("fileInfoBox").style.display !== "flex") {
		loadSampleFile()
	}

	const panel = document.getElementById("pipelinePanel")
	const bar = document.getElementById("pipelineBar")
	const pct = document.getElementById("pipelinePct")
	const doneBtn = document.getElementById("viewResultsNowBtn")
	const headline = document.getElementById("pipelineHeadline")
	const steps = [1, 2, 3, 4].map(i => document.getElementById("step-" + i))

	panel.style.display = "block"
	doneBtn.style.display = "none"
	steps.forEach(s => (s.className = "pipeline-step"))
	headline.textContent = "Running Multi-Modal Forensics..."

	const stages = [
		{ idx: 0, pct: 25, delay: 200 },
		{ idx: 1, pct: 55, delay: 750 },
		{ idx: 2, pct: 82, delay: 1350 },
		{ idx: 3, pct: 100, delay: 1950 },
	]

	stages.forEach((stage, i) => {
		setTimeout(() => {
			if (i > 0) steps[i - 1].className = "pipeline-step done"
			steps[stage.idx].className = "pipeline-step running"
			bar.style.width = stage.pct + "%"
			pct.textContent = stage.pct + "%"
		}, stage.delay)
	})

	setTimeout(() => {
		steps[3].className = "pipeline-step done"
		headline.textContent = "2 Coordinated Swarms Isolated"
		doneBtn.style.display = "inline-flex"
	}, 2550)
}

function initAnalyzeWorkspace() {
	const dropzone = document.getElementById("csvDropzone")
	const fileInput = document.getElementById("csvFileInput")
	const loadSampleBtn = document.getElementById("loadSampleBtn")
	const windowRange = document.getElementById("windowRange")
	const windowLabel = document.getElementById("windowLabel")
	const runAnalysisBtn = document.getElementById("runAnalysisBtn")

	if (dropzone && fileInput) {
		dropzone.addEventListener("click", () => fileInput.click())
		dropzone.addEventListener("dragover", e => {
			e.preventDefault()
			dropzone.classList.add("dragover")
		})
		dropzone.addEventListener("dragleave", () =>
			dropzone.classList.remove("dragover"),
		)
		dropzone.addEventListener("drop", e => {
			e.preventDefault()
			dropzone.classList.remove("dragover")
			if (e.dataTransfer.files.length) {
				showSelectedFile(
					e.dataTransfer.files[0].name,
					"Custom upload • Schema verified",
				)
			}
		})
		fileInput.addEventListener("change", () => {
			if (fileInput.files.length) {
				showSelectedFile(fileInput.files[0].name, "Local CSV • Schema verified")
			}
		})
	}

	if (loadSampleBtn) {
		loadSampleBtn.addEventListener("click", e => {
			e.stopPropagation()
			loadSampleFile()
		})
	}

	document.querySelectorAll(".switch").forEach(sw => {
		sw.addEventListener("click", () => {
			sw.classList.toggle("on")
			sw.setAttribute("aria-checked", sw.classList.contains("on"))
		})
	})

	if (windowRange && windowLabel) {
		windowRange.addEventListener("input", () => {
			windowLabel.textContent = windowRange.value + " seconds"
		})
	}

	if (runAnalysisBtn) {
		runAnalysisBtn.addEventListener("click", runSimulatedAnalysis)
	}
}
