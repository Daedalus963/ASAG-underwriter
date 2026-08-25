// Point this at your running FastAPI backend.
const API_BASE = window.ASAG_API_BASE || "http://127.0.0.1:8000";
const GOOGLE_MAPS_API_KEY = window.ASAG_GOOGLE_MAPS_API_KEY || "";

const state = {
  token: localStorage.getItem("asag_token") || null,
  applicants: [],
  selectedApplicant: null,
  lastAgriData: null,
  lastEmotionData: null,
  map: null,
  mapScriptPromise: null,
};

// ---------- helpers ----------
async function api(path, { method = "GET", body, isForm = false } = {}) {
  const headers = {};
  if (state.token) headers["Authorization"] = `Bearer ${state.token}`;
  if (!isForm && body !== undefined) headers["Content-Type"] = "application/json";

  const resp = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : (isForm ? body : JSON.stringify(body)),
  });

  let data = null;
  try { data = await resp.json(); } catch (_) { /* no body */ }

  if (!resp.ok) {
    const detail = data && data.detail ? data.detail : `Request failed (${resp.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

function setMsg(el, text, kind) {
  el.textContent = text || "";
  el.className = "form-msg" + (kind ? ` ${kind}` : "");
}

function showView(id) {
  document.querySelectorAll(".view").forEach(v => v.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}

// ---------- auth ----------
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const loginMsg = document.getElementById("login-msg");
const registerMsg = document.getElementById("register-msg");

document.getElementById("show-register").onclick = () => {
  loginForm.classList.add("hidden");
  registerForm.classList.remove("hidden");
};
document.getElementById("show-login").onclick = () => {
  registerForm.classList.add("hidden");
  loginForm.classList.remove("hidden");
};

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  setMsg(loginMsg, "Signing in…");
  try {
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    const data = await api("/auth/login", { method: "POST", body: { email, password } });
    state.token = data.access_token;
    localStorage.setItem("asag_token", state.token);
    setMsg(loginMsg, "");
    await enterDashboard();
  } catch (err) {
    setMsg(loginMsg, err.message, "error");
  }
});

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  setMsg(registerMsg, "Creating account…");
  try {
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    const role = document.getElementById("register-role").value;
    await api("/auth/register", { method: "POST", body: { email, password, role } });
    setMsg(registerMsg, "Account created. Sign in now.", "success");
    setTimeout(() => {
      registerForm.classList.add("hidden");
      loginForm.classList.remove("hidden");
      document.getElementById("login-email").value = email;
    }, 700);
  } catch (err) {
    setMsg(registerMsg, err.message, "error");
  }
});

document.getElementById("logout-btn").onclick = () => {
  state.token = null;
  localStorage.removeItem("asag_token");
  showView("view-login");
};

async function enterDashboard() {
  const me = await api("/auth/me");
  document.getElementById("whoami").textContent = `${me.email} · ${me.role}`;
  showView("view-dashboard");
  await refreshApplicants();
}

// ---------- tabs ----------
document.querySelectorAll(".rail-tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".rail-tab").forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.add("hidden"));
    document.getElementById(`tab-${tab.dataset.tab}`).classList.remove("hidden");
  });
});

// ---------- applicant creation ----------
document.getElementById("applicant-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = document.getElementById("applicant-msg");
  setMsg(msg, "Saving…");
  try {
    const payload = {
      display_name: document.getElementById("f-name").value,
      latitude: parseFloat(document.getElementById("f-lat").value),
      longitude: parseFloat(document.getElementById("f-lon").value),
      crop_type: document.getElementById("f-crop").value || null,
      farm_size_acres: document.getElementById("f-acres").value ? parseFloat(document.getElementById("f-acres").value) : null,
      loan_amount_inr: document.getElementById("f-loan").value ? parseFloat(document.getElementById("f-loan").value) : null,
    };
    await api("/applicants", { method: "POST", body: payload });
    setMsg(msg, "Applicant saved.", "success");
    e.target.reset();
    await refreshApplicants();
  } catch (err) {
    setMsg(msg, err.message, "error");
  }
});

// ---------- applicant list + workspace ----------
async function refreshApplicants() {
  state.applicants = await api("/applicants");
  document.getElementById("applicant-count").textContent = state.applicants.length;
  const list = document.getElementById("applicant-list");
  list.innerHTML = "";
  state.applicants.forEach(a => {
    const li = document.createElement("li");
    li.className = "applicant-item" + (state.selectedApplicant?.id === a.id ? " selected" : "");
    li.innerHTML = `<div class="a-name">${escapeHtml(a.display_name)}</div>
      <div class="a-meta">${a.latitude.toFixed(3)}, ${a.longitude.toFixed(3)} · ${a.crop_type || "—"}</div>`;
    li.onclick = () => selectApplicant(a);
    list.appendChild(li);
  });
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function selectApplicant(applicant) {
  state.selectedApplicant = applicant;
  state.lastAgriData = null;
  state.lastEmotionData = null;
  refreshApplicants();
  renderWorkspace();
}

function renderWorkspace() {
  const ws = document.getElementById("workspace");
  const a = state.selectedApplicant;
  if (!a) {
    ws.innerHTML = `<p class="workspace-empty">Select an applicant from the ledger to begin an assessment.</p>`;
    return;
  }

  ws.innerHTML = `
    <div class="ws-section">
      <h3>${escapeHtml(a.display_name)}</h3>
      <div class="data-line"><span>Coordinates</span><span>${a.latitude}, ${a.longitude}</span></div>
      <div class="data-line"><span>Crop</span><span>${a.crop_type || "—"}</span></div>
      <div class="data-line"><span>Farm size</span><span>${a.farm_size_acres ?? "—"} acres</span></div>
      <div class="data-line"><span>Loan requested</span><span>₹${a.loan_amount_inr ?? "—"}</span></div>
    </div>

    <div class="ws-section location-section">
      <div class="section-title-row">
        <div>
          <h3><span class="step-index">MAP</span> Farm location <span class="source-label">SATELLITE CONTEXT</span></h3>
          <p class="section-help">Inspect the farm area around the submitted coordinates. Imagery may not be real-time.</p>
        </div>
        <a class="btn btn-ghost btn-sm" target="_blank" rel="noopener" href="https://www.google.com/maps/@${a.latitude},${a.longitude},17z/data=!3m1!1e3">Open in Google Maps</a>
      </div>
      <div class="map-frame" id="farm-map"><div class="map-loading">Loading satellite context…</div></div>
      <div class="map-note"><strong>Shows:</strong> Google satellite imagery and the submitted farm point. <strong>Does not show:</strong> live soil moisture. That signal is fetched separately below.</div>
    </div>

    <div class="ws-section">
      <h3><span class="step-index">01</span> Land conditions <span class="source-label">LIVE · Open-Meteo</span></h3>
      <p class="section-help">Use the applicant's coordinates to check current soil moisture, temperature, and precipitation.</p>
      <div class="ws-row">
        <button class="btn btn-ghost btn-sm" id="btn-fetch-agri">Fetch live soil data</button>
      </div>
      <div id="agri-result"></div>
    </div>

    <div class="ws-section">
      <h3><span class="step-index">02</span> Applicant audio <span class="source-label">EXPERIMENTAL SIGNAL</span></h3>
      <p class="section-help">Upload a short clip to generate an experimental acoustic feature summary.</p>
      <div class="ws-row">
        <input type="file" id="audio-file" accept=".wav,.mp3,.flac,.m4a">
        <button class="btn btn-ghost btn-sm" id="btn-analyze-audio">Analyze clip</button>
      </div>
      <div id="emotion-result"></div>
    </div>

    <div class="ws-section">
      <h3><span class="step-index">03</span> Assessment brief <span class="source-label">SIMULATED DECISION</span></h3>
      <p class="section-help">Combine the available signals into a reviewable, fully explained prototype output.</p>
      <div class="ws-row">
        <button class="btn btn-primary" id="btn-run-assess">Run assessment</button>
      </div>
      <div id="assess-result"></div>
    </div>
  `;

  document.getElementById("btn-fetch-agri").onclick = fetchAgriData;
  document.getElementById("btn-analyze-audio").onclick = analyzeAudio;
  document.getElementById("btn-run-assess").onclick = runAssessment;
  loadFarmMap(a);
}

function loadGoogleMapsScript() {
  if (window.google?.maps) return Promise.resolve();
  if (state.mapScriptPromise) return state.mapScriptPromise;
  if (!GOOGLE_MAPS_API_KEY) return Promise.reject(new Error("Google Maps API key is not configured."));

  state.mapScriptPromise = new Promise((resolve, reject) => {
    const callbackName = "asagGoogleMapsReady";
    window[callbackName] = () => {
      delete window[callbackName];
      resolve();
    };
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(GOOGLE_MAPS_API_KEY)}&callback=${callbackName}`;
    script.async = true;
    script.defer = true;
    script.onerror = () => reject(new Error("Google Maps could not be loaded."));
    document.head.appendChild(script);
  });
  return state.mapScriptPromise;
}

