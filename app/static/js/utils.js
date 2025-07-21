// NeuroBank FastAPI Banking System - Utilities
(function() {
    'use strict';

    // Simple utility functions
    window.NeuroBank = window.NeuroBank || {};

    window.NeuroBank.Utils = {
        formatCurrency: function(amount) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(amount);
        },

        formatDate: function(date) {
            return new Date(date).toLocaleDateString();
        },

        showAlert: function(message, type) {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    };
})();
