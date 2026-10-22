/**
 * Automobile AI Assistant — Apple Store Experience
 * Client Application Logic
 */

// Application Global State
const state = {
  activeVehicle: null,
  vehicles: [],
  selectedSymptoms: new Set(),
  diagnosisMode: 'ai',
  liveObd: null,
  isAutoStreaming: true,
  streamInterval: null,
  speechRecognition: null,
  isRecording: false,
  datasetFaults: [],
  currentDatasetFilter: 'All',
  datasetOffset: 0,
  datasetLimit: 15,
  datasetTotal: 1500,
  datasetFilterFault: 'All'
};

// Symptom Definitions by Automotive Domain Category
const SYMPTOM_CATEGORIES = {
  "🔧 Powertrain & Combustion": [
    "Engine vibration",
    "Engine overheating",
    "Engine not starting",
    "Engine stalling",
    "Poor acceleration",
    "Low engine power"
  ],
  "⛽ Fuel & Air Delivery": [
    "Poor mileage",
    "High fuel consumption",
    "Fuel smell"
  ],
  "🛑 Braking & Deceleration": [
    "Brake noise",
    "Brake vibration",
    "Weak braking"
  ],
  "⚡ Electrical & Ignition": [
    "Battery problem",
    "Starter problem",
    "Warning light"
  ],
  "🔊 Acoustic Anomalies": [
    "Clicking sound",
    "Grinding sound",
    "Knocking sound",
    "Whistling sound"
  ]
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
  setupTheme();
  setupNavigation();
  setupSymptomCategories();
  setupSpeechRecognition();
  setupFormHandlers();
  setupOBDStreaming();
  setupRangeValueDisplays();
  setupDatasetExplorer();
  setupModalHandlers();

  // Load initial application data
  await loadVehicles();
  await loadDashboardStats();
  await loadHealthScore();
  await loadDiagnosisHistory();
  await loadFaultsCatalog();
  await loadRawDatasetRecords('All', 0);
});

// ============================================================================
// THEME MANAGEMENT (Apple Store Light / Apple Pro Dark Titanium)
// ============================================================================

function setupTheme() {
  const savedTheme = localStorage.getItem('apple_store_theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  const themeBtn = document.getElementById('apple-theme-toggle');
  themeBtn?.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const nextTheme = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nextTheme);
    localStorage.setItem('apple_store_theme', nextTheme);
    updateThemeIcon(nextTheme);
    showToast(`Switched to Apple ${nextTheme === 'dark' ? 'Pro Dark Titanium' : 'Store Clean Light'} Mode`, 'info');
  });
}

function updateThemeIcon(theme) {
  const btn = document.getElementById('apple-theme-toggle');
  if (btn) {
    btn.textContent = theme === 'dark' ? '☀️' : '🌓';
    btn.title = theme === 'dark' ? 'Switch to Apple Store Light Mode' : 'Switch to Apple Pro Dark Titanium Mode';
  }
}

// ============================================================================
// NAVIGATION & TABS
// ============================================================================

function setupNavigation() {
  // Global Top Navigation Buttons
  const navButtons = document.querySelectorAll('.apple-nav-btn');
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      switchTab(targetId);
    });
  });

  // Circular Category Shelf Buttons
  const shelfButtons = document.querySelectorAll('.shelf-item-btn');
  shelfButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-shelf-tab');
      switchTab(targetId);
    });
  });

  // Brand click returns to Store dashboard
  document.getElementById('brand-home-btn')?.addEventListener('click', () => {
    switchTab('tab-dashboard');
  });

  // Quick Action Buttons
  document.getElementById('dash-quick-diag-btn')?.addEventListener('click', () => switchTab('tab-diagnose'));
  document.getElementById('qa-diagnose-btn')?.addEventListener('click', () => switchTab('tab-diagnose'));
  document.getElementById('qa-obd-btn')?.addEventListener('click', () => switchTab('tab-obd'));
  document.getElementById('dash-edit-vehicle-btn')?.addEventListener('click', () => switchTab('tab-vehicles'));

  // Hero Section Buttons
  document.getElementById('hero-quick-diag-btn')?.addEventListener('click', () => switchTab('tab-diagnose'));
  document.getElementById('hero-voice-assistant-btn')?.addEventListener('click', () => {
    switchTab('tab-diagnose');
    setTimeout(() => {
      const mic = document.getElementById('voice-mic-btn');
      mic?.click();
    }, 400);
  });
  document.getElementById('ribbon-learn-more-btn')?.addEventListener('click', () => switchTab('tab-dataset'));

  // Showcase Cards on Store page
  document.getElementById('feat-card-diag')?.addEventListener('click', () => switchTab('tab-diagnose'));
  document.getElementById('feat-card-dataset')?.addEventListener('click', () => switchTab('tab-dataset'));
  document.getElementById('feat-card-obd')?.addEventListener('click', () => switchTab('tab-obd'));

  // Global Header Vehicle Switcher
  const selectEl = document.getElementById('global-vehicle-select');
  selectEl?.addEventListener('change', async (e) => {
    const reg = e.target.value;
    if (reg) {
      await setActiveVehicle(reg);
    }
  });
}

function switchTab(tabId) {
  // Update Top Nav
  document.querySelectorAll('.apple-nav-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
  });

  // Update Category Shelf Buttons
  document.querySelectorAll('.shelf-item-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-shelf-tab') === tabId);
  });

  // Update Tab Sections
  document.querySelectorAll('.page-tab-content').forEach(section => {
    section.classList.toggle('active', section.id === tabId);
  });

  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Tab-specific refreshes
  if (tabId === 'tab-dashboard') {
    loadDashboardStats();
  } else if (tabId === 'tab-vehicles') {
    loadVehicles();
  } else if (tabId === 'tab-health') {
    loadHealthScore();
  } else if (tabId === 'tab-history') {
    loadDiagnosisHistory();
  } else if (tabId === 'tab-obd') {
    fetchLiveObd();
  } else if (tabId === 'tab-dataset') {
    loadFaultsCatalog();
  }
}

// ============================================================================
// VEHICLE MANAGEMENT
// ============================================================================

async function loadVehicles() {
  try {
    const res = await fetch('/api/vehicles');
    const data = await res.json();
    state.vehicles = data.vehicles || [];

    const activeRes = await fetch('/api/active-vehicle');
    const activeData = await activeRes.json();
    state.activeVehicle = activeData.vehicle;

    populateVehicleSelectors();
    renderFleetCards();
  } catch (err) {
    console.error('Error loading vehicles:', err);
    showToast('Failed to load fleet profiles', 'error');
  }
}

function populateVehicleSelectors() {
  const selectEl = document.getElementById('global-vehicle-select');
  if (!selectEl) return;
  selectEl.innerHTML = '';

  if (state.vehicles.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = 'No Registered Vehicles';
    selectEl.appendChild(opt);
    return;
  }

  state.vehicles.forEach(v => {
    const opt = document.createElement('option');
    opt.value = v.registration_number;
    opt.textContent = `${v.manufacturer} ${v.model} (${v.registration_number})`;
    if (state.activeVehicle && state.activeVehicle.registration_number === v.registration_number) {
      opt.selected = true;
    }
    selectEl.appendChild(opt);
  });
}