async function loadFarmMap(applicant) {
  const container = document.getElementById("farm-map");
  if (!container) return;
  try {
    await loadGoogleMapsScript();
    const position = { lat: applicant.latitude, lng: applicant.longitude };
    state.map = new google.maps.Map(container, {
      center: position, zoom: 17, mapTypeId: "satellite",
      fullscreenControl: true, streetViewControl: false, mapTypeControl: true,
      gestureHandling: "greedy",
    });
    new google.maps.Marker({ map: state.map, position, title: applicant.display_name });
  } catch (_) {
    container.innerHTML = `<div class="map-setup"><strong>Satellite view ready to connect</strong><span>Add a browser-restricted Google Maps API key as <code>window.ASAG_GOOGLE_MAPS_API_KEY</code> before <code>app.js</code> to embed imagery here.</span><a target="_blank" rel="noopener" href="https://www.google.com/maps/@${applicant.latitude},${applicant.longitude},17z/data=!3m1!1e3">Open this location in Google Maps satellite view</a></div>`;
  }
}

async function fetchAgriData() {
  const a = state.selectedApplicant;
  const box = document.getElementById("agri-result");
  box.innerHTML = `<p class="form-msg">Fetching…</p>`;
  try {
    const data = await api(`/agri/soil-moisture?latitude=${a.latitude}&longitude=${a.longitude}`);
    state.lastAgriData = data;
    box.innerHTML = `
      <div class="data-line"><span>Source</span><span>${data.source}</span></div>
      <div class="data-line"><span>Soil moisture</span><span>${data.soil_moisture_m3_m3 ?? "n/a"} m³/m³</span></div>
      <div class="data-line"><span>Soil temperature</span><span>${data.soil_temperature_c ?? "n/a"} °C</span></div>
      <div class="data-line"><span>Risk flag</span><span>${data.risk_flag}</span></div>
    `;
  } catch (err) {
    box.innerHTML = `<p class="form-msg error">${err.message}</p>`;
  }
}

