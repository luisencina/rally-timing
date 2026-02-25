// Rally Timing - Shared Utilities

/**
 * Format milliseconds to MM:SS.mmm display string.
 * Example: 154567 -> "02:34.567"
 */
function formatTime(ms) {
    if (ms == null || ms <= 0) return '--:--.---';
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const millis = ms % 1000;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(millis).padStart(3, '0')}`;
}

/**
 * Parse time components to milliseconds.
 */
function timeToMs(minutes, seconds, millis) {
    return (parseInt(minutes) || 0) * 60000 +
           (parseInt(seconds) || 0) * 1000 +
           (parseInt(millis) || 0);
}

/**
 * Parse milliseconds into components { minutes, seconds, millis }.
 */
function msToComponents(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    return {
        minutes: Math.floor(totalSeconds / 60),
        seconds: totalSeconds % 60,
        millis: ms % 1000,
    };
}

/**
 * Get today's date as YYYY-MM-DD string.
 */
function todayString() {
    return new Date().toISOString().slice(0, 10);
}

/**
 * Track condition labels in Spanish.
 */
const CONDITION_LABELS = {
    dry: 'Seco',
    wet: 'Mojado',
    humid: 'Humedo',
};

/**
 * Show a toast notification.
 */
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-fade');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Inject the shared navigation bar into the page.
 */
function renderNav() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const links = [
        { href: 'index.html', label: 'Dashboard', icon: '&#9776;' },
        { href: 'pilots.html', label: 'Pilotos', icon: '&#9823;' },
        { href: 'cars.html', label: 'Autos', icon: '&#9951;' },
        { href: 'categories.html', label: 'Categorias', icon: '&#9881;' },
        { href: 'runs.html', label: 'Pasadas', icon: '&#9201;' },
        { href: 'rankings.html', label: 'Rankings', icon: '&#9733;' },
    ];

    const nav = document.createElement('nav');
    nav.className = 'main-nav';
    nav.innerHTML = `
        <div class="nav-brand">Rally Timing</div>
        <div class="nav-links">
            ${links.map(l =>
                `<a href="${l.href}" class="${currentPage === l.href ? 'active' : ''}">${l.icon} ${l.label}</a>`
            ).join('')}
        </div>
    `;

    document.body.insertBefore(nav, document.body.firstChild);
}

// Render nav on every page load
document.addEventListener('DOMContentLoaded', renderNav);
