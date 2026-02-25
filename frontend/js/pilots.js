// Rally Timing - Pilots Page Logic

let editingPilotId = null;

async function loadPilots() {
    const search = document.getElementById('search-input').value;
    try {
        const pilots = await PilotsAPI.list(search);
        const tbody = document.getElementById('pilots-table');

        if (pilots.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No hay pilotos registrados</td></tr>';
            return;
        }

        tbody.innerHTML = pilots.map(p => `
            <tr>
                <td><strong>${p.first_name} ${p.last_name}</strong></td>
                <td>${p.nickname || '-'}</td>
                <td>${p.phone || '-'}</td>
                <td>${p.license_number || '-'}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="editPilot(${p.id})">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="deletePilot(${p.id}, '${p.first_name} ${p.last_name}')">Eliminar</button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function openModal(pilot = null) {
    editingPilotId = pilot ? pilot.id : null;
    document.getElementById('modal-title').textContent = pilot ? 'Editar Piloto' : 'Agregar Piloto';
    document.getElementById('pilot-id').value = pilot ? pilot.id : '';
    document.getElementById('first_name').value = pilot ? pilot.first_name : '';
    document.getElementById('last_name').value = pilot ? pilot.last_name : '';
    document.getElementById('nickname').value = pilot ? (pilot.nickname || '') : '';
    document.getElementById('phone').value = pilot ? (pilot.phone || '') : '';
    document.getElementById('email').value = pilot ? (pilot.email || '') : '';
    document.getElementById('license_number').value = pilot ? (pilot.license_number || '') : '';
    document.getElementById('notes').value = pilot ? (pilot.notes || '') : '';
    document.getElementById('pilot-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('pilot-modal').classList.remove('active');
    document.getElementById('pilot-form').reset();
    editingPilotId = null;
}

async function editPilot(id) {
    try {
        const pilot = await PilotsAPI.get(id);
        openModal(pilot);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function savePilot(e) {
    e.preventDefault();
    const data = {
        first_name: document.getElementById('first_name').value,
        last_name: document.getElementById('last_name').value,
        nickname: document.getElementById('nickname').value,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value,
        license_number: document.getElementById('license_number').value,
        notes: document.getElementById('notes').value,
    };

    try {
        if (editingPilotId) {
            await PilotsAPI.update(editingPilotId, data);
            showToast('Piloto actualizado');
        } else {
            await PilotsAPI.create(data);
            showToast('Piloto creado');
        }
        closeModal();
        loadPilots();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function deletePilot(id, name) {
    if (!confirm(`Desactivar piloto "${name}"?`)) return;
    try {
        await PilotsAPI.delete(id);
        showToast('Piloto desactivado');
        loadPilots();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', loadPilots);