async function analyzeAudio() {
  const fileInput = document.getElementById("audio-file");
  const box = document.getElementById("emotion-result");
  if (!fileInput.files.length) {
    box.innerHTML = `<p class="form-msg error">Choose an audio file first.</p>`;
    return;
  }
  box.innerHTML = `<p class="form-msg">Analyzing…</p>`;
  try {
    const fd = new FormData();
    fd.append("file", fileInput.files[0]);
    const data = await api("/emotion/analyze", { method: "POST", body: fd, isForm: true });
    state.lastEmotionData = data;
    box.innerHTML = `
      <div class="data-line"><span>Mode</span><span>${data.mode}</span></div>
      <div class="data-line"><span>Predicted emotion</span><span>${data.predicted_emotion}</span></div>
      <div class="data-line"><span>Confidence</span><span>${data.confidence ?? "n/a"}</span></div>
      ${data.warning ? `<div class="disclaimer-box">${data.warning}</div>` : ""}
    `;
  } catch (err) {
    box.innerHTML = `<p class="form-msg error">${err.message}</p>`;
  }
}

async function runAssessment() {
  const box = document.getElementById("assess-result");
  const a = state.selectedApplicant;

  if (!state.lastAgriData || !state.lastEmotionData) {
    box.innerHTML = `<p class="form-msg error">Run steps 1 and 2 first.</p>`;
    return;
  }
  box.innerHTML = `<p class="form-msg">Scoring…</p>`;
  try {
    const data = await api(`/credit/assess/${a.id}`, {
      method: "POST",
      body: { agri_data: state.lastAgriData, emotion_data: state.lastEmotionData },
    });

    const stampClass = data.decision.startsWith("APPROVED") ? "approved"
      : data.decision.startsWith("DECLINED") ? "declined" : "review";

    const rows = data.explanation.map(row => {
      const sign = row.contribution > 0 ? "pos" : row.contribution < 0 ? "neg" : "";
      return `<li><span class="factor">${row.factor} — ${row.note}</span><span class="contrib ${sign}">${row.contribution > 0 ? "+" : ""}${row.contribution}</span></li>`;
    }).join("");

    box.innerHTML = `
      <div class="ws-row" style="align-items:flex-start; gap:24px;">
        <div class="stamp ${stampClass}">${data.decision.replace(/_/g, " ")}</div>
        <div style="flex:1;">
          <div class="data-line"><span>Simulated risk score</span><span>${data.total_simulated_risk}</span></div>
          <div class="data-line"><span>Suggested LTV cap</span><span>${data.suggested_ltv_cap}</span></div>
        </div>
      </div>
      <ul class="explanation-list">${rows}</ul>
      <div class="disclaimer-box">${data.disclaimer}</div>
    `;
  } catch (err) {
    box.innerHTML = `<p class="form-msg error">${err.message}</p>`;
  }
}

// ---------- boot ----------
(async function boot() {
  if (state.token) {
    try {
      await enterDashboard();
      return;
    } catch (_) {
      localStorage.removeItem("asag_token");
      state.token = null;
    }
  }
  showView("view-login");
})();
