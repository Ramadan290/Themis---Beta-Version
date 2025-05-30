const token = localStorage.getItem('token');

document.addEventListener("DOMContentLoaded", () => {
    fetch("/status/employee", {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("name").textContent = data.username;
        document.getElementById("position").textContent = data.position;
        document.getElementById("department").textContent = data.department;

        // Convert ISO date (YYYY-MM-DD) to DD-MM-YYYY
        const formattedDate = formatDate(data.start_date);
        document.getElementById("start_date").textContent = formattedDate;

        document.getElementById("status").textContent = data.status;
        document.getElementById("completion_rate").textContent = data.completion_rate;

        let projectList = document.getElementById("project_contributions");
        data.project_contributions.forEach(project => {
            let listItem = document.createElement("li");
            listItem.textContent = `${project.name} - ${project.status}`;
            projectList.appendChild(listItem);
        });

        // Corrected attendance data structure
        document.getElementById("days_present").textContent = data.attendance.Present || 0;
        document.getElementById("days_absent").textContent = data.attendance.Absent || 0;
        document.getElementById("days_late").textContent = data.attendance.Late || 0;

        document.getElementById("salary").textContent = data.payroll.salary;
        document.getElementById("total_appraisals").textContent = data.payroll.total_appraisals;
        document.getElementById("total_penalties").textContent = data.payroll.total_penalties;
    })
    .catch(error => console.error("Error fetching employee data:", error));
});

// ✅ Helper function to convert date format
function formatDate(isoDate) {
    if (!isoDate) return "N/A";  // Handle null, undefined, or empty string
    
    try {
        // Handle cases where the date includes time (YYYY-MM-DDTHH:MM:SS)
        const dateOnly = isoDate.split("T")[0]; 
        const parts = dateOnly.split("-");

        // Ensure valid date format
        if (parts.length !== 3) return "Invalid Date";

        return `${parts[2]}-${parts[1]}-${parts[0]}`; // Convert YYYY-MM-DD to DD-MM-YYYY
    } catch (error) {
        console.error("Error formatting date:", error);
        return "Invalid Date";
    }
}