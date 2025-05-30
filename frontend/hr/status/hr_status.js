let currentChart = null; // Store the active chart instance

document.addEventListener("DOMContentLoaded", () => {
    fetchHRData();
});

function fetchHRData() {
    fetch("/status/hr/analytics", {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + localStorage.getItem("token")
        }
    })
    .then(response => response.json())
    .then(data => {
        if (!data || typeof data !== "object") {
            console.error("Invalid data format from API:", data);
            alert("Failed to load HR analytics data.");
            return;
        }
        window.hrData = data;
        console.log("HR Data Loaded:", window.hrData);
    })
    .catch(error => {
        console.error("Error fetching HR analytics:", error);
        alert("Error loading HR analytics.");
    });
}

// Show specific chart based on button click
function showChart(type) {
    if (!window.hrData) {
        alert("Data not loaded yet. Please wait...");
        return;
    }

    let labels = [], datasetLabel = "", datasetValues = [];

    switch (type) {
        case "attendance":
            if (!window.hrData.attendance_summary) return alert("No attendance data available.");
            labels = Object.keys(window.hrData.attendance_summary);
            datasetLabel = "Attendance Overview";
            datasetValues = Object.values(window.hrData.attendance_summary);
            break;
        case "payroll":
            if (!window.hrData.payroll_distribution) return alert("No payroll data available.");
            labels = Object.keys(window.hrData.payroll_distribution);
            datasetLabel = "Payroll Distribution";
            datasetValues = Object.values(window.hrData.payroll_distribution);
            break;
        case "departments":
            if (!window.hrData.employee_distribution) return alert("No department data available.");
            labels = Object.keys(window.hrData.employee_distribution);
            datasetLabel = "Employees per Department";
            datasetValues = Object.values(window.hrData.employee_distribution);
            break;
        case "completion_rate":
            if (!window.hrData.task_completion_distribution) return alert("No completion rate data available.");
            labels = Object.keys(window.hrData.task_completion_distribution);
            datasetLabel = "Task Completion Rate";
            datasetValues = Object.values(window.hrData.task_completion_distribution);
            break;
        case "workload":
            if (!window.hrData.workload_distribution) return alert("No workload data available.");
            labels = Object.keys(window.hrData.workload_distribution);
            datasetLabel = "Workload Distribution";
            datasetValues = Object.values(window.hrData.workload_distribution);
            break;
        case "workload_balancing":
            if (!window.hrData.workload_balancing) return alert("No workload balancing data available.");
            labels = Object.keys(window.hrData.workload_balancing);
            datasetLabel = "Workload Balancing";
            datasetValues = Object.values(window.hrData.workload_balancing);
            break;
        case "raise_requests":
            if (!window.hrData.raise_requests_summary) return alert("No raise request data available.");
            labels = Object.keys(window.hrData.raise_requests_summary);
            datasetLabel = "Raise Requests Summary";
            datasetValues = Object.values(window.hrData.raise_requests_summary);
            break;
        case "interaction_summary":
            if (!window.hrData.interaction_summary) return alert("No interaction data available.");
            labels = Object.keys(window.hrData.interaction_summary);
            datasetLabel = "Interaction Summary";
            datasetValues = Object.values(window.hrData.interaction_summary);
            break;
        default:
            alert("Invalid chart type");
            return;
    }

    renderChart(labels, datasetLabel, datasetValues, "bar"); // Default to bar chart
    document.getElementById("chart-container").style.display = "block"; // Show chart container
    document.getElementById("chart-type-buttons").style.display = "block"; // Show chart type buttons
}

// Render the chart dynamically
function renderChart(labels, datasetLabel, datasetValues, chartType) {
    const ctx = document.getElementById("analyticsChart").getContext("2d");

    if (currentChart) {
        currentChart.destroy();
    }

    currentChart = new Chart(ctx, {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                label: datasetLabel,
                data: datasetValues,
                backgroundColor: ["red", "blue", "green", "yellow", "orange", "purple"],
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Update chart type dynamically
function updateChartType(type) {
    if (currentChart) {
        currentChart.config.type = type;
        currentChart.update();
    }
}

function closeChart() {
    document.getElementById("chart-container").style.display = "none"; // Hide chart
    document.getElementById("chart-type-buttons").style.display = "none"; // Hide buttons

    // Change button color dynamically
    const closeButton = document.querySelector(".close-chart-btn");
    if (closeButton) {
        closeButton.style.backgroundColor = "#6c757d"; // Gray color after closing
        closeButton.style.color = "white"; // Ensure text remains visible
    }

    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }
}