function renderFleetCards() {
  const container = document.getElementById('fleet-container');
  const countBadge = document.getElementById('fleet-count-badge');
  if (!container) return;

  if (countBadge) {
    countBadge.textContent = `${state.vehicles.length} Vehicle${state.vehicles.length === 1 ? '' : 's'}`;
  }

  if (state.vehicles.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 2.5rem; color: var(--text-tertiary);">
        <p>No vehicles currently registered in garage fleet.</p>
        <p style="font-size: 0.8rem; margin-top: 0.4rem;">Use the form to add your first automobile.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = state.vehicles.map(v => {
    const isActive = state.activeVehicle && state.activeVehicle.registration_number === v.registration_number;
    return `
      <div class="apple-card" style="padding: 18px; border-color: ${isActive ? 'var(--apple-blue)' : 'var(--border-subtle)'}; background: ${isActive ? 'var(--bg-card-subtle)' : 'var(--bg-card)'};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
          <div>
            <h4 style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin-bottom: 2px;">
              ${v.manufacturer} ${v.model}
            </h4>
            <span class="car-reg-badge">${v.registration_number}</span>
          </div>
          ${isActive ? `
            <span style="font-size: 0.72rem; font-weight: 700; color: var(--apple-blue); background: var(--apple-blue-tint); padding: 4px 10px; border-radius: var(--radius-pill);">
              ✓ ACTIVE TARGET
            </span>
          ` : `
            <button class="btn-apple-secondary" style="padding: 4px 12px; font-size: 0.75rem;" onclick="setActiveVehicle('${v.registration_number}')">
              Set Active
            </button>
          `}
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; font-size: 0.78rem; color: var(--text-secondary); margin-bottom: 12px;">
          <div>Year: <strong>${v.manufacturing_year}</strong></div>
          <div>Fuel: <strong>${v.fuel_type}</strong></div>
          <div>Transmission: <strong>${v.transmission_type}</strong></div>
          <div>Mileage: <strong>${v.current_mileage.toLocaleString()} km</strong></div>
          <div style="grid-column: span 2;">Last Service: <strong>${v.last_service_date || 'N/A'}</strong></div>
        </div>

        <div style="display: flex; gap: 8px; justify-content: flex-end; border-top: 1px solid var(--border-subtle); padding-top: 10px;">
          <button class="btn-apple-secondary" style="padding: 4px 10px; font-size: 0.72rem;" onclick="editVehicle('${v.registration_number}')">
            ✏️ Edit Profile
          </button>
          <button class="btn-apple-secondary" style="padding: 4px 10px; font-size: 0.72rem; color: var(--apple-red);" onclick="deleteVehicle('${v.registration_number}')">
            🗑️ Remove
          </button>
        </div>
      </div>
    `;
  }).join('');
}

async function setActiveVehicle(reg) {
  try {
    const res = await fetch('/api/active-vehicle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ registration_number: reg })
    });
    const data = await res.json();
    if (data.success) {
      state.activeVehicle = data.active_vehicle;
      populateVehicleSelectors();
      renderFleetCards();
      loadDashboardStats();
      loadHealthScore();
      showToast(`Active vehicle switched to ${data.active_vehicle.manufacturer} ${data.active_vehicle.model}`, 'success');
    }
  } catch (err) {
    showToast('Failed to switch active vehicle', 'error');
  }
}

function editVehicle(reg) {
  const v = state.vehicles.find(item => item.registration_number === reg);
  if (!v) return;

  document.getElementById('form-reg-number').value = v.registration_number;
  document.getElementById('form-manufacturer').value = v.manufacturer;
  document.getElementById('form-model').value = v.model;
  document.getElementById('form-year').value = v.manufacturing_year;
  document.getElementById('form-fuel').value = v.fuel_type;
  document.getElementById('form-transmission').value = v.transmission_type;
  document.getElementById('form-mileage').value = v.current_mileage;
  document.getElementById('form-service-date').value = v.last_service_date || '2025-10-01';

  document.getElementById('vehicle-form-mode-title').textContent = `Update ${v.model} (${v.registration_number})`;
  document.getElementById('form-reg-number').scrollIntoView({ behavior: 'smooth' });
}

