/* ── Apex ETA Agent — Dashboard JS ─────────────────────────────────────── */

const MODE_COLORS = {
  autonomous:           "#2E8648",
  supervised:           "#D47E00",
  escalate_dispatcher:  "#C0392B",
  escalate_human:       "#C0392B",
};

const MODE_LABELS = {
  autonomous:           "AUTONOMOUS",
  supervised:           "SUPERVISED",
  escalate_dispatcher:  "ESCALATE → DISPATCHER",
  escalate_human:       "ESCALATE → HUMAN",
};

const MODE_BG = {
  autonomous:           "#E8F5EB",
  supervised:           "#FFF3E0",
  escalate_dispatcher:  "#FFEBEE",
  escalate_human:       "#FFEBEE",
};

// ── Work stream chart ────────────────────────────────────────────────────── //
(function initWorkstreamChart() {
  const ctx = document.getElementById("chart-workstream").getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: WORKSTREAM.labels,
      datasets: [
        {
          label: "Total volume/day",
          data: WORKSTREAM.volumes,
          backgroundColor: WORKSTREAM.colors.map(c => c + "33"),
          borderColor:     WORKSTREAM.colors,
          borderWidth: 2,
          yAxisID: "y",
        },
        {
          label: "Automatable % (right axis)",
          data: WORKSTREAM.automatable_pct,
          type: "line",
          borderColor: "#1B2A4A",
          backgroundColor: "transparent",
          pointBackgroundColor: "#1B2A4A",
          borderWidth: 2,
          pointRadius: 5,
          yAxisID: "y2",
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom", labels: { font: { size: 11 } } },
        tooltip: {
          callbacks: {
            afterBody: (items) => {
              const i = items[0].dataIndex;
              return [
                `Daily minutes: ${WORKSTREAM.daily_minutes[i].toLocaleString()}`,
                `Recoverable mins: ${WORKSTREAM.recoverable_minutes[i].toLocaleString()}`,
              ];
            },
          },
        },
      },
      scales: {
        y:  { title: { display: true, text: "Cases/day", font: { size: 11 } }, grid: { color: "#EEF2F7" } },
        y2: {
          position: "right",
          title: { display: true, text: "Automatable %", font: { size: 11 } },
          min: 0, max: 100,
          grid: { display: false },
        },
      },
    },
  });
})();

// ── Capacity chart ───────────────────────────────────────────────────────── //
(function initCapacityChart() {
  const ctx = document.getElementById("chart-capacity").getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: WORKSTREAM.labels,
      datasets: [
        {
          label: "Total person-min/day",
          data: WORKSTREAM.daily_minutes,
          backgroundColor: "#CCD6E044",
          borderColor: "#CCD6E0",
          borderWidth: 1,
        },
        {
          label: "Recoverable person-min/day",
          data: WORKSTREAM.recoverable_minutes,
          backgroundColor: WORKSTREAM.colors.map(c => c + "BB"),
          borderColor:     WORKSTREAM.colors,
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom", labels: { font: { size: 11 } } } },
      scales: {
        y: { title: { display: true, text: "Person-min/day", font: { size: 11 } }, grid: { color: "#EEF2F7" } },
      },
    },
  });
})();

// ── Mode donut — mutable ─────────────────────────────────────────────────── //
let modeChart;
(function initModeChart() {
  const ctx = document.getElementById("chart-modes").getContext("2d");
  modeChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Autonomous", "Supervised", "Escalated"],
      datasets: [{
        data: [0, 0, 0],
        backgroundColor: ["#2E8648", "#D47E00", "#C0392B"],
        borderWidth: 3,
        borderColor: "#fff",
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: "65%",
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (item) => {
              const total = item.dataset.data.reduce((a, b) => a + b, 0);
              const pct = total ? ((item.raw / total) * 100).toFixed(1) : 0;
              return ` ${item.label}: ${item.raw} (${pct}%)`;
            },
          },
        },
      },
    },
  });
})();

function updateModeChart(auto, sup, esc) {
  modeChart.data.datasets[0].data = [auto, sup, esc];
  modeChart.update();
}

