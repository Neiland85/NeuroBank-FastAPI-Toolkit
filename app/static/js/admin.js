// NeuroBank FastAPI Banking System - Main JavaScript

class NeuroBankAdmin {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.setupSearch();
        this.setupTableFilters();
    }

    setupEventListeners() {
        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', this.toggleSidebar);
        }

        // Export buttons
        document.querySelectorAll('[data-export]').forEach(btn => {
            btn.addEventListener('click', this.handleExport.bind(this));
        });

        // Refresh buttons
        document.querySelectorAll('[data-refresh]').forEach(btn => {
            btn.addEventListener('click', this.handleRefresh.bind(this));
        });
    }

    toggleSidebar() {
        const sidebar = document.querySelector('.admin-sidebar');
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
    }

    initializeCharts() {
        // Transaction Chart
        const transactionChartCtx = document.getElementById('transactionChart');
        if (transactionChartCtx) {
            this.createTransactionChart(transactionChartCtx);
        }

        // User Activity Chart
        const userActivityChartCtx = document.getElementById('userActivityChart');
        if (userActivityChartCtx) {
            this.createUserActivityChart(userActivityChartCtx);
        }
    }

    createTransactionChart(ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Transactions',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    createUserActivityChart(ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'Inactive', 'Pending'],
                datasets: [{
                    data: [60, 25, 15],
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    setupSearch() {
        const searchInputs = document.querySelectorAll('[data-search]');
        searchInputs.forEach(input => {
            input.addEventListener('input', this.handleSearch.bind(this));
        });
    }

    setupTableFilters() {
        const filterSelects = document.querySelectorAll('[data-filter]');
        filterSelects.forEach(select => {
            select.addEventListener('change', this.handleFilter.bind(this));
        });
    }

    handleSearch(event) {
        const searchTerm = event.target.value.toLowerCase();
        const targetTable = event.target.dataset.search;
        const table = document.querySelector(`#${targetTable}`);

        if (table) {
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }
    }

    handleFilter(event) {
        const filterValue = event.target.value;
        const targetTable = event.target.dataset.filter;
        const table = document.querySelector(`#${targetTable}`);

        if (table) {
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                if (!filterValue || row.dataset.status === filterValue) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
    }

    handleExport(event) {
        const format = event.target.dataset.export;
        const tableId = event.target.dataset.table;

        if (format === 'csv') {
            this.exportToCSV(tableId);
        } else if (format === 'excel') {
            this.exportToExcel(tableId);
        }
    }

    handleRefresh(event) {
        const target = event.target.dataset.refresh;

        // Show loading spinner
        event.target.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        // Simulate refresh
        setTimeout(() => {
            event.target.innerHTML = '<i class="fas fa-sync-alt"></i>';
            this.showNotification('Data refreshed successfully', 'success');
        }, 1000);
    }

    exportToCSV(tableId) {
        const table = document.querySelector(`#${tableId}`);
        if (!table) return;

        let csv = [];
        const rows = table.querySelectorAll('tr');

        rows.forEach(row => {
            const cols = row.querySelectorAll('td, th');
            const rowData = Array.from(cols).map(col => col.textContent);
            csv.push(rowData.join(','));
        });

        const csvContent = csv.join('\n');
        this.downloadFile(csvContent, 'export.csv', 'text/csv');
    }

    exportToExcel(tableId) {
        // Simplified Excel export - in real implementation, use SheetJS
        this.exportToCSV(tableId);
        this.showNotification('Excel export feature coming soon! CSV downloaded instead.', 'info');
    }

    downloadFile(content, filename, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        window.URL.revokeObjectURL(url);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.neuroBankAdmin = new NeuroBankAdmin();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NeuroBankAdmin;
}
