/**
 * Currency Converter Widget
 * Real-time currency conversion using NUAM API through Nginx proxy
 */

(function() {
    'use strict';

    let conversionTimeout = null;
    const DEBOUNCE_DELAY = 500; // milliseconds

    // Initialize currency converter when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initCurrencyConverter();
    });

    function initCurrencyConverter() {
        const amountInput = document.getElementById('amount');
        const fromCurrency = document.getElementById('from_currency');
        const toCurrency = document.getElementById('to_currency');

        if (!amountInput || !fromCurrency || !toCurrency) {
            console.log('Currency converter elements not found on this page');
            return;
        }

        // Add event listeners
        amountInput.addEventListener('input', debounceConversion);
        fromCurrency.addEventListener('change', performConversion);
        toCurrency.addEventListener('change', performConversion);

        // Perform initial conversion
        performConversion();
    }

    function debounceConversion() {
        clearTimeout(conversionTimeout);
        conversionTimeout = setTimeout(performConversion, DEBOUNCE_DELAY);
    }

    async function performConversion() {
        const amountInput = document.getElementById('amount');
        const fromCurrency = document.getElementById('from_currency');
        const toCurrency = document.getElementById('to_currency');
        const resultText = document.getElementById('result_text');
        const rateText = document.getElementById('rate_text');
        const timestamp = document.getElementById('timestamp');

        const amount = parseFloat(amountInput.value);
        const from = fromCurrency.value;
        const to = toCurrency.value;

        // Validation
        if (!amount || amount <= 0) {
            resultText.textContent = 'Ingrese un monto válido';
            rateText.textContent = 'Tasa: -';
            timestamp.textContent = '-';
            return;
        }

        if (from === to) {
            const formattedAmount = formatCurrency(amount, to);
            resultText.textContent = formattedAmount;
            rateText.textContent = 'Tasa: 1.00 (misma moneda)';
            timestamp.textContent = new Date().toLocaleString('es-CL');
            return;
        }

        // Show loading state
        resultText.textContent = 'Calculando...';
        rateText.textContent = 'Tasa: ...';

        try {
            // Use the Nginx proxy path for API calls
            const apiURL = `/api/v1/divisas/tasa-ajax/?from=${from}&to=${to}`;
            const response = await fetch(apiURL);

            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }

            const data = await response.json();

            // Check if the API returned success
            if (!data.success) {
                throw new Error(data.error || 'Error desconocido');
            }

            // Calculate conversion
            const rate = parseFloat(data.rate);

            if (!rate || isNaN(rate) || rate <= 0) {
                throw new Error('Tasa de cambio inválida');
            }

            const convertedAmount = amount * rate;

            // Update UI
            resultText.textContent = `${formatCurrency(amount, from)} = ${formatCurrency(convertedAmount, to)}`;
            rateText.textContent = `Tasa: 1 ${from} = ${rate.toFixed(4)} ${to}`;
            timestamp.textContent = `Actualizado: ${new Date().toLocaleString('es-CL')}`;

        } catch (error) {
            console.error('Error en conversión:', error);
            resultText.textContent = 'Error al obtener la tasa';
            rateText.textContent = 'Por favor, intente nuevamente';
            timestamp.textContent = '-';

            // Log detailed error for debugging
            console.error('Detalles del error:', {
                message: error.message,
                from: from,
                to: to,
                amount: amount
            });

            // Show error notification
            if (window.NUAM && window.NUAM.showAlert) {
                window.NUAM.showAlert('Error al obtener la tasa de cambio', 'error');
            }
        }
    }

    function formatCurrency(value, currency) {
        const locale = 'es-CL';

        // Determine decimal places based on currency
        const decimals = ['JPY', 'KRW'].includes(currency) ? 0 : 2;

        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    }

    // Export functions for testing
    window.CurrencyConverter = {
        init: initCurrencyConverter,
        convert: performConversion
    };

})();
