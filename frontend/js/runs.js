// Rally Timing - Runs Page Logic + Stopwatch

// --- Stopwatch State ---
let swStartTime = null;
let swElapsedMs = 0;
let swRunning = false;
let swAnimFrame = null;

// --- Tab switching ---
function switchTab(tab) {
    document.getElementById('panel-manual').style.display = tab === 'manual' ? 'block' : 'none';
    document.getElementById('panel-stopwatch').style.display = tab === 'stopwatch' ? 'block' : 'none';
    document.getElementById('tab-manual').className = `btn btn-sm ${tab === 'manual' ? 'btn-primary' : 'btn-secondary'}`;
    document.getElementById('tab-stopwatch').className = `btn btn-sm ${tab === 'stopwatch' ? 'btn-primary' : 'btn-secondary'}`;
    document.getElementById('run-source').value = tab;
}

// --- Stopwatch ---
function toggleStopwatch() {
    if (swRunning) {
        stopStopwatch();
    } else {
        startStopwatch();
    }
}

function startStopwatch() {
    swStartTime = performance.now();
    swRunning = true;
    const btn = document.getElementById('sw-btn');
    btn.textContent = 'DETENER';
    btn.classList.add('running');
    updateStopwatchDisplay();
}

function stopStopwatch() {
    swElapsedMs = Math.round(performance.now() - swStartTime);
    swRunning = false;
    cancelAnimationFrame(swAnimFrame);

    const btn = document.getElementById('sw-btn');
    btn.textContent = 'INICIAR';
    btn.classList.remove('running');

    document.getElementById('sw-display').textContent = formatTime(swElapsedMs);

    // Auto-fill manual fields too
    const parts = msToComponents(swElapsedMs);
    document.getElementById('time-min').value = parts.minutes;
    document.getElementById('time-sec').value = parts.seconds;
    document.getElementById('time-ms').value = parts.millis;
}

function updateStopwatchDisplay() {
    if (!swRunning) return;
    const elapsed = Math.round(performance.now() - swStartTime);
    document.getElementById('sw-display').textContent = formatTime(elapsed);
    swAnimFrame = requestAnimationFrame(updateStopwatchDisplay);
}

// --- Load pilots dropdown ---
async function loadRunFormData() {
    try {
        const pilots = await PilotsAPI.list();
        const select = document.getElementById('run-pilot');
        select.innerHTML = '<option value="">Seleccionar piloto...</option>' +
            pilots.map(p => `<option value="${p.id}">${p.first_name} ${p.last_name}</option>`).join('');

        // Load all cars initially
        const cars = await CarsAPI.list();
        const carSelect = document.getElementById('run-car');
        carSelect.innerHTML = '<option value="">Seleccionar auto...</option>' +
            cars.map(c => `<option value="${c.id}" data-pilot="${c.pilot_id || ''}">${c.brand} ${c.model} (${c.category})</option>`).join('');
    } catch (err) {
        showToast(err.message, 'error');
    }

    // Set today's date
    document.getElementById('run-date').value = todayString();
}

async function loadCarsForPilot() {
    const pilotId = document.getElementById('run-pilot').value;
    try {
        // Load all cars, but if pilot selected, show their cars first
        const allCars = await CarsAPI.list();
        const carSelect = document.getElementById('run-car');

        if (pilotId) {
            const pilotCars = allCars.filter(c => c.pilot_id == pilotId);
            const otherCars = allCars.filter(c => c.pilot_id != pilotId);

            let html = '<option value="">Seleccionar auto...</option>';
            if (pilotCars.length > 0) {
                html += '<optgroup label="Autos del piloto">';
                html += pilotCars.map(c => `<option value="${c.id}">${c.brand} ${c.model} (${c.category})</option>`).join('');
                html += '</optgroup>';
            }
            if (otherCars.length > 0) {
                html += '<optgroup label="Otros autos">';
                html += otherCars.map(c => `<option value="${c.id}">${c.brand} ${c.model} (${c.category})</option>`).join('');
                html += '</optgroup>';
            }
            carSelect.innerHTML = html;

            // Auto-select if pilot has exactly one car
            if (pilotCars.length === 1) {
                carSelect.value = pilotCars[0].id;
            }
        } else {
            carSelect.innerHTML = '<option value="">Seleccionar auto...</option>' +
                allCars.map(c => `<option value="${c.id}">${c.brand} ${c.model} (${c.category})</option>`).join('');
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// --- Save run ---
async function saveRun(e) {
    e.preventDefault();

    const source = document.getElementById('run-source').value;
    let totalTimeMs;

    if (source === 'stopwatch' && swElapsedMs > 0) {
        totalTimeMs = swElapsedMs;
    } else {
        totalTimeMs = timeToMs(
            document.getElementById('time-min').value,
            document.getElementById('time-sec').value,
            document.getElementById('time-ms').value
        );
    }

    if (totalTimeMs <= 0) {
        showToast('El tiempo debe ser mayor a 0', 'error');
        return;
    }

    const condition = document.querySelector('input[name="condition"]:checked');
    if (!condition) {
        showToast('Selecciona la condicion del tramo', 'error');
        return;
    }

    const data = {
        pilot_id: parseInt(document.getElementById('run-pilot').value),
        car_id: parseInt(document.getElementById('run-car').value),
        run_date: document.getElementById('run-date').value,
        total_time_ms: totalTimeMs,
        track_condition: condition.value,
        notes: document.getElementById('run-notes').value,
        source: source,
    };

    try {
        await RunsAPI.create(data);
        showToast(`Pasada registrada: ${formatTime(totalTimeMs)}`);

        // Reset stopwatch
        swElapsedMs = 0;
        document.getElementById('sw-display').textContent = '00:00.000';
        document.getElementById('time-min').value = 0;
        document.getElementById('time-sec').value = 0;
        document.getElementById('time-ms').value = 0;
        document.getElementById('run-notes').value = '';

        loadTodayRuns();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// --- Load today's runs ---
async function loadTodayRuns() {
    try {
        const runs = await RunsAPI.list({ date: todayString() });
        const tbody = document.getElementById('today-runs');

        if (runs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Sin pasadas hoy</td></tr>';
            return;
        }

        tbody.innerHTML = runs.map(r => {
            const hasPenalty = r.penalty_total_ms > 0;
            const penaltyBadge = hasPenalty
                ? `<span class="badge badge-wet">+${formatTime(r.penalty_total_ms)}</span>`
                : '<span style="color:var(--text-muted)">-</span>';
            const finalClass = hasPenalty ? 'time-cell" style="color:var(--warning)' : 'time-cell';

            return `
            <tr>
                <td>${r.pilot_name || '-'}</td>
                <td>${r.car_name || '-'}</td>
                <td class="time-cell">${formatTime(r.total_time_ms)}</td>
                <td>${penaltyBadge}</td>
                <td class="${finalClass}">${formatTime(r.final_time_ms)}</td>
                <td><span class="badge badge-${r.track_condition}">${CONDITION_LABELS[r.track_condition]}</span></td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="openPenaltyModal(${r.id})">Penal.</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteRun(${r.id})">Invalidar</button>
                </td>
            </tr>`;
        }).join('');
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function deleteRun(id) {
    if (!confirm('Invalidar esta pasada?')) return;
    try {
        await RunsAPI.delete(id);
        showToast('Pasada invalidada');
        loadTodayRuns();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// --- Penalties ---
let currentPenaltyRunId = null;

async function openPenaltyModal(runId) {
    currentPenaltyRunId = runId;
    document.getElementById('penalty-modal').classList.add('active');
    document.getElementById('penalty-form').reset();
    await refreshPenaltyModal();
}

function closePenaltyModal() {
    document.getElementById('penalty-modal').classList.remove('active');
    currentPenaltyRunId = null;
}

async function refreshPenaltyModal() {
    try {
        const run = await RunsAPI.get(currentPenaltyRunId);

        document.getElementById('penalty-run-info').innerHTML =
            `<strong>${run.pilot_name}</strong> - ${run.car_name} | ` +
            `Tiempo: <span class="time-cell">${formatTime(run.total_time_ms)}</span>` +
            (run.penalty_total_ms > 0
                ? ` + <span style="color:var(--warning)">${formatTime(run.penalty_total_ms)}</span> = <strong>${formatTime(run.final_time_ms)}</strong>`
                : '');

        const listEl = document.getElementById('penalty-list');
        if (run.penalties.length === 0) {
            listEl.innerHTML = '<p style="color:var(--text-muted);font-size:0.85rem;">Sin penalizaciones</p>';
        } else {
            listEl.innerHTML = run.penalties.map(p => `
                <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem;background:var(--bg-input);border-radius:var(--radius);margin-bottom:0.5rem;">
                    <div>
                        <span class="badge badge-wet">+${formatTime(p.time_ms)}</span>
                        <span style="margin-left:0.5rem;font-size:0.85rem;">${p.reason}</span>
                    </div>
                    <button class="btn btn-danger btn-sm" onclick="removePenalty(${p.id})">Quitar</button>
                </div>
            `).join('');
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function savePenalty(e) {
    e.preventDefault();
    const timeMs = timeToMs(
        document.getElementById('pen-min').value,
        document.getElementById('pen-sec').value,
        document.getElementById('pen-ms').value
    );
    const reason = document.getElementById('pen-reason').value.trim();

    if (timeMs <= 0) {
        showToast('El tiempo de penalizacion debe ser mayor a 0', 'error');
        return;
    }

    try {
        await RunsAPI.addPenalty(currentPenaltyRunId, { time_ms: timeMs, reason });
        showToast(`Penalizacion agregada: +${formatTime(timeMs)}`);
        document.getElementById('penalty-form').reset();
        await refreshPenaltyModal();
        loadTodayRuns();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function removePenalty(penaltyId) {
    if (!confirm('Quitar esta penalizacion?')) return;
    try {
        await RunsAPI.removePenalty(currentPenaltyRunId, penaltyId);
        showToast('Penalizacion eliminada');
        await refreshPenaltyModal();
        loadTodayRuns();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadRunFormData();
    loadTodayRuns();
});
