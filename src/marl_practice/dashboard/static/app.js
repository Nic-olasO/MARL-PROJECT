const state = {
  episodes: [],
  filtered: [],
  logPath: "runs/baselines.jsonl",
};

const els = {
  form: document.querySelector("#log-form"),
  logPath: document.querySelector("#log-path"),
  status: document.querySelector("#status"),
  policyFilter: document.querySelector("#policy-filter"),
  metrics: {
    episodes: document.querySelector("#metric-episodes"),
    returns: document.querySelector("#metric-return"),
    completion: document.querySelector("#metric-completion"),
    violations: document.querySelector("#metric-violations"),
  },
  returnRange: document.querySelector("#return-range"),
  returnChart: document.querySelector("#return-chart"),
  completionBars: document.querySelector("#completion-bars"),
  safetyBars: document.querySelector("#safety-bars"),
  table: document.querySelector("#episodes-table"),
  tableCount: document.querySelector("#table-count"),
};

function fmtNumber(value, digits = 2) {
  return Number(value || 0).toFixed(digits);
}

function fmtPercent(value) {
  return `${Math.round(Number(value || 0) * 100)}%`;
}

function safetyViolations(episode) {
  const safety = episode.safety_summary || {};
  if (Number.isFinite(Number(safety.total_violations))) {
    return Number(safety.total_violations);
  }
  return Number(safety.invalid_serves || 0) + Number(safety.collision_events || 0);
}

function visibleEpisodes() {
  const policy = els.policyFilter.value;
  if (policy === "all") return state.episodes;
  return state.episodes.filter((episode) => episode.policy_name === policy);
}

async function loadEpisodes(logPath) {
  els.status.textContent = `Loading ${logPath}`;
  const response = await fetch(`/api/episodes?path=${encodeURIComponent(logPath)}`);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const payload = await response.json();
  state.episodes = payload.episodes || [];
  state.logPath = payload.log_path || logPath;
  updatePolicyFilter();
  render();
  els.status.textContent = state.episodes.length
    ? `Loaded ${state.episodes.length} episode records from ${state.logPath}`
    : `No episode records found at ${state.logPath}`;
}

function updatePolicyFilter() {
  const current = els.policyFilter.value;
  const policies = [...new Set(state.episodes.map((episode) => episode.policy_name || "unknown"))].sort();
  els.policyFilter.innerHTML = '<option value="all">All policies</option>';
  for (const policy of policies) {
    const option = document.createElement("option");
    option.value = policy;
    option.textContent = policy;
    els.policyFilter.append(option);
  }
  els.policyFilter.value = policies.includes(current) ? current : "all";
}

function render() {
  state.filtered = visibleEpisodes();
  renderMetrics();
  renderReturnChart();
  renderCompletionBars();
  renderSafetyBars();
  renderTable();
}

function renderMetrics() {
  const episodes = state.filtered;
  const count = episodes.length || 1;
  const avgReturn = episodes.reduce((sum, item) => sum + Number(item.episode_return || 0), 0) / count;
  const avgCompletion = episodes.reduce((sum, item) => sum + Number(item.completion_rate || 0), 0) / count;
  const totalViolations = episodes.reduce((sum, item) => sum + safetyViolations(item), 0);

  els.metrics.episodes.textContent = String(episodes.length);
  els.metrics.returns.textContent = fmtNumber(avgReturn);
  els.metrics.completion.textContent = fmtPercent(avgCompletion);
  els.metrics.violations.textContent = String(totalViolations);
}

function renderReturnChart() {
  const episodes = state.filtered;
  els.returnChart.innerHTML = "";

  if (!episodes.length) {
    els.returnChart.innerHTML = '<div class="empty">Run a baseline with --log-path to populate this view.</div>';
    els.returnChart.style.setProperty("--bars", 1);
    els.returnRange.textContent = "No data";
    return;
  }

  const returns = episodes.map((episode) => Number(episode.episode_return || 0));
  const min = Math.min(...returns, 0);
  const max = Math.max(...returns, 1);
  const span = max - min || 1;
  els.returnRange.textContent = `${fmtNumber(min)} to ${fmtNumber(max)}`;
  els.returnChart.style.setProperty("--bars", String(episodes.length));

  for (const value of returns) {
    const bar = document.createElement("div");
    bar.className = "chart-bar";
    bar.title = `Return ${fmtNumber(value)}`;
    bar.style.height = `${Math.max(4, ((value - min) / span) * 100)}%`;
    els.returnChart.append(bar);
  }
}

function renderCompletionBars() {
  renderBarList(
    els.completionBars,
    state.filtered.slice(-8),
    (episode, index) => `#${episode.seed ?? index + 1}`,
    (episode) => Number(episode.completion_rate || 0),
    (episode) => fmtPercent(episode.completion_rate),
    false,
  );
}

function renderSafetyBars() {
  const episodes = state.filtered.slice(-8);
  const max = Math.max(...episodes.map(safetyViolations), 1);
  renderBarList(
    els.safetyBars,
    episodes,
    (episode, index) => `#${episode.seed ?? index + 1}`,
    (episode) => safetyViolations(episode) / max,
    (episode) => String(safetyViolations(episode)),
    true,
  );
}

function renderBarList(container, episodes, labelFn, valueFn, displayFn, warn) {
  container.innerHTML = "";
  if (!episodes.length) {
    container.innerHTML = '<div class="empty">No episodes yet.</div>';
    return;
  }

  episodes.forEach((episode, index) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <span>${labelFn(episode, index)}</span>
      <div class="track"><div class="fill ${warn ? "warn" : ""}" style="width: ${Math.max(0, Math.min(1, valueFn(episode))) * 100}%"></div></div>
      <strong>${displayFn(episode)}</strong>
    `;
    container.append(row);
  });
}

function renderTable() {
  const rows = [...state.filtered].slice(-12).reverse();
  els.table.innerHTML = "";
  els.tableCount.textContent = `${rows.length} rows`;

  for (const episode of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${episode.seed ?? ""}</td>
      <td>${episode.policy_name || "unknown"}</td>
      <td>${episode.steps ?? 0}</td>
      <td>${fmtNumber(episode.episode_return)}</td>
      <td>${episode.completed_tasks ?? 0}</td>
      <td>${fmtPercent(episode.completion_rate)}</td>
      <td>${safetyViolations(episode)}</td>
    `;
    els.table.append(tr);
  }
}

els.form.addEventListener("submit", (event) => {
  event.preventDefault();
  loadEpisodes(els.logPath.value).catch((error) => {
    els.status.textContent = `Could not load episodes: ${error.message}`;
  });
});

els.policyFilter.addEventListener("change", render);

loadEpisodes(state.logPath).catch((error) => {
  els.status.textContent = `Could not load episodes: ${error.message}`;
});
