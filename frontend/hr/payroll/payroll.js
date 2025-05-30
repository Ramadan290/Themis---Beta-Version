const token = localStorage.getItem("token");



// Function to fetch and display payroll data including attendance
async function fetchPayrolls() {
    const username = document.getElementById("usernameFilter").value;
    const minSalary = document.getElementById("minSalaryFilter").value;
    const maxSalary = document.getElementById("maxSalaryFilter").value;

    let url = `/payroll/hr/get?`;
    if (username) url += `username=${username}&`;
    if (minSalary) url += `min_salary=${minSalary}&`;
    if (maxSalary) url += `max_salary=${maxSalary}&`;

    try {
        const response = await fetch(url, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        if (!response.ok) throw new Error("Failed to fetch payrolls");

        const payrolls = await response.json();
        const payrollTable = document.getElementById("payrollTableBody");
        payrollTable.innerHTML = "";

        payrolls.forEach((payroll) => {
            const row = document.createElement("tr");
            row.innerHTML = `
            <td><div class="box">${payroll.username}</div></td>
            <td><div class="box">${payroll.salary}</div></td>
                        <td>
            ${payroll.benefits.map(b => `<div class="box">${b}</div>`).join("")}
        </td>
                <td>
                    ${payroll.appraisals.map(a => `<div class="box">${a.amount} on ${a.date}</div>`).join("")}
                </td>
                <td>
                    ${payroll.penalties.map(p => `<div class="box">${p.amount} (${p.reason})</div>`).join("")}
                </td>
            `;
            payrollTable.appendChild(row);
        });

        showSalaries(); // Reveal salaries after filtering
    } catch (error) {
        console.error("Error fetching payrolls:", error);
    }
}

// Function to show salaries when filtering is applied
function showSalaries() {
    // Show salary column in the table header
    document.querySelectorAll(".salary-column").forEach(column => {
        column.style.display = "table-cell"; // Show salary header
    });

    // Show salary values inside the table rows
    document.querySelectorAll("#payrollTableBody tr td:nth-child(2)").forEach(cell => {
        cell.style.display = "table-cell"; // Show salary column in tbody
    });

    // Show the collapse button
    document.getElementById("collapseButton").style.display = "inline-block";
}

function hideSalaries() {
    // Hide salary column in the table header
    document.querySelectorAll(".salary-column").forEach(column => {
        column.style.display = "none"; // Hide salary header
    });


    // Hide salary values inside the table rows
    document.querySelectorAll("#payrollTableBody tr td:nth-child(2)").forEach(cell => {
        cell.style.display = "none"; // Hide salary column in tbody
    });

    // Hide the collapse button after collapsing salaries
    document.getElementById("collapseButton").style.display = "none";
}

// Function to update salary using username
async function updateSalary() {
    const usernameField = document.getElementById("salaryEmployeeId");
    const salaryField = document.getElementById("newSalary");

    const username = usernameField.value;
    const newSalary = salaryField.value;

    try {
        const response = await fetch(`/payroll/hr/update/${username}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ salary: parseFloat(newSalary) }),
        });

        if (!response.ok) throw new Error("Failed to update salary");

        showModal('Salary updated successfully!', 'success'); // Success message
        fetchPayrolls();

        // Clear the input fields
        usernameField.value = "";
        salaryField.value = "";
    } catch (error) {
        showModal('Failed to Update Salary!', 'failure'); // Success message
    }
}

// Function to add an appraisal using username
async function addAppraisal() {
    const usernameField = document.getElementById("appraisalEmployeeId");
    const amountField = document.getElementById("appraisalAmount");
    const dateField = document.getElementById("appraisalDate");

    const username = usernameField.value;
    const amount = amountField.value;
    const date = dateField.value;

    try {
        const response = await fetch(`/payroll/hr/update/${username}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ appraisals: [{ amount: parseFloat(amount), date }] }),
        });

        if (!response.ok) throw new Error("Failed to add appraisal");

        showModal('Appraisal applied successfully!', 'success'); // Success message
        fetchPayrolls();

        // Clear the input fields
        usernameField.value = "";
        amountField.value = "";
        dateField.value = "";
    } catch (error) {
        showModal('Failed to Add Appraisal', 'Failure'); 
    }
}

