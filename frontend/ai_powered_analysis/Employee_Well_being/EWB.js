// ✅ Toggle Sections Dynamically
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    section.style.display = section.style.display === "none" ? "block" : "none";
}

// ✅ Predict Employee Well-Being
async function predictWellBeing() {
    const username = document.getElementById('wellBeingUsername').value;
    if (!username) {
        showModal('Enter a Username!', 'success'); 
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:8000/classification/predict_wellbeing/${username}`, {
            method: 'GET',
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            document.getElementById('predictionResult').innerHTML = `<p>Predicted Well-Being: <strong>${data.predicted_wellbeing}</strong></p>`;
        } else {
            alert('Error fetching well-being prediction');
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to fetch well-being prediction.");
    }
}

// ✅ Fetch Employee Data
async function fetchEmployeeData() {
    const username = document.getElementById('employeeUsername').value;
    if (!username) {
        showModal('Enter a username ', 'success'); 
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:8000/classification/well_being/${username}`, {
            method: 'GET',
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            const emp = data.employee_data;
            document.getElementById('employeeData').innerHTML = `<div class='employee-box'>
                <p><strong>Username:</strong> ${emp.username}</p>
                <p><strong>Completion Rate:</strong> ${emp.completion_rate}%</p>
                <p><strong>Project Contribution:</strong> ${emp.project_contribtution}</p>
                <p><strong>Workload Handling:</strong> ${emp.workload_handling}</p>
                <p><strong>Attendance:</strong> Present: ${emp.total_present_days}, Absent: ${emp.total_absent_days}, Late: ${emp.total_late_days}</p>
                <p><strong>Salary:</strong> $${emp.salary}</p>
                <p><strong>Appraisals:</strong> ${emp.total_appraisals}</p>
                <p><strong>Penalties:</strong> ${emp.total_penalties}</p>
                <p><strong>Benefits:</strong> ${emp.total_benefits}</p>
                <p><strong>Raise Requests:</strong> ${emp.total_raise_requests}</p>
                <p><strong>Interaction Level:</strong> Messages Sent: ${emp.interaction_level.messages_sent}, Meetings Attended: ${emp.interaction_level.meetings_attended}, Conflicts Involved: ${emp.interaction_level.conflicts_involved}</p>
            </div>`;
        } else {
            alert('Error fetching employee data');
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to fetch employee data.");
    }
}

// ✅ Fetch All Employees
async function fetchAllEmployees() {
    try {
        const response = await fetch('http://localhost:8000/classification/well_being/employee_data/all', {
            method: 'GET',
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            let output = data.employees_data.map(emp => `<div class='employee-box'>
                <p><strong>Username:</strong> ${emp.username}</p>
                <p><strong>Completion Rate:</strong> ${emp.completion_rate}%</p>
                <p><strong>Project Contribution:</strong> ${emp.project_contribtution}</p>
                <p><strong>Workload Handling:</strong> ${emp.workload_handling}</p>
                <p><strong>Attendance:</strong> Present: ${emp.total_present_days}, Absent: ${emp.total_absent_days}, Late: ${emp.total_late_days}</p>
                <p><strong>Salary:</strong> $${emp.salary}</p>
                <p><strong>Appraisals:</strong> ${emp.total_appraisals}</p>
                <p><strong>Penalties:</strong> ${emp.total_penalties}</p>
                <p><strong>Benefits:</strong> ${emp.total_benefits}</p>
                <p><strong>Raise Requests:</strong> ${emp.total_raise_requests}</p>
            </div>`).join('');
            
            document.getElementById('allEmployees').innerHTML = output;
        } else {
            showModal('Error Fetching all Employees!', 'failure'); 
        }
    } catch (error) {
        console.error("Error:", error);
        showModal('Error', 'failure'); 
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