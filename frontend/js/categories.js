// Rally Timing - Categories Page Logic

let editingCategoryId = null;

async function loadCategories() {
    try {
        const categories = await CategoriesAPI.list();
        const tbody = document.getElementById('categories-table');

        if (categories.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="empty-state">No hay categorias registradas</td></tr>';
            return;
        }

        tbody.innerHTML = categories.map(c => `
            <tr>
                <td><span class="badge badge-category">${c.name}</span></td>
                <td>${c.description || '-'}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="editCategory(${c.id})">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteCategory(${c.id}, '${c.name}')">Eliminar</button>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function openModal(category = null) {
    editingCategoryId = category ? category.id : null;
    document.getElementById('modal-title').textContent = category ? 'Editar Categoria' : 'Agregar Categoria';
    document.getElementById('category-id').value = category ? category.id : '';
    document.getElementById('cat-name').value = category ? category.name : '';
    document.getElementById('cat-description').value = category ? (category.description || '') : '';
    document.getElementById('category-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('category-modal').classList.remove('active');
    document.getElementById('category-form').reset();
    editingCategoryId = null;
}

async function editCategory(id) {
    try {
        const category = await CategoriesAPI.get(id);
        openModal(category);
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function saveCategory(e) {
    e.preventDefault();
    const data = {
        name: document.getElementById('cat-name').value,
        description: document.getElementById('cat-description').value,
    };

    try {
        if (editingCategoryId) {
            await CategoriesAPI.update(editingCategoryId, data);
            showToast('Categoria actualizada');
        } else {
            await CategoriesAPI.create(data);
            showToast('Categoria creada');
        }
        closeModal();
        loadCategories();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function deleteCategory(id, name) {
    if (!confirm(`Desactivar categoria "${name}"?`)) return;
    try {
        await CategoriesAPI.delete(id);
        showToast('Categoria desactivada');
        loadCategories();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', loadCategories);
