// ✅ Toggle Sections Dynamically
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    section.style.display = section.style.display === "none" ? "block" : "none";
}

// ✅ Predict Employee BCR
async function predictBCR() {
    const username = document.getElementById('bcrUsername').value;
    if (!username) {
        showModal('Enter a Username!!', 'failure'); 
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/classification/predict_bcr/${username}`, {
            method: 'GET',
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        });

        const data = await response.json();
        if (data.status === "success") {
            document.getElementById("bcrPredictionResult").innerHTML = `<p>Predicted BCR: <strong>${data.predicted_bcr}</strong></p>`;
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        console.error("Error:", error);
        showModal('Error Occured!!', 'failure'); 
    }
}

// ✅ Fetch Specific Employee BCR Data
async function fetchEmployeeBCRData() {
    const username = document.getElementById('employeeBCRUsername').value;
    if (!username) {
        showModal('Enter a Username!!', 'failure'); 
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/classification/bcr_data/${username}`, {
            method: 'GET',
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        });

        const data = await response.json();
        if (data.status === "success") {
            const emp = data.employee_data;
            document.getElementById("employeeBCRData").innerHTML = `<div class='employee-box'>
                <p><strong>Username:</strong> ${emp.username}</p>
                <p><strong>Salary:</strong> $${emp.salary}</p>
                <p><strong>Appraisals:</strong> ${emp.total_appraisals}</p>
                <p><strong>Penalties:</strong> ${emp.total_penalties}</p>
                <p><strong>Raise Requests:</strong> ${emp.total_raise_requests}</p>
                <p><strong>Completion Rate:</strong> ${emp.completion_rate}%</p>
                <p><strong>Project Contribution:</strong> ${emp.project_contribtution}</p>
                <p><strong>Workload Handling:</strong> ${emp.workload_handling}</p>
            </div>`;
        } else {
            alert("Error fetching employee BCR data.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to fetch employee BCR data.");
    }
}

// ✅ Fetch All Employees BCR Data
async function fetchAllEmployeesBCR() {
    try {
        const response = await fetch('http://localhost:8000/classification/bcr_data/all', {
            method: 'GET',
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        });

        const data = await response.json();
        if (data.status === "success") {
            let output = data.employees_data.map(emp => `<div class='employee-box'>
                <p><strong>Username:</strong> ${emp.username}</p>
                <p><strong>Salary:</strong> $${emp.salary}</p>
                <p><strong>Appraisals:</strong> ${emp.total_appraisals}</p>
                <p><strong>Penalties:</strong> ${emp.total_penalties}</p>
                <p><strong>Raise Requests:</strong> ${emp.total_raise_requests}</p>
                <p><strong>Completion Rate:</strong> ${emp.completion_rate}%</p>
                <p><strong>Project Contribution:</strong> ${emp.project_contribtution}</p>
                <p><strong>Workload Handling:</strong> ${emp.workload_handling}</p>
            </div>`).join('');
            
            document.getElementById('allEmployeesBCR').innerHTML = output;
        } else {
            showModal('Error!!', 'failure'); 
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to fetch all employees BCR data.");
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