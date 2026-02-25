// Rally Timing - Cars Page Logic

let editingCarId = null;

async function loadCars() {
    const category = document.getElementById('filter-category').value;
    try {
        const cars = await CarsAPI.list({ category: category || undefined });
        const tbody = document.getElementById('cars-table');

        if (cars.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No hay autos registrados</td></tr>';
            return;
        }

        tbody.innerHTML = cars.map(c => `
            <tr>
                <td><strong>${c.brand} ${c.model}</strong></td>
                <td>${c.year || '-'}</td>
                <td><span class="badge badge-category">${c.category}</span></td>
                <td>${c.pilot_name || 'Sin asignar'}</td>
                <td>${c.plate_number || '-'}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="editCar(${c.id})">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteCar(${c.id}, '${c.brand} ${c.model}')">Eliminar</button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function loadPilotOptions() {
    try {
        const pilots = await PilotsAPI.list();
        const select = document.getElementById('car-pilot');
        select.innerHTML = '<option value="">Sin asignar</option>' +
            pilots.map(p => `<option value="${p.id}">${p.first_name} ${p.last_name}</option>`).join('');
    } catch (err) {
        console.error('Error loading pilots for select:', err);
    }
}

async function openCarModal(car = null) {
    await loadPilotOptions();
    editingCarId = car ? car.id : null;
    document.getElementById('car-modal-title').textContent = car ? 'Editar Auto' : 'Agregar Auto';
    document.getElementById('car-id').value = car ? car.id : '';
    document.getElementById('car-brand').value = car ? car.brand : '';
    document.getElementById('car-model').value = car ? car.model : '';
    document.getElementById('car-year').value = car ? (car.year || '') : '';
    document.getElementById('car-category').value = car ? car.category : '';
    document.getElementById('car-pilot').value = car ? (car.pilot_id || '') : '';
    document.getElementById('car-plate').value = car ? (car.plate_number || '') : '';
    document.getElementById('car-notes').value = car ? (car.notes || '') : '';
    document.getElementById('car-modal').classList.add('active');
}

function closeCarModal() {
    document.getElementById('car-modal').classList.remove('active');
    document.getElementById('car-form').reset();
    editingCarId = null;
}

async function editCar(id) {
    try {
        const car = await CarsAPI.get(id);
        openCarModal(car);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function saveCar(e) {
    e.preventDefault();
    const yearVal = document.getElementById('car-year').value;
    const pilotVal = document.getElementById('car-pilot').value;

    const data = {
        brand: document.getElementById('car-brand').value,
        model: document.getElementById('car-model').value,
        year: yearVal ? parseInt(yearVal) : null,
        category: document.getElementById('car-category').value,
        pilot_id: pilotVal ? parseInt(pilotVal) : null,
        plate_number: document.getElementById('car-plate').value,
        notes: document.getElementById('car-notes').value,
    };

    try {
        if (editingCarId) {
            await CarsAPI.update(editingCarId, data);
            showToast('Auto actualizado');
        } else {
            await CarsAPI.create(data);
            showToast('Auto creado');
        }
        closeCarModal();
        loadCars();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function deleteCar(id, name) {
    if (!confirm(`Desactivar auto "${name}"?`)) return;
    try {
        await CarsAPI.delete(id);
        showToast('Auto desactivado');
        loadCars();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', loadCars);