// ── KPI refresh ──────────────────────────────────────────────────────────── //
async function refreshStats() {
  try {
    const r = await fetch("/api/stats");
    const d = await r.json();
    document.getElementById("kpi-total-val").textContent = d.total || "0";
    document.getElementById("kpi-auto-val").textContent  = d.total ? d.autonomous_pct + "%" : "—";
    document.getElementById("kpi-sup-val").textContent   = d.total ? d.supervised_pct  + "%" : "—";
    document.getElementById("kpi-esc-val").textContent   = d.total ? d.escalated_pct   + "%" : "—";
    document.getElementById("kpi-gps-val").textContent   = d.avg_gps_age_minutes ?? "—";
    if (d.total) {
      updateModeChart(d.autonomous_count, d.supervised_count, d.escalated_count);
    }
  } catch (_) {}
}

// ── Log refresh ──────────────────────────────────────────────────────────── //
async function refreshLog() {
  try {
    const r = await fetch("/api/interactions?limit=25");
    const rows = await r.json();
    const tbody = document.getElementById("log-tbody");
    if (!rows.length) {
      tbody.innerHTML = `<tr class="log-empty"><td colspan="7">No interactions yet — run a demo above</td></tr>`;
      return;
    }
    tbody.innerHTML = rows.map(e => {
      const dest = e.escalation_destination || "—";
      const gps  = e.gps_age_minutes != null ? e.gps_age_minutes + " min" : "—";
      const t = new Date(e.timestamp_utc).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
      return `<tr>
        <td>${e.case_id}</td>
        <td>${e.order_id || "—"}</td>
        <td>${e.inquiry_channel}</td>
        <td><span class="log-mode log-mode-${e.mode}">${e.mode.replace("_", " ")}</span></td>
        <td>${gps}</td>
        <td>${dest}</td>
        <td>${t}</td>
      </tr>`;
    }).join("");
  } catch (_) {}
}

// ── Run inquiry ──────────────────────────────────────────────────────────── //
async function runInquiry(orderId, channel, label) {
  const panel = document.getElementById("result-panel");
  panel.classList.remove("hidden");
  panel.className = "result-panel";

  document.getElementById("result-message").textContent = "Processing…";
  document.getElementById("result-mode-badge").textContent = "";
  document.getElementById("result-case-id").textContent = "";
  document.getElementById("result-order").textContent = "—";
  document.getElementById("result-gps").textContent = "—";
  document.getElementById("result-dest").textContent = "—";
  document.getElementById("result-reason").textContent = "";

  try {
    const res = await fetch("/api/inquiry", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        order_id:  orderId,
        channel:   channel,
        raw_query: label || `Where is order ${orderId}?`,
      }),
    });
    const d = await res.json();

    panel.classList.add(`mode-${d.mode}`);

    const badge = document.getElementById("result-mode-badge");
    badge.textContent = MODE_LABELS[d.mode] || d.mode.toUpperCase();
    badge.style.background = MODE_BG[d.mode] || "#EEF2F7";
    badge.style.color       = MODE_COLORS[d.mode] || "#1B2A4A";

    document.getElementById("result-case-id").textContent = d.case_id;
    document.getElementById("result-message").textContent = d.customer_message;
    document.getElementById("result-order").textContent   = d.order_id || "not found";
    document.getElementById("result-gps").textContent     = d.gps_age_minutes != null ? d.gps_age_minutes + " min" : "unavailable";
    document.getElementById("result-dest").textContent    = d.escalation_destination || "none (agent replied)";
    document.getElementById("result-reason").textContent  = "Decision: " + d.reason;

    panel.scrollIntoView({ behavior: "smooth", block: "nearest" });

    refreshStats();
    refreshLog();
  } catch (err) {
    document.getElementById("result-message").textContent = "Error: " + err.message;
  }
}

// ── Wire up scenario buttons ─────────────────────────────────────────────── //
document.querySelectorAll(".scenario-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".scenario-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    runInquiry(btn.dataset.order, btn.dataset.channel, btn.dataset.label);
  });
});

// ── Manual form ──────────────────────────────────────────────────────────── //
document.getElementById("btn-manual").addEventListener("click", () => {
  const orderId  = document.getElementById("manual-order").value.trim().toUpperCase();
  const channel  = document.getElementById("manual-channel").value;
  if (!orderId) { alert("Enter an order ID"); return; }
  document.querySelectorAll(".scenario-btn").forEach(b => b.classList.remove("active"));
  runInquiry(orderId, channel);
});
document.getElementById("manual-order").addEventListener("keydown", e => {
  if (e.key === "Enter") document.getElementById("btn-manual").click();
});

// ── Log refresh button ───────────────────────────────────────────────────── //
document.getElementById("btn-refresh-log").addEventListener("click", refreshLog);

// ── Initial load ─────────────────────────────────────────────────────────── //
refreshStats();
refreshLog();
