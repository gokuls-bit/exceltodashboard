// FinFlow Main Scripts

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Bootstrap Tooltips and Popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 2. Setup Modals Edit Buttons
    // For Income list:
    const editIncomeModal = document.getElementById('editIncomeModal');
    if (editIncomeModal) {
        editIncomeModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            const id = button.getAttribute('data-id');
            const date = button.getAttribute('data-date');
            const source = button.getAttribute('data-source');
            const amount = button.getAttribute('data-amount');
            const desc = button.getAttribute('data-description');

            const form = editIncomeModal.querySelector('form');
            form.setAttribute('action', `/income/edit/${id}`);

            editIncomeModal.querySelector('#edit-date').value = date;
            editIncomeModal.querySelector('#edit-source').value = source;
            editIncomeModal.querySelector('#edit-amount').value = amount;
            editIncomeModal.querySelector('#edit-description').value = desc;
        });
    }

    // For Expense list:
    const editExpenseModal = document.getElementById('editExpenseModal');
    if (editExpenseModal) {
        editExpenseModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            const id = button.getAttribute('data-id');
            const date = button.getAttribute('data-date');
            const category = button.getAttribute('data-category');
            const amount = button.getAttribute('data-amount');
            const desc = button.getAttribute('data-description');

            const form = editExpenseModal.querySelector('form');
            form.setAttribute('action', `/expense/edit/${id}`);

            editExpenseModal.querySelector('#edit-date').value = date;
            editExpenseModal.querySelector('#edit-category').value = category;
            editExpenseModal.querySelector('#edit-amount').value = amount;
            editExpenseModal.querySelector('#edit-description').value = desc;
        });
    }

    // For Budget Planner list:
    const editBudgetModal = document.getElementById('editBudgetModal');
    if (editBudgetModal) {
        editBudgetModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            const id = button.getAttribute('data-id');
            const limit = button.getAttribute('data-limit');
            const category = button.getAttribute('data-category');

            const form = editBudgetModal.querySelector('form');
            form.setAttribute('action', `/budget/edit/${id}`);

            editBudgetModal.querySelector('#edit-category-name').innerText = category;
            editBudgetModal.querySelector('#edit-limit').value = limit;
        });
    }

    // For Savings Goals list:
    const editSavingsModal = document.getElementById('editSavingsModal');
    if (editSavingsModal) {
        editSavingsModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            const id = button.getAttribute('data-id');
            const name = button.getAttribute('data-name');
            const target = button.getAttribute('data-target');
            const current = button.getAttribute('data-current');
            const date = button.getAttribute('data-date');

            const form = editSavingsModal.querySelector('form');
            form.setAttribute('action', `/savings/edit/${id}`);

            editSavingsModal.querySelector('#edit-name').value = name;
            editSavingsModal.querySelector('#edit-target').value = target;
            editSavingsModal.querySelector('#edit-current').value = current;
            editSavingsModal.querySelector('#edit-date').value = date || '';
        });
    }
});
