/**
 * NUAM - Main JavaScript
 * Modern JS for Django Templates with Nginx Support
 */

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');

    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.animation = 'slideOut 0.3s ease-out forwards';
                setTimeout(() => alert.remove(), 300);
            });
        }, 5000);
    }
});

// API Configuration - Works with Nginx Reverse Proxy
const API_CONFIG = {
    baseURL: '/api/v1',
    currencyURL: '/currency-api/v1',
    timeout: 30000,

    // Get CSRF token from cookie
    getCSRFToken: function() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    // Helper function to make API calls
    fetch: async function(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, mergedOptions);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Currency API helper
    fetchCurrency: async function(endpoint, options = {}) {
        const url = `${this.currencyURL}${endpoint}`;
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Currency API Error:', error);
            throw error;
        }
    }
};

// Show notification/alert
function showAlert(message, type = 'info') {
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    messagesContainer.appendChild(alert);

    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease-out forwards';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    document.body.appendChild(container);
    return container;
}

// Form validation helper
function validateForm(formId, rules) {
    const form = document.getElementById(formId);
    if (!form) return false;

    let isValid = true;

    for (const [fieldId, validation] of Object.entries(rules)) {
        const field = document.getElementById(fieldId);
        if (!field) continue;

        if (validation.required && !field.value.trim()) {
            showAlert(`${validation.label} es requerido`, 'error');
            isValid = false;
        }

        if (validation.minLength && field.value.length < validation.minLength) {
            showAlert(`${validation.label} debe tener al menos ${validation.minLength} caracteres`, 'error');
            isValid = false;
        }

        if (validation.pattern && !validation.pattern.test(field.value)) {
            showAlert(`${validation.label} no tiene el formato correcto`, 'error');
            isValid = false;
        }
    }

    return isValid;
}

// Loading spinner helper
function showLoading(element) {
    element.disabled = true;
    element.dataset.originalText = element.textContent;
    element.textContent = 'Cargando...';
}

function hideLoading(element) {
    element.disabled = false;
    element.textContent = element.dataset.originalText || 'Enviar';
}

// Export for use in other scripts
window.NUAM = {
    API: API_CONFIG,
    showAlert,
    validateForm,
    showLoading,
    hideLoading
};
