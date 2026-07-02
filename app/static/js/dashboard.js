const chartData = window.smartSpendCharts || {};
const chartColor = "#2563eb";
const categoryCanvas = document.getElementById("categoryChart");
if (categoryCanvas) {
  new Chart(categoryCanvas, {
    type: "pie",
    data: {
      labels: chartData.categoryLabels || [],
      datasets: [{
        data: chartData.categoryValues || [],
        backgroundColor: ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#0891b2", "#4b5563", "#9333ea", "#ea580c", "#64748b"],
        borderWidth: 0
      }]
    },
    options: { plugins: { legend: { position: "bottom" } } }
  });
}
const monthlyCanvas = document.getElementById("monthlyChart");
if (monthlyCanvas) {
  new Chart(monthlyCanvas, {
    type: "bar",
    data: {
      labels: chartData.monthlyLabels || [],
      datasets: [{ label: "Monthly spend", data: chartData.monthlyValues || [], backgroundColor: chartColor }]
    },
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
  });
}