async function deleteVehicle(reg) {
  if (!confirm(`Are you sure you want to remove ${reg} from your garage fleet?`)) return;

  try {
    const res = await fetch(`/api/vehicles/${encodeURIComponent(reg)}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, 'info');
      await loadVehicles();
      await loadDashboardStats();
    }
  } catch (err) {
    showToast('Failed to delete vehicle', 'error');
  }
}

function setupFormHandlers() {
  const form = document.getElementById('vehicle-registration-form');
  form?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const payload = {
      registration_number: document.getElementById('form-reg-number').value.trim(),
      manufacturer: document.getElementById('form-manufacturer').value.trim(),
      model: document.getElementById('form-model').value.trim(),
      manufacturing_year: parseInt(document.getElementById('form-year').value, 10),
      fuel_type: document.getElementById('form-fuel').value,
      transmission_type: document.getElementById('form-transmission').value,
      current_mileage: parseInt(document.getElementById('form-mileage').value, 10) || 0,
      last_service_date: document.getElementById('form-service-date').value
    };

    try {
      const res = await fetch('/api/vehicles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        showToast(data.message, 'success');
        form.reset();
        document.getElementById('vehicle-form-mode-title').textContent = 'Register Vehicle';
        await loadVehicles();
        await loadDashboardStats();
      }
    } catch (err) {
      showToast('Error saving vehicle profile', 'error');
    }
  });

  document.getElementById('reset-vehicle-form-btn')?.addEventListener('click', () => {
    form?.reset();
    document.getElementById('vehicle-form-mode-title').textContent = 'Register Vehicle';
  });
}

// ============================================================================
// DASHBOARD STATS
// ============================================================================

async function loadDashboardStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();

    const car = data.active_vehicle;
    if (car) {
      document.getElementById('dash-active-car-name').textContent = `${car.manufacturer} ${car.model}`;
      document.getElementById('dash-active-car-reg').textContent = car.registration_number;

      document.getElementById('dash-card-model').textContent = `${car.manufacturer} ${car.model}`;
      document.getElementById('dash-card-reg').textContent = car.registration_number;

      document.getElementById('dash-spec-year').textContent = car.manufacturing_year;
      document.getElementById('dash-spec-fuel').textContent = car.fuel_type;
      document.getElementById('dash-spec-transmission').textContent = car.transmission_type;
      document.getElementById('dash-spec-mileage').textContent = `${car.current_mileage.toLocaleString()} km`;
      document.getElementById('dash-spec-service').textContent = car.last_service_date || 'N/A';

      const age = new Date().getFullYear() - car.manufacturing_year;
      document.getElementById('dash-spec-age').textContent = `${Math.max(0, age)} years`;
    } else {
      document.getElementById('dash-active-car-name').textContent = 'No Vehicle';
      document.getElementById('dash-active-car-reg').textContent = 'Register first';
      document.getElementById('dash-card-model').textContent = 'No Vehicle Active';
      document.getElementById('dash-card-reg').textContent = 'PLEASE REGISTER';
    }

    document.getElementById('dash-health-score').textContent = `${data.health_score} / 100`;
    document.getElementById('dash-health-rating').textContent =
      data.health_score > 80 ? 'Optimal Condition' :
      data.health_score > 50 ? 'Service Recommended' : 'Critical Faults Detected';

    document.getElementById('dash-total-diagnoses').textContent = data.total_diagnoses;
    document.getElementById('dash-vehicle-diag-count').textContent = `${data.active_vehicle_diagnoses} for active car`;

    const last = data.last_diagnosis;
    if (last) {
      document.getElementById('dash-last-fault').textContent = last.predicted_fault;
      document.getElementById('dash-last-severity').textContent = `Severity: ${last.severity} (${last.timestamp})`;

      const badge = document.getElementById('dash-card-severity-badge');
      if (badge) {
        badge.innerHTML = `<span class="severity-pill ${last.severity}">${last.severity} FAULT</span>`;
      }
    } else {
      document.getElementById('dash-last-fault').textContent = 'All Clear';
      document.getElementById('dash-last-severity').textContent = 'No diagnostic alerts recorded';
    }

    renderDashboardActivity(last);
  } catch (err) {
    console.error('Error loading dashboard stats:', err);
  }
}

function renderDashboardActivity(lastDiag) {
  const container = document.getElementById('dash-activity-container');
  if (!container) return;

  if (!lastDiag) {
    container.innerHTML = `
      <div style="text-align: center; padding: 2.5rem; color: var(--text-tertiary);">
        <p>No recent diagnostic events recorded.</p>
        <button class="btn-apple-secondary" style="margin-top: 0.8rem;" onclick="switchTab('tab-diagnose')">
          Run First AI Diagnosis Scan &rsaquo;
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 18px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span class="severity-pill ${lastDiag.severity}">${lastDiag.severity}</span>
        <span style="font-size: 0.75rem; color: var(--text-tertiary); font-family: var(--font-mono);">${lastDiag.timestamp}</span>
      </div>
      <h4 style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">${lastDiag.predicted_fault}</h4>
      <p style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 10px;">
        <strong>Symptoms:</strong> ${lastDiag.symptoms || 'None recorded'}
      </p>
      <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-subtle); padding-top: 10px;">
        <span style="font-size: 0.8rem; font-weight: 600; color: var(--apple-blue);">Confidence: ${lastDiag.confidence}%</span>
        <button class="apple-link-btn" onclick="switchTab('tab-history')">
          Audit History &rsaquo;
        </button>
      </div>
    </div>
  `;
}

// ============================================================================
// DIAGNOSIS TAB & SYMPTOM SELECTION
// ============================================================================

function setupSymptomCategories() {
  const container = document.getElementById('symptoms-container');
  if (!container) return;

  container.innerHTML = Object.entries(SYMPTOM_CATEGORIES).map(([category, symptoms]) => `
    <div class="symptom-category-box">
      <div class="category-title-label">
        <span>${category}</span>
        <span style="font-size: 0.72rem; color: var(--text-tertiary);">${symptoms.length} symptoms</span>
      </div>
      <div class="symptoms-pill-wrapper">
        ${symptoms.map(symptom => `
          <div class="apple-symptom-chip" data-symptom="${symptom}">
            ${symptom}
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');

  // Chip click listeners
  container.querySelectorAll('.apple-symptom-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const symptom = chip.getAttribute('data-symptom');
      if (state.selectedSymptoms.has(symptom)) {
        state.selectedSymptoms.delete(symptom);
        chip.classList.remove('selected');
      } else {
        state.selectedSymptoms.add(symptom);
        chip.classList.add('selected');
      }
    });
  });

  // Clear Symptoms Button
  document.getElementById('clear-symptoms-btn')?.addEventListener('click', () => {
    state.selectedSymptoms.clear();
    container.querySelectorAll('.apple-symptom-chip').forEach(c => c.classList.remove('selected'));
    showToast('Symptoms selection cleared', 'info');
  });

  // Mode Switcher Buttons
  const aiBtn = document.getElementById('mode-btn-ai');
  const ruleBtn = document.getElementById('mode-btn-rule');

  aiBtn?.addEventListener('click', () => {
    state.diagnosisMode = 'ai';
    aiBtn.classList.add('active');
    ruleBtn?.classList.remove('active');
  });

  ruleBtn?.addEventListener('click', () => {
    state.diagnosisMode = 'rule';
    ruleBtn.classList.add('active');
    aiBtn?.classList.remove('active');
  });

  // Run Diagnosis Button
  document.getElementById('run-diagnosis-btn')?.addEventListener('click', executeDiagnosis);

  // Import Live OBD to Diagnosis
  document.getElementById('import-live-obd-btn')?.addEventListener('click', async () => {
    await importObdToDiagnosis();
  });
  document.getElementById('auto-fill-obd-btn')?.addEventListener('click', async () => {
    await importObdToDiagnosis();
  });
}

function setupRangeValueDisplays() {
  const tempSlider = document.getElementById('input-engine-temp');
  const tempDisp = document.getElementById('val-disp-temp');
  tempSlider?.addEventListener('input', (e) => {
    tempDisp.textContent = `${e.target.value}°C`;
  });

  const voltSlider = document.getElementById('input-battery-voltage');
  const voltDisp = document.getElementById('val-disp-voltage');
  voltSlider?.addEventListener('input', (e) => {
    voltDisp.textContent = `${e.target.value}V`;
  });

  const rpmInput = document.getElementById('input-rpm');
  const rpmDisp = document.getElementById('val-disp-rpm');
  rpmInput?.addEventListener('input', (e) => {
    rpmDisp.textContent = `${e.target.value} RPM`;
  });
}

async function importObdToDiagnosis() {
  try {
    const res = await fetch('/api/obd/live');
    const data = await res.json();
    const tel = data.telemetry;

    document.getElementById('input-engine-temp').value = tel['Engine Temperature'];
    document.getElementById('val-disp-temp').textContent = `${tel['Engine Temperature']}°C`;

    document.getElementById('input-battery-voltage').value = tel['Battery Voltage'];
    document.getElementById('val-disp-voltage').textContent = `${tel['Battery Voltage']}V`;

    document.getElementById('input-rpm').value = tel['RPM'];
    document.getElementById('val-disp-rpm').textContent = `${tel['RPM']} RPM`;

    if (tel['DTC'] && tel['DTC'] !== 'None') {
      document.getElementById('input-dtc').value = tel['DTC'];
    }

    if (state.activeVehicle) {
      document.getElementById('input-diag-mileage').value = state.activeVehicle.current_mileage;
    }

    showToast('Live OBD parameters imported into diagnostic sliders!', 'success');
  } catch (err) {
    showToast('Failed to import live OBD data', 'error');
  }
}

// Voice Recognition & Natural Language Extraction
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const micBtn = document.getElementById('voice-mic-btn');
  const textInput = document.getElementById('voice-sim-input');

  if (SpeechRecognition) {
    state.speechRecognition = new SpeechRecognition();
    state.speechRecognition.continuous = false;
    state.speechRecognition.interimResults = false;
    state.speechRecognition.lang = 'en-US';

    state.speechRecognition.onstart = () => {
      state.isRecording = true;
      micBtn.classList.add('recording');
      showToast('Listening... Speak your car symptoms now', 'info');
    };

    state.speechRecognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      textInput.value = transcript;
      extractAndSelectSymptoms(transcript);
    };

    state.speechRecognition.onerror = (e) => {
      console.warn('Speech recognition error:', e.error);
      micBtn.classList.remove('recording');
      state.isRecording = false;
    };

    state.speechRecognition.onend = () => {
      micBtn.classList.remove('recording');
      state.isRecording = false;
    };

    micBtn?.addEventListener('click', () => {
      if (state.isRecording) {
        state.speechRecognition.stop();
      } else {
        state.speechRecognition.start();
      }
    });
  } else {
    micBtn?.addEventListener('click', () => {
      const text = textInput.value.trim();
      if (text) {
        extractAndSelectSymptoms(text);
      } else {
        showToast('Type symptom description and press Enter', 'info');
      }
    });
  }

  textInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      extractAndSelectSymptoms(textInput.value.trim());
    }
  });
}

async function extractAndSelectSymptoms(text) {
  if (!text) return;
  try {
    const res = await fetch('/api/voice/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    const found = data.symptoms || [];

    if (found.length === 0) {
      showToast('No specific symptom keywords detected in sentence', 'info');
      return;
    }

    found.forEach(sym => {
      state.selectedSymptoms.add(sym);
      const chip = document.querySelector(`.apple-symptom-chip[data-symptom="${sym}"]`);
      if (chip) chip.classList.add('selected');
    });

    showToast(`Detected & applied ${found.length} symptom(s): ${found.join(', ')}`, 'success');
  } catch (err) {
    showToast('Error parsing symptoms from text', 'error');
  }
}

// ============================================================================
// EXECUTE DIAGNOSIS & RENDER DEEP DATASET EVIDENCE
// (This is the primary requirement: "give the result right but there is no details see")
// ============================================================================

async function executeDiagnosis() {
  if (!state.activeVehicle) {
    showToast('Please register or select a vehicle first', 'error');
    switchTab('tab-vehicles');
    return;
  }

  const symptomsList = Array.from(state.selectedSymptoms);
  if (state.diagnosisMode === 'rule' && symptomsList.length === 0) {
    showToast('Rule-based engine requires at least one symptom selected', 'error');
    return;
  }

  const payload = {
    vehicle_reg: state.activeVehicle.registration_number,
    mode: state.diagnosisMode,
    symptoms: symptomsList,
    engine_temp: parseFloat(document.getElementById('input-engine-temp').value),
    rpm: parseInt(document.getElementById('input-rpm').value, 10),
    battery_voltage: parseFloat(document.getElementById('input-battery-voltage').value),
    mileage: parseInt(document.getElementById('input-diag-mileage').value, 10),
    dtc_code: document.getElementById('input-dtc').value.trim() || 'None'
  };

  const btn = document.getElementById('run-diagnosis-btn');
  const originalText = btn.innerHTML;
  btn.innerHTML = '⚙️ Cross-Referencing 1,500+ Dataset Records...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/diagnose', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      renderDiagnosisResult(data);
      showToast('Diagnostic scan complete with verified dataset evidence!', 'success');
      loadDashboardStats();
      loadHealthScore();
    } else {
      showToast(data.detail || 'Diagnosis failed', 'error');
    }
  } catch (err) {
    showToast('Network error while running diagnosis', 'error');
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

function renderDiagnosisResult(resultData) {
  const wrapper = document.getElementById('diagnosis-result-wrapper');
  if (!wrapper) return;

  const diag = resultData.diagnosis;
  const car = resultData.vehicle;
  const reportUrl = resultData.report_url;
  const evidence = diag.dataset_evidence || {};
  const benchmarks = evidence.sensor_benchmarks || {};
  const closestRecords = evidence.closest_records || [];
  const components = evidence.affected_components || [];
  const steps = evidence.workshop_procedure || [];
  const dtcs = evidence.dtc_matches || [];

  wrapper.innerHTML = `
    <div class="diagnosis-sheet">
      <!-- Sheet Hero Header -->
      <div class="sheet-hero-header">
        <div>
          <div class="sheet-car-meta">
            ${resultData.timestamp} &bull; ${car.manufacturer} ${car.model} (${car.registration_number})
          </div>
          <h3 class="sheet-fault-name">${diag.fault}</h3>
          <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 4px;">
            ${evidence.category || 'Automotive Powertrain'} &bull; ${evidence.summary || ''}
          </div>
        </div>
        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
          <span class="severity-pill ${diag.severity}">${diag.severity} FAULT</span>
          <span style="font-size: 0.72rem; color: var(--apple-blue); font-weight: 600;">AI Machine Learning</span>
        </div>
      </div>

      <!-- Confidence Bar -->
      <div class="confidence-meter-box">
        <div class="meter-labels">
          <span>AI Prediction Confidence</span>
          <strong>${diag.confidence}% Confidence</strong>
        </div>
        <div class="meter-track">
          <div class="meter-fill" style="width: ${diag.confidence}%;"></div>
        </div>
      </div>

      <!-- DATASET EVIDENCE & VERIFICATION PROOF -->
      <div class="dataset-proof-card">
        <div class="proof-header">
          <span>📊</span> Verified Dataset Evidence (1,500+ Samples Cross-Matched)
        </div>
        <div class="proof-metrics-row">
          <div class="proof-metric-cell">
            <div class="num">${evidence.dataset_count || 0}</div>
            <div class="desc">Matching Dataset Records</div>
          </div>
          <div class="proof-metric-cell">
            <div class="num">${evidence.dataset_percentage || 0}%</div>
            <div class="desc">Share of Total Dataset</div>
          </div>
          <div class="proof-metric-cell">
            <div class="num">${closestRecords.length > 0 ? closestRecords[0].similarity_score : 95.0}%</div>
            <div class="desc">Feature Alignment Score</div>
          </div>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4;">
          The Random Forest model verified this vehicle's symptom and telemetry fingerprint against <strong>${evidence.total_dataset_records || 1500} verified vehicle records</strong> in <code>data/dataset.csv</code>. The closest matching clusters confirm this fault signature.
        </p>
      </div>

      <!-- SENSOR BENCHMARK VS DATASET NORMS -->
      ${benchmarks.engine_temperature ? `
        <div class="benchmark-table-box">
          <div class="benchmark-table-title">Sensor Benchmark vs Normal & Fault Baselines</div>
          <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); overflow: hidden;">
            <div class="benchmark-row header">
              <div>Parameter</div>
              <div>Your Reading</div>
              <div>Normal Avg</div>
              <div>Fault Status</div>
            </div>
            <div class="benchmark-row">
              <div><strong>Coolant Temp</strong></div>
              <div>${benchmarks.engine_temperature.user_value}°C</div>
              <div>${benchmarks.engine_temperature.normal_avg}°C</div>
              <div>
                <span class="status-badge ${benchmarks.engine_temperature.status.includes('Critical') ? 'alert' : benchmarks.engine_temperature.status.includes('Elevated') ? 'warning' : 'safe'}">
                  ${benchmarks.engine_temperature.status}
                </span>
              </div>
            </div>
            <div class="benchmark-row">
              <div><strong>Battery Voltage</strong></div>
              <div>${benchmarks.battery_voltage.user_value}V</div>
              <div>${benchmarks.battery_voltage.normal_avg}V</div>
              <div>
                <span class="status-badge ${benchmarks.battery_voltage.status.includes('Critical') ? 'alert' : benchmarks.battery_voltage.status.includes('Drop') || benchmarks.battery_voltage.status.includes('Weak') ? 'warning' : 'safe'}">
                  ${benchmarks.battery_voltage.status}
                </span>
              </div>
            </div>
            <div class="benchmark-row">
              <div><strong>Engine RPM</strong></div>
              <div>${benchmarks.rpm.user_value} RPM</div>
              <div>${benchmarks.rpm.normal_avg} RPM</div>
              <div>
                <span class="status-badge ${benchmarks.rpm.status.includes('Surge') || benchmarks.rpm.status.includes('Stalling') ? 'warning' : 'safe'}">
                  ${benchmarks.rpm.status}
                </span>
              </div>
            </div>
          </div>
        </div>
      ` : ''}

      <!-- TOP CLOSEST MATCHED DATASET ROWS -->
      ${closestRecords.length > 0 ? `
        <div class="closest-samples-box">
          <div class="closest-samples-title">
            <span>Closest Real Samples in dataset.csv</span>
            <span style="font-size: 0.72rem; color: var(--apple-blue); font-weight: 600;">Top ${closestRecords.length} Matches</span>
          </div>
          ${closestRecords.map(rec => `
            <div class="closest-sample-card">
              <div>
                <span style="font-weight: 700; color: var(--text-primary);">CSV Line #${rec.dataset_row_index}</span>
                <span style="color: var(--text-tertiary); margin: 0 4px;">&bull;</span>
                <span style="color: var(--text-secondary);">${rec.fault}</span>
                <div style="font-size: 0.72rem; color: var(--text-tertiary); margin-top: 2px;">
                  Temp: ${rec.engine_temperature}°C | Volt: ${rec.battery_voltage}V | RPM: ${rec.rpm} | ${rec.mileage.toLocaleString()} km
                </div>
              </div>
              <div style="text-align: right;">
                <span style="font-weight: 700; color: var(--apple-green); font-size: 0.9rem;">${rec.similarity_score}%</span>
                <div style="font-size: 0.68rem; color: var(--text-tertiary);">Similarity Match</div>
              </div>
            </div>
          `).join('')}
        </div>
      ` : ''}

      <!-- AFFECTED MECHANICAL COMPONENTS -->
      ${components.length > 0 ? `
        <div style="margin-bottom: 22px;">
          <h4 style="font-size: 0.82rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 10px;">
            Affected Powertrain Components & Inspection:
          </h4>
          <div class="components-sheet-grid">
            ${components.map(c => `
              <div class="component-card-mini">
                <div class="comp-name">${c.name}</div>
                <div class="comp-role">${c.role}</div>
                <div class="comp-wear">⚠️ ${c.wear}</div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <!-- WORKSHOP RESOLUTION STEPS -->
      ${steps.length > 0 ? `
        <div class="action-plan-box">
          <div class="action-plan-title">
            <span>🛠️</span> Step-by-Step Workshop Resolution Plan
          </div>
          <ol class="steps-list">
            ${steps.map(step => `<li>${step}</li>`).join('')}
          </ol>
        </div>
      ` : ''}

      <!-- DRIVING SAFETY ADVISORY -->
      ${evidence.danger_level ? `
        <div style="background: var(--apple-red-tint); border: 1px solid rgba(255, 59, 48, 0.2); border-radius: var(--radius-md); padding: 14px 16px; margin-bottom: 22px;">
          <strong style="color: var(--apple-red); font-size: 0.82rem; text-transform: uppercase; display: block; margin-bottom: 4px;">
            ⚠️ Driving Hazard & Risk Assessment
          </strong>
          <p style="font-size: 0.82rem; color: var(--text-primary); line-height: 1.4;">
            ${evidence.danger_level}
          </p>
        </div>
      ` : ''}

      <!-- ASSOCIATED DTC CODES -->
      ${dtcs.length > 0 ? `
        <div style="margin-bottom: 24px;">
          <h4 style="font-size: 0.82rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 8px;">
            Diagnostic Trouble Codes Linked:
          </h4>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            ${dtcs.map(d => `
              <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-medium); border-radius: var(--radius-md); padding: 8px 12px; font-size: 0.8rem;">
                <strong style="color: var(--apple-blue);">${d.code}</strong> &mdash; ${d.description}
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <!-- ACTION BUTTONS -->
      <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-top: 10px;">
        ${reportUrl ? `
          <a href="${reportUrl}" class="btn-apple-primary" target="_blank" style="flex: 1; text-align: center;">
            📄 Download Official PDF Report
          </a>
        ` : ''}
        <button class="btn-apple-secondary" onclick="openFaultQuickLook('${diag.fault}')">
          📖 View Full Fault Profile
        </button>
        <button class="btn-apple-secondary" onclick="window.scrollTo({top: 0, behavior: 'smooth'})">
          🔄 Run Another Scan
        </button>
      </div>
    </div>
  `;

  wrapper.scrollIntoView({ behavior: 'smooth' });
}

// ============================================================================
// DATASET & FAULTS EXPLORER (Catalog, Filtering, and Raw Inspector)
// ============================================================================

function setupDatasetExplorer() {
  // Category Filter Buttons
  const filterButtons = document.querySelectorAll('.dataset-filter-btn');
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cat = btn.getAttribute('data-filter');
      state.currentDatasetFilter = cat;
      filterFaultsCatalog(cat);
    });
  });

  // Raw dataset dropdown filter
  const select = document.getElementById('dataset-filter-select');
  select?.addEventListener('change', async (e) => {
    state.datasetFilterFault = e.target.value;
    state.datasetOffset = 0;
    await loadRawDatasetRecords(state.datasetFilterFault, 0);
  });

  // Pagination buttons
  document.getElementById('dataset-prev-btn')?.addEventListener('click', async () => {
    if (state.datasetOffset >= state.datasetLimit) {
      state.datasetOffset -= state.datasetLimit;
      await loadRawDatasetRecords(state.datasetFilterFault, state.datasetOffset);
    }
  });

  document.getElementById('dataset-next-btn')?.addEventListener('click', async () => {
    if (state.datasetOffset + state.datasetLimit < state.datasetTotal) {
      state.datasetOffset += state.datasetLimit;
      await loadRawDatasetRecords(state.datasetFilterFault, state.datasetOffset);
    }
  });
}

async function loadFaultsCatalog() {
  const container = document.getElementById('faults-catalog-container');
  if (!container) return;

  try {
    const res = await fetch('/api/dataset/faults');
    const data = await res.json();
    state.datasetFaults = data.faults || [];
    filterFaultsCatalog(state.currentDatasetFilter);
  } catch (err) {
    console.error('Error loading faults catalog:', err);
  }
}

function filterFaultsCatalog(filterCategory) {
  const container = document.getElementById('faults-catalog-container');
  if (!container) return;

  let filtered = state.datasetFaults;
  if (filterCategory !== 'All') {
    filtered = state.datasetFaults.filter(f => {
      const cat = f.category || '';
      return cat.toLowerCase().includes(filterCategory.toLowerCase());
    });
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-tertiary);">
        No faults in category "${filterCategory}".
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(f => `
    <div class="fault-catalog-card" onclick="openFaultQuickLook('${f.fault}')">
      <div>
        <div class="fault-card-top">
          <span class="fault-sample-tag">${f.dataset_count} Records (${f.dataset_percentage}%)</span>
          <span class="severity-pill ${f.severity}">${f.severity}</span>
        </div>
        <h4 class="fault-card-title">${f.fault}</h4>
        <p class="fault-card-summary">${f.summary}</p>
        
        <div class="fault-sensors-pill-row">
          <span class="sensor-micro-pill">Avg Temp: ${f.sensor_means.engine_temperature}°C</span>
          <span class="sensor-micro-pill">Avg Volt: ${f.sensor_means.battery_voltage}V</span>
          <span class="sensor-micro-pill">Avg RPM: ${f.sensor_means.rpm}</span>
        </div>

        <div style="font-size: 0.72rem; color: var(--text-secondary); margin-bottom: 14px;">
          <strong>Symptoms:</strong> ${(f.primary_symptoms || []).slice(0, 3).join(', ') || 'Nominal'}
        </div>
      </div>

      <div class="fault-card-buttons" onclick="event.stopPropagation()">
        <button class="btn-apple-secondary" onclick="openFaultQuickLook('${f.fault}')">
          Quick Look
        </button>
        <button class="btn-apple-primary" onclick="simulateFaultInModel('${f.fault}')">
          Simulate in AI &rsaquo;
        </button>
      </div>
    </div>
  `).join('');
}

async function loadRawDatasetRecords(fault, offset) {
  const tbody = document.getElementById('dataset-raw-table-body');
  const pageInfo = document.getElementById('dataset-page-info');
  if (!tbody) return;

  try {
    const url = `/api/dataset/records?fault=${encodeURIComponent(fault)}&limit=${state.datasetLimit}&offset=${offset}`;
    const res = await fetch(url);
    const data = await res.json();

    state.datasetTotal = data.total;
    const records = data.records || [];

    if (pageInfo) {
      const end = Math.min(offset + records.length, data.total);
      pageInfo.textContent = `Showing rows ${offset + 1}–${end} of ${data.total} records`;
    }

    if (records.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; padding: 2rem; color: var(--text-tertiary);">
            No records found.
          </td>
        </tr>
      `;
      return;
    }

    const symptomCols = [
      'engine_vibration', 'engine_overheating', 'poor_mileage',
      'starting_problem', 'check_engine_light', 'brake_noise',
      'battery_problem', 'low_power', 'abnormal_sound'
    ];

    tbody.innerHTML = records.map(r => {
      const active = symptomCols
        .filter(c => r[c] === 1)
        .map(c => c.replace('_', ' ').titleCase())
        .join(', ') || 'Nominal';

      return `
        <tr>
          <td><strong style="color: var(--apple-blue);">#${r.row_number}</strong></td>
          <td><strong>${r.fault}</strong></td>
          <td style="max-width: 220px; font-size: 0.74rem; color: var(--text-secondary);">${active}</td>
          <td>${r.engine_temperature.toFixed(1)}°C</td>
          <td>${r.battery_voltage.toFixed(2)}V</td>
          <td>${r.rpm}</td>
          <td>${r.mileage.toLocaleString()} km</td>
          <td>${r.vehicle_age} yrs</td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading dataset records:', err);
  }
}

// Auto-fill diagnosis with representative fault parameters and run scan
function simulateFaultInModel(faultName) {
  const fault = state.datasetFaults.find(f => f.fault === faultName);
  if (!fault) return;

  switchTab('tab-diagnose');

  // Clear previous
  state.selectedSymptoms.clear();
  document.querySelectorAll('.apple-symptom-chip').forEach(c => c.classList.remove('selected'));

  // Select primary symptoms
  (fault.primary_symptoms || []).forEach(sym => {
    state.selectedSymptoms.add(sym);
    const chip = document.querySelector(`.apple-symptom-chip[data-symptom="${sym}"]`);
    if (chip) chip.classList.add('selected');
  });

  // Set sensor telemetry
  const means = fault.sensor_means;
  document.getElementById('input-engine-temp').value = means.engine_temperature;
  document.getElementById('val-disp-temp').textContent = `${means.engine_temperature}°C`;

  document.getElementById('input-battery-voltage').value = means.battery_voltage;
  document.getElementById('val-disp-voltage').textContent = `${means.battery_voltage}V`;

  document.getElementById('input-rpm').value = means.rpm;
  document.getElementById('val-disp-rpm').textContent = `${means.rpm} RPM`;

  if (fault.dtc_codes && fault.dtc_codes.length > 0) {
    document.getElementById('input-dtc').value = fault.dtc_codes[0];
  }

  showToast(`Loaded ${faultName} template into AI Diagnosis. Tap Run AI Diagnosis Scan!`, 'info');
}

// ============================================================================
// APPLE QUICK LOOK MODAL SHEET
// ============================================================================

function setupModalHandlers() {
  const modal = document.getElementById('apple-quick-look-modal');
  const closeBtn = document.getElementById('modal-close-btn');

  closeBtn?.addEventListener('click', () => {
    modal.classList.remove('open');
  });

  modal?.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.remove('open');
    }
  });
}

async function openFaultQuickLook(faultName) {
  const modal = document.getElementById('apple-quick-look-modal');
  const content = document.getElementById('quick-look-modal-content');
  if (!modal || !content) return;

  modal.classList.add('open');
  content.innerHTML = `
    <div style="text-align: center; padding: 2rem; color: var(--text-tertiary);">
      Loading complete technical profile for ${faultName}...
    </div>
  `;

  try {
    const res = await fetch(`/api/dataset/fault/${encodeURIComponent(faultName)}`);
    const data = await res.json();
    const f = data.fault_detail;

    content.innerHTML = `
      <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span class="severity-pill ${f.severity}">${f.severity} SEVERITY</span>
          <span style="font-size: 0.75rem; color: var(--apple-blue); font-weight: 600;">
            ${f.dataset_count} Samples in Dataset (${f.dataset_percentage}%)
          </span>
        </div>
        <h2 style="font-size: 1.8rem; font-weight: 800; color: var(--text-primary); margin-bottom: 4px;">
          ${f.fault}
        </h2>
        <div style="font-size: 0.85rem; color: var(--text-secondary);">
          ${f.category} &bull; Estimated Repair: ${f.estimated_repair_time}
        </div>
      </div>

      <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 16px; margin-bottom: 20px;">
        <h4 style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 6px;">
          Technical System Overview
        </h4>
        <p style="font-size: 0.88rem; color: var(--text-primary); line-height: 1.45;">
          ${f.summary}
        </p>
      </div>

      <!-- Sensor Averages vs Normal -->
      <div style="margin-bottom: 20px;">
        <h4 style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 10px;">
          Telemetry Fingerprint in dataset.csv:
        </h4>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
          <div style="background: var(--bg-card-subtle); padding: 12px; border-radius: var(--radius-md); text-align: center;">
            <div style="font-size: 0.7rem; color: var(--text-tertiary); text-transform: uppercase;">Avg Temperature</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin: 2px 0;">${f.sensor_means.engine_temperature}°C</div>
            <div style="font-size: 0.68rem; color: var(--apple-blue);">Normal: ${f.normal_baseline.engine_temperature}°C</div>
          </div>
          <div style="background: var(--bg-card-subtle); padding: 12px; border-radius: var(--radius-md); text-align: center;">
            <div style="font-size: 0.7rem; color: var(--text-tertiary); text-transform: uppercase;">Avg Battery Volt</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin: 2px 0;">${f.sensor_means.battery_voltage}V</div>
            <div style="font-size: 0.68rem; color: var(--apple-blue);">Normal: ${f.normal_baseline.battery_voltage}V</div>
          </div>
          <div style="background: var(--bg-card-subtle); padding: 12px; border-radius: var(--radius-md); text-align: center;">
            <div style="font-size: 0.7rem; color: var(--text-tertiary); text-transform: uppercase;">Avg Engine RPM</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin: 2px 0;">${f.sensor_means.rpm}</div>
            <div style="font-size: 0.68rem; color: var(--apple-blue);">Normal: ${f.normal_baseline.rpm}</div>
          </div>
        </div>
      </div>

      <!-- Affected Components -->
      <div style="margin-bottom: 20px;">
        <h4 style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 10px;">
          Mechanical Components Affected:
        </h4>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
          ${(f.affected_components || []).map(c => `
            <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 10px;">
              <strong style="color: var(--text-primary); font-size: 0.85rem;">${c.name}</strong>
              <div style="font-size: 0.72rem; color: var(--text-tertiary);">${c.role}</div>
              <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 4px;">⚠️ ${c.wear}</div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Workshop Procedure -->
      <div style="margin-bottom: 22px;">
        <h4 style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 10px;">
          Workshop Diagnostic Steps:
        </h4>
        <ol style="padding-left: 20px; font-size: 0.84rem; color: var(--text-secondary); line-height: 1.5;">
          ${(f.workshop_procedure || []).map(step => `<li style="margin-bottom: 6px;">${step}</li>`).join('')}
        </ol>
      </div>

      <div style="display: flex; gap: 10px;">
        <button class="btn-apple-primary" style="flex: 1;" onclick="document.getElementById('apple-quick-look-modal').classList.remove('open'); simulateFaultInModel('${f.fault}');">
          🔬 Simulate in AI Diagnosis Scan &rsaquo;
        </button>
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<p style="color: var(--apple-red);">Failed to load fault details.</p>`;
  }
}

// Helper string method
String.prototype.titleCase = function() {
  return this.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
};

// ============================================================================
// OBD-II MONITOR TAB & GAUGES
// ============================================================================

function setupOBDStreaming() {
  const modeSelect = document.getElementById('obd-mode-select');
  const refreshBtn = document.getElementById('obd-refresh-btn');
  const autoToggle = document.getElementById('obd-auto-stream-toggle');
  const sendDiagBtn = document.getElementById('obd-send-diag-btn');

  refreshBtn?.addEventListener('click', () => fetchLiveObd());
  modeSelect?.addEventListener('change', () => fetchLiveObd());

  autoToggle?.addEventListener('change', (e) => {
    state.isAutoStreaming = e.target.checked;
    if (state.isAutoStreaming) {
      startObdStreaming();
      showToast('Live OBD streaming resumed', 'info');
    } else {
      stopObdStreaming();
      showToast('Live OBD streaming paused', 'info');
    }
  });

  sendDiagBtn?.addEventListener('click', async () => {
    await importObdToDiagnosis();
    switchTab('tab-diagnose');
  });

  startObdStreaming();
}

function startObdStreaming() {
  if (state.streamInterval) clearInterval(state.streamInterval);
  state.streamInterval = setInterval(() => {
    const obdSection = document.getElementById('tab-obd');
    if (obdSection?.classList.contains('active')) {
      fetchLiveObd();
    }
  }, 1500);
}

function stopObdStreaming() {
  if (state.streamInterval) {
    clearInterval(state.streamInterval);
    state.streamInterval = null;
  }
}

async function fetchLiveObd() {
  const mode = document.getElementById('obd-mode-select')?.value || 'Normal';
  try {
    const res = await fetch(`/api/obd/live?fault_mode=${encodeURIComponent(mode)}`);
    const data = await res.json();
    state.liveObd = data.telemetry;

    updateGaugeDisplays(data.telemetry);
    updateDtcTerminal(data.telemetry, data.dtc_info, data.timestamp);
  } catch (err) {
    console.error('Error fetching live OBD:', err);
  }
}

function updateGaugeDisplays(tel) {
  const maxDash = 188.49;

  // 1. RPM (0 - 6000)
  const rpm = tel['RPM'] || 0;
  const rpmEl = document.getElementById('gauge-rpm-val');
  const rpmProg = document.getElementById('gauge-rpm-progress');
  if (rpmEl) rpmEl.textContent = rpm;
  if (rpmProg) {
    const pct = Math.min(1, rpm / 6000);
    rpmProg.style.strokeDashoffset = maxDash - (maxDash * pct);
    rpmProg.style.stroke = rpm > 4500 ? 'var(--apple-red)' : rpm > 3000 ? 'var(--apple-orange)' : 'var(--apple-blue)';
  }

  // 2. Engine Temp (40 - 130 C)
  const temp = tel['Engine Temperature'] || 90;
  const tempEl = document.getElementById('gauge-temp-val');
  const tempProg = document.getElementById('gauge-temp-progress');
  if (tempEl) tempEl.textContent = temp;
  if (tempProg) {
    const pct = Math.min(1, Math.max(0, (temp - 40) / 90));
    tempProg.style.strokeDashoffset = maxDash - (maxDash * pct);
    tempProg.style.stroke = temp > 105 ? 'var(--apple-red)' : temp > 95 ? 'var(--apple-orange)' : 'var(--apple-green)';
  }

  // 3. Battery Voltage (9 - 15 V)
  const volt = tel['Battery Voltage'] || 12.6;
  const voltEl = document.getElementById('gauge-volt-val');
  const voltProg = document.getElementById('gauge-volt-progress');
  if (voltEl) voltEl.textContent = volt;
  if (voltProg) {
    const pct = Math.min(1, Math.max(0, (volt - 9) / 6));
    voltProg.style.strokeDashoffset = maxDash - (maxDash * pct);
    voltProg.style.stroke = volt < 11.5 || volt > 14.8 ? 'var(--apple-red)' : volt < 12.2 ? 'var(--apple-orange)' : 'var(--apple-green)';
  }

  // 4. Velocity
  const speed = tel['Speed'] || 0;
  const speedEl = document.getElementById('gauge-speed-val');
  const speedProg = document.getElementById('gauge-speed-progress');
  if (speedEl) speedEl.textContent = speed;
  if (speedProg) {
    const pct = Math.min(1, speed / 180);
    speedProg.style.strokeDashoffset = maxDash - (maxDash * pct);
    speedProg.style.stroke = 'var(--apple-blue)';
  }
}

function updateDtcTerminal(tel, dtcInfo, timestamp) {
  const container = document.getElementById('dtc-terminal-content');
  const timeDisp = document.getElementById('obd-timestamp-disp');
  if (timeDisp) timeDisp.textContent = `CAN-Bus Sync: ${timestamp}`;
  if (!container) return;

  const dtc = tel['DTC'];
  if (!dtc || dtc === 'None') {
    container.innerHTML = `
      <div class="dtc-status-clear">
        <span>✅</span>
        <span>NO ACTIVE DIAGNOSTIC TROUBLE CODES DETECTED. ALL SENSORS WITHIN NOMINAL TOLERANCES.</span>
      </div>
    `;
  } else {
    container.innerHTML = `
      <div class="dtc-status-fault">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <strong style="font-size: 1.1rem; color: var(--apple-red);">ACTIVE DTC: ${dtc}</strong>
          <span class="severity-pill ${dtcInfo ? dtcInfo.severity : 'HIGH'}">${dtcInfo ? dtcInfo.severity : 'HIGH'} SEVERITY</span>
        </div>
        <p style="font-size: 0.85rem; margin-bottom: 6px;">
          <strong>Description:</strong> ${dtcInfo ? dtcInfo.description : 'Subsystem anomaly detected'}
        </p>
        <p style="font-size: 0.82rem; margin-bottom: 6px;">
          <strong>Potential Causes:</strong> ${dtcInfo ? dtcInfo.causes : 'Sensor circuit out of range'}
        </p>
        <p style="font-size: 0.82rem; color: var(--text-primary);">
          <strong>Recommendation:</strong> ${dtcInfo ? dtcInfo.recommendation : 'Inspect component with qualified technician'}
        </p>
      </div>
    `;
  }
}

// ============================================================================
// HEALTH SCORE & SERVICE REMINDERS
// ============================================================================

async function loadHealthScore() {
  try {
    const res = await fetch('/api/health-score');
    const data = await res.json();

    const score = data.score || 100;
    const scoreVal = document.getElementById('health-score-val');
    const circle = document.getElementById('radial-health-circle');

    if (scoreVal) scoreVal.textContent = score;
    if (circle) {
      const maxCirc = 502.65;
      const offset = maxCirc - (maxCirc * (score / 100));
      circle.style.strokeDashoffset = offset;
      circle.style.stroke = score > 80 ? 'var(--apple-green)' : score > 50 ? 'var(--apple-orange)' : 'var(--apple-red)';
    }

    const sevBadge = document.getElementById('health-last-severity-badge');
    if (sevBadge) {
      sevBadge.innerHTML = `<span class="severity-pill ${data.last_severity}">${data.last_severity} SEVERITY</span>`;
    }

    renderDeductions(data.deductions || []);
    renderReminders(data.reminders || []);
  } catch (err) {
    console.error('Error loading health score:', err);
  }
}

function renderDeductions(deductions) {
  const container = document.getElementById('deductions-list-container');
  if (!container) return;

  if (deductions.length === 0) {
    container.innerHTML = `
      <p style="font-size: 0.85rem; color: var(--apple-green);">
        ✅ All telemetry parameters nominal. Zero health deductions applied.
      </p>
    `;
    return;
  }

  container.innerHTML = deductions.map(d => `
    <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-card-subtle); border-radius: var(--radius-sm); padding: 8px 12px; margin-bottom: 6px; font-size: 0.82rem;">
      <span style="color: var(--text-primary);">${d.reason}</span>
      <strong style="color: var(--apple-red); font-family: var(--font-mono);">&minus;${d.penalty} pts</strong>
    </div>
  `).join('');
}

function renderReminders(reminders) {
  const container = document.getElementById('maintenance-reminders-container');
  if (!container) return;

  if (reminders.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: var(--text-tertiary);">
        All scheduled preventive maintenance up to date.
      </div>
    `;
    return;
  }

  container.innerHTML = reminders.map(r => `
    <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 14px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <strong style="font-size: 0.9rem; color: var(--text-primary); display: block;">${r.service}</strong>
        <span style="font-size: 0.75rem; color: var(--text-tertiary);">${r.interval}</span>
      </div>
      <span class="severity-pill ${r.status === 'Due' ? 'HIGH' : 'MEDIUM'}">
        ${r.status}
      </span>
    </div>
  `).join('');
}

// ============================================================================
// DIAGNOSIS HISTORY & AUDIT LOG
// ============================================================================

async function loadDiagnosisHistory() {
  const tbody = document.getElementById('history-table-body');
  if (!tbody) return;

  try {
    const res = await fetch('/api/history');
    const data = await res.json();
    const history = data.history || [];

    if (history.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; padding: 2.5rem; color: var(--text-tertiary);">
            No historical diagnosis records found in audit log.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = history.map(row => `
      <tr>
        <td style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-secondary);">${row.timestamp}</td>
        <td><strong style="color: var(--apple-blue);">${row.vehicle_reg}</strong></td>
        <td><strong>${row.predicted_fault}</strong></td>
        <td><span class="severity-pill ${row.severity}">${row.severity}</span></td>
        <td style="font-family: var(--font-mono); font-weight: 600;">${row.confidence}%</td>
        <td style="font-size: 0.75rem; color: var(--text-secondary); max-width: 240px;">${row.symptoms || 'None'}</td>
        <td>
          <button class="btn-apple-secondary" style="padding: 3px 8px; font-size: 0.72rem;" onclick="openFaultQuickLook('${row.predicted_fault}')">
            View Details
          </button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Error loading history:', err);
  }

  document.getElementById('refresh-history-btn')?.addEventListener('click', () => {
    loadDiagnosisHistory();
    showToast('Audit history refreshed', 'info');
  });
}

// ============================================================================
// GLOBAL TOAST NOTIFICATIONS
// ============================================================================

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'apple-toast';

  const icon = type === 'success' ? '✅' : type === 'error' ? '⚠️' : 'ℹ️';
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