// Function to add a penalty using username
async function addPenalty() {
    const usernameField = document.getElementById("penaltyEmployeeId");
    const amountField = document.getElementById("penaltyAmount");
    const reasonField = document.getElementById("penaltyReason");

    const username = usernameField.value;
    const amount = amountField.value;
    const reason = reasonField.value;

    try {
        const response = await fetch(`/payroll/hr/update/${username}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ penalties: [{ amount: parseFloat(amount), reason }] }),
        });

        if (!response.ok) throw new Error("Failed to add penalty");

        showModal('Penalty applied successfully!', 'success'); // Success message
        fetchPayrolls();

        // Clear the input fields
        usernameField.value = "";
        amountField.value = "";
        reasonField.value = "";
    } catch (error) {
        showModal('Failed to Add Penalty', 'failure'); 
    }
}


/*******************************************Raise Requests**************************************/


// Function to fetch and display pending raise requests
// Load Raise Requests on Page Load
document.addEventListener("DOMContentLoaded", fetchRaiseRequests);

/***************************************************************************************************************/

// Function to fetch and display pending raise requests
async function fetchRaiseRequests() {
    try {
        const response = await fetch("/payroll/hr/raise-requests/pending", {
            headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) throw new Error("Failed to fetch raise requests");

        const data = await response.json();
        const raiseRequests = data.pending_raise_requests;
        const raiseRequestsTable = document.getElementById("raiseRequestsTableBody"); // ✅ FIXED: Corrected ID Reference

        if (!raiseRequestsTable) {
            console.error("Error: Table body element not found.");
            return;
        }

        raiseRequestsTable.innerHTML = ""; // Clear previous content

        if (!raiseRequests || raiseRequests.length === 0) {
            raiseRequestsTable.innerHTML = `<tr><td colspan="6">No pending raise requests.</td></tr>`;
            return;
        }

        raiseRequests.forEach((request) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${request.request_id}</td>
                <td>${request.username}</td>
                <td>${request.requested_amount}</td>
                <td>${request.reason}</td>
                <td>${request.status}</td>
                <td>
                    <button onclick="manageRaiseRequest('${request.request_id}', 'accept')">Approve</button>
                    <button onclick="manageRaiseRequest('${request.request_id}', 'reject')">Reject</button>
                </td>
            `;
            raiseRequestsTable.appendChild(row);
        });

    } catch (error) {
        console.error("Error fetching raise requests:", error);
    }
}

/***************************************************************************************************************/

// Function to approve or reject a raise request
async function manageRaiseRequest(requestId, action) {
    try {
        const response = await fetch(`/payroll/hr/raise-request/approval/${requestId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                Authorization: `Bearer ${token}`,
            },
            body: new URLSearchParams({ action }),
        });

        if (!response.ok) throw new Error(`Failed to ${action} raise request`);

        showModal(`Raise request ${action}ed successfully!`, "success");
        fetchRaiseRequests(); // Refresh table after action
    } catch (error) {
        console.error(`Error ${action}ing raise request:`, error);
        showModal(`Error ${action}ing raise request.`, "failure");
    }
}




function showModal(message, type = 'success') {
    const modal = document.getElementById('raiseModal');
    const modalMessage = document.getElementById('raise-modal-message');

    modalMessage.textContent = message;
    
    // Reset modal class and apply appropriate styling
    modal.className = 'modal'; // Reset any existing classes
    if (type === 'success') {
        modal.style.backgroundColor = '#28a745'; // Green for success
    } else {
        modal.style.backgroundColor = '#dc3545'; // Red for failure
    }

    modal.style.display = 'block';

    // Auto-fade and remove after 3 seconds
    setTimeout(() => {
        modal.classList.add('fade-out');
        setTimeout(() => {
            modal.style.display = 'none';
            modal.classList.remove('fade-out'); // Reset for next use
        }, 500);
    }, 3000);
}