

document.addEventListener('DOMContentLoaded', () => {
    // Only load charts if we are on a page containing chart canvas elements
    const cashFlowCanvas = document.getElementById('cashFlowChart');
    const breakdownCanvas = document.getElementById('breakdownChart');
    const budgetCanvas = document.getElementById('budgetChart');
    const savingsCanvas = document.getElementById('savingsChart');
    
    if (!cashFlowCanvas && !breakdownCanvas && !budgetCanvas && !savingsCanvas) {
        return; // Not on the dashboard page
    }
    
    // Fetch theme-appropriate colors from CSS custom properties
    const style = getComputedStyle(document.body);
    const accentColor = style.getPropertyValue('--accent').trim() || '#10B981';
    const textColor = style.getPropertyValue('--text-primary').trim() || '#0F172A';
    const textMuted = style.getPropertyValue('--text-muted').trim() || '#94A3B8';
    const borderColor = style.getPropertyValue('--border-color').trim() || '#E2E8F0';
    
    // Fetch Chart Data from API
    fetch('/api/charts/data')
        .then(response => response.json())
        .then(data => {
            // 1. Cash Flow Chart: Income vs Expense (Bar Chart)
            if (cashFlowCanvas) {
                new Chart(cashFlowCanvas, {
                    type: 'bar',
                    data: {
                        labels: data.cashflow.labels,
                        datasets: [
                            {
                                label: 'Income',
                                data: data.cashflow.income,
                                backgroundColor: accentColor,
                                borderRadius: 6,
                                barThickness: 12
                            },
                            {
                                label: 'Expense',
                                data: data.cashflow.expense,
                                backgroundColor: '#EF4444', // Red-orange
                                borderRadius: 6,
                                barThickness: 12
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: { color: textColor, font: { family: 'Outfit', size: 12 } },
                                position: 'top'
                            }
                        },
                        scales: {
                            x: {
                                grid: { display: false },
                                ticks: { color: textMuted, font: { family: 'Outfit' } }
                            },
                            y: {
                                grid: { color: borderColor },
                                ticks: { color: textMuted, font: { family: 'Outfit' } }
                            }
                        }
                    }
                });
            }
            
            // 2. Expense Breakdown (Doughnut Chart)
            if (breakdownCanvas) {
                if (data.breakdown.values.length === 0) {
                    // Show a message if no data exists
                    const ctx = breakdownCanvas.getContext('2d');
                    ctx.font = '14px Outfit';
                    ctx.fillStyle = textMuted;
                    ctx.textAlign = 'center';
                    ctx.fillText('No expenses recorded yet', breakdownCanvas.width / 2, breakdownCanvas.height / 2);
                } else {
                    new Chart(breakdownCanvas, {
                        type: 'doughnut',
                        data: {
                            labels: data.breakdown.labels,
                            datasets: [{
                                data: data.breakdown.values,
                                backgroundColor: [
                                    '#10B981', '#3B82F6', '#F59E0B', '#EF4444', 
                                    '#8B5CF6', '#EC4899', '#06B6D4', '#14B8A6', 
                                    '#F43F5E', '#10B981', '#64748B'
                                ],
                                borderWidth: 0,
                                weight: 0.5
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    labels: { color: textColor, font: { family: 'Outfit', size: 11 } },
                                    position: 'right'
                                }
                            },
                            cutout: '70%'
                        }
                    });
                }
            }
            
            // 3. Budget Utilization (Horizontal Bar Chart)
            if (budgetCanvas) {
                if (data.budget.labels.length === 0) {
                    const ctx = budgetCanvas.getContext('2d');
                    ctx.font = '14px Outfit';
                    ctx.fillStyle = textMuted;
                    ctx.textAlign = 'center';
                    ctx.fillText('No budgets set for this month', budgetCanvas.width / 2, budgetCanvas.height / 2);
                } else {
                    new Chart(budgetCanvas, {
                        type: 'bar',
                        data: {
                            labels: data.budget.labels,
                            datasets: [
                                {
                                    label: 'Spent',
                                    data: data.budget.spent,
                                    backgroundColor: (ctx) => {
                                        const idx = ctx.dataIndex;
                                        const limit = data.budget.limits[idx];
                                        const spent = data.budget.spent[idx];
                                        return spent > limit ? '#EF4444' : accentColor;
                                    },
                                    borderRadius: 4,
                                    barThickness: 8
                                },
                                {
                                    label: 'Limit',
                                    data: data.budget.limits,
                                    backgroundColor: '#E2E8F0',
                                    borderRadius: 4,
                                    barThickness: 8
                                }
                            ]
                        },
                        options: {
                            indexAxis: 'y',
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    labels: { color: textColor, font: { family: 'Outfit' } },
                                    position: 'top'
                                }
                            },
                            scales: {
                                x: {
                                    grid: { display: false },
                                    ticks: { color: textMuted, font: { family: 'Outfit' } }
                                },
                                y: {
                                    grid: { display: false },
                                    ticks: { color: textColor, font: { family: 'Outfit', weight: 'bold' } }
                                }
                            }
                        }
                    });
                }
            }
            
            // 4. Savings Progress Chart (Grouped Bars)
            if (savingsCanvas) {
                if (data.savings.labels.length === 0) {
                    const ctx = savingsCanvas.getContext('2d');
                    ctx.font = '14px Outfit';
                    ctx.fillStyle = textMuted;
                    ctx.textAlign = 'center';
                    ctx.fillText('No savings goals set yet', savingsCanvas.width / 2, savingsCanvas.height / 2);
                } else {
                    new Chart(savingsCanvas, {
                        type: 'bar',
                        data: {
                            labels: data.savings.labels,
                            datasets: [
                                {
                                    label: 'Current Amount',
                                    data: data.savings.current,
                                    backgroundColor: accentColor,
                                    borderRadius: 4,
                                    barThickness: 10
                                },
                                {
                                    label: 'Target Amount',
                                    data: data.savings.target,
                                    backgroundColor: '#60A5FA', // blue
                                    borderRadius: 4,
                                    barThickness: 10
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    labels: { color: textColor, font: { family: 'Outfit' } }
                                }
                            },
                            scales: {
                                x: {
                                    grid: { display: false },
                                    ticks: { color: textMuted, font: { family: 'Outfit' } }
                                },
                                y: {
                                    grid: { color: borderColor },
                                    ticks: { color: textMuted, font: { family: 'Outfit' } }
                                }
                            }
                        }
                    });
                }
            }
        })
        .catch(err => console.error('Error fetching chart data:', err));
});
