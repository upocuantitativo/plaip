/**
 * PLAIP - Main JavaScript
 * Personalized Learning's Artificial Intelligence Paths
 */

// API Helper Functions
const API = {
    async get(endpoint) {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    },

    async post(endpoint, data = {}) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    }
};

// Toast Notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') ||
        createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto"
                    data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// Loading Overlay
function showLoading(message = 'Cargando...') {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">${message}</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.remove();
}

// Skill Colors
const SKILL_COLORS = {
    literacy: '#4CAF50',
    numeracy: '#2196F3',
    digital: '#9C27B0',
    citizenship: '#FF9800'
};

// Format percentage
function formatPercent(value) {
    return `${Math.round(value)}%`;
}

// Format time
function formatTime(minutes) {
    if (minutes < 60) return `${Math.round(minutes)} min`;
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hours}h ${mins}m`;
}

// Create progress bar
function createProgressBar(value, maxValue = 100, color = 'primary') {
    const percent = (value / maxValue) * 100;
    return `
        <div class="progress" style="height: 8px;">
            <div class="progress-bar bg-${color}"
                 style="width: ${percent}%"
                 role="progressbar"
                 aria-valuenow="${value}"
                 aria-valuemin="0"
                 aria-valuemax="${maxValue}">
            </div>
        </div>
    `;
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', () => {
    // Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));

    // Bootstrap popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    popoverTriggerList.forEach(el => new bootstrap.Popover(el));
});

// Export functions for use in templates
window.PLAIP = {
    API,
    showToast,
    showLoading,
    hideLoading,
    SKILL_COLORS,
    formatPercent,
    formatTime,
    createProgressBar
};
