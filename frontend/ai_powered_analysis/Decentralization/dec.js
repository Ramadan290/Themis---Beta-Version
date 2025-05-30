// ✅ Toggle Sections Dynamically
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    section.style.display = section.style.display === "none" ? "block" : "none";
}

// ✅ Predict Employee Department Change and Display to HR
async function predictDepartment() {
    const username = document.getElementById('decentralizationUsername').value;
    if (!username) {
        showModal('Enter a Username!!', 'failure'); 
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/classification/predict_department/${username}`, {
            method: 'GET',
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
        });

        const data = await response.json();
        if (data.status === "success") {
            document.getElementById("departmentPredictionResult").innerHTML = `<p>Prediction Successful</p>`;
            document.getElementById("currentDepartment").innerText = data.department;
            document.getElementById("suggestedDepartment").innerText = data.suggested_department;

            // ✅ Show HR Approval Section
            document.getElementById("hrApprovalSection").style.display = "block";
        } else {
            alert("Error: " + data.message);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to fetch department prediction.");
    }
}

// ✅ HR Approval for Department Change
async function updateDepartment(acceptChange) {
    const username = document.getElementById('decentralizationUsername').value;
    if (!username) {
        showModal('Please Enter a username before decision', 'failure'); 
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/classification/update_department/${username}`, {
            method: "PUT",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token"),
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ accept_change: acceptChange })
        });

        const data = await response.json();
        document.getElementById("approvalMessage").innerText = data.message;

        // ✅ Hide Approval Section After Decision
        setTimeout(() => {
            document.getElementById("hrApprovalSection").style.display = "none";
        }, 3000);
    } catch (error) {
        console.error("Error:", error);
        alert("Failed to update department.");
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