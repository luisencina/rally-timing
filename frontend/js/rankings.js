// Rally Timing - Rankings Page Logic

let rankingsChart = null;
let historyChart = null;

async function loadRankings() {
    const category = document.getElementById('filter-category').value;
    const condition = document.getElementById('filter-condition').value;

    try {
        const rankings = await RankingsAPI.bestTimes({
            category: category || undefined,
            condition: condition || undefined,
        });

        const tbody = document.getElementById('rankings-table');
        if (rankings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No hay datos para mostrar</td></tr>';
            updateRankingsChart([]);
            return;
        }

        tbody.innerHTML = rankings.map(r => `
            <tr>
                <td class="position-cell">${r.position}</td>
                <td><strong>${r.pilot_name}</strong>${r.nickname ? ` (${r.nickname})` : ''}</td>
                <td>${r.car_name}</td>
                <td class="time-cell">${formatTime(r.best_time_ms)}</td>
                <td><span class="badge badge-category">${r.car_category}</span></td>
                <td><span class="badge badge-${r.track_condition}">${CONDITION_LABELS[r.track_condition]}</span></td>
                <td>${r.run_date}</td>
            </tr>
        `).join('');

        updateRankingsChart(rankings);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function updateRankingsChart(rankings) {
    const ctx = document.getElementById('rankings-chart');
    if (!ctx) return;

    if (rankingsChart) {
        rankingsChart.destroy();
    }

    if (rankings.length === 0) return;

    const labels = rankings.map(r => r.nickname || r.pilot_name.split(' ')[0]);
    const data = rankings.map(r => r.best_time_ms / 1000); // Show in seconds

    rankingsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Mejor Tiempo (segundos)',
                data: data,
                backgroundColor: '#e6394680',
                borderColor: '#e63946',
                borderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => formatTime(Math.round(ctx.raw * 1000)),
                    },
                },
            },
            scales: {
                y: {
                    title: { display: true, text: 'Tiempo (seg)', color: '#8b8fa3' },
                    grid: { color: '#2e3245' },
                    ticks: { color: '#8b8fa3' },
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#8b8fa3' },
                },
            },
        },
    });
}

async function loadRecords() {
    try {
        const records = await RankingsAPI.records();
        const section = document.getElementById('records-section');

        if (!records.overall) {
            section.innerHTML = '<p class="empty-state">No hay records aun</p>';
            return;
        }

        let html = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${formatTime(records.overall.best_time_ms)}</div>
                    <div class="stat-label">Record General</div>
                    <div style="font-size:0.8rem;color:var(--text-muted);margin-top:0.25rem;">
                        ${records.overall.pilot_name} - ${records.overall.car_name}
                    </div>
                </div>
        `;

        records.by_category.forEach(r => {
            html += `
                <div class="stat-card">
                    <div class="stat-value">${formatTime(r.best_time_ms)}</div>
                    <div class="stat-label">Cat. ${r.category}</div>
                    <div style="font-size:0.8rem;color:var(--text-muted);margin-top:0.25rem;">
                        ${r.pilot_name}
                    </div>
                </div>
            `;
        });

        html += '</div>';
        section.innerHTML = html;
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function loadPilotOptions() {
    try {
        const pilots = await PilotsAPI.list();
        const select = document.getElementById('history-pilot');
        select.innerHTML = '<option value="">Seleccionar piloto...</option>' +
            pilots.map(p => `<option value="${p.id}">${p.first_name} ${p.last_name}</option>`).join('');
    } catch (err) {
        console.error('Error loading pilots:', err);
    }
}

async function loadPilotHistory() {
    const pilotId = document.getElementById('history-pilot').value;
    if (!pilotId) {
        if (historyChart) historyChart.destroy();
        return;
    }

    try {
        const history = await RankingsAPI.history(pilotId);
        const ctx = document.getElementById('history-chart');

        if (historyChart) historyChart.destroy();

        if (history.length === 0) return;

        const labels = history.map(h => h.run_date);
        const data = history.map(h => h.total_time_ms / 1000);

        historyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Tiempo (segundos)',
                    data: data,
                    borderColor: '#e63946',
                    backgroundColor: '#e6394620',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 5,
                    pointBackgroundColor: '#e63946',
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (ctx) => formatTime(Math.round(ctx.raw * 1000)),
                        },
                    },
                },
                scales: {
                    y: {
                        title: { display: true, text: 'Tiempo (seg)', color: '#8b8fa3' },
                        grid: { color: '#2e3245' },
                        ticks: { color: '#8b8fa3' },
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#8b8fa3' },
                    },
                },
            },
        });
    } catch (err) {
        showToast(err.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadRankings();
    loadRecords();
    loadPilotOptions();
});
