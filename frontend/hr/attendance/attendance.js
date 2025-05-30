const token = localStorage.getItem("token");



document.getElementById("openModalBtn").addEventListener("click", function () {
    document.getElementById("reviewModal").style.display = "block";
});

document.getElementById("closeModal").addEventListener("click", function () {
    document.getElementById("reviewModal").style.display = "none";
});

// Toggle Attendance Section
function toggleAttendance() {
    const section = document.getElementById("attendanceSection");
    const button = document.getElementById("attendanceToggle");

    if (section.style.display === "none") {
        section.style.display = "block";
        button.textContent = "▼ Hide Results";
        fetchHRAttendanceRecords(); // Fetch all records when expanded
    } else {
        section.style.display = "none";
        button.textContent = "▶ Show Results";
    }
}

// Toggle Sick Notes Section
function toggleSickNotes() {
    const section = document.getElementById("sickNotesSection");
    const button = document.getElementById("sickNotesToggle");

    if (section.style.display === "none") {
        section.style.display = "block";
        button.textContent = "▼ Hide Results";
        fetchPendingSickNotes(); // Fetch all pending sick notes when expanded
    } else {
        section.style.display = "none";
        button.textContent = "▶ Show";
    }
}

// Fetch all Attendance Records
async function fetchHRAttendanceRecords() {
    try {
        const response = await fetch('/attendance/hr/get', {
            headers: { 'Authorization': `Bearer ${token}` },
        });

        const hrAttendanceRecordsElement = document.getElementById("hrAttendanceRecordsElement");
        hrAttendanceRecordsElement.innerHTML = '';

        if (response.ok) {
            const records = await response.json();
            records.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${record.attendance_id}</td>
                    <td>${record.username}</td>
                    <td>${record.date}</td>
                    <td>${record.status}</td>
                    <td>${record.sick_note ? record.sick_note.status : 'N/A'}</td>`;
                hrAttendanceRecordsElement.appendChild(row);
            });
        } else {
            hrAttendanceRecordsElement.innerHTML = '<tr><td colspan="5">No attendance records found.</td></tr>';
        }
    } catch (error) {
        console.error('Error fetching HR attendance records:', error);
    }
}

// Filter Attendance Records
async function filterHRAttendance() {
    const date = document.getElementById('filter-date').value;
    const username = document.getElementById('filter-username').value;
    const status = document.getElementById('filter-status').value;

    let url = `/attendance/hr/filter?`;
    if (date) url += `date=${date}&`;
    if (username) url += `username=${username}&`;
    if (status) url += `status=${status}&`;

    try {
        const response = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });
        const hrAttendanceRecordsElement = document.getElementById("hrAttendanceRecordsElement");
        hrAttendanceRecordsElement.innerHTML = '';

        if (response.ok) {
            const records = await response.json();
            records.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${record.attendance_id}</td>
                    <td>${record.username}</td>
                    <td>${record.date}</td>
                    <td>${record.status}</td>
                    <td>${record.sick_note ? record.sick_note.status : 'N/A'}</td>`;
                hrAttendanceRecordsElement.appendChild(row);
            });
        } else {
            hrAttendanceRecordsElement.innerHTML = '<tr><td colspan="5">No records found.</td></tr>';
        }
    } catch (error) {
        console.error('Error filtering HR attendance records:', error);
    }
}

// Fetch Pending Sick Notes
async function fetchPendingSickNotes() {
    try {
        const response = await fetch("/attendance/hr/sick-notes/pending", {
            headers: { "Authorization": `Bearer ${token}` },
        });

        const sickNotesContainer = document.getElementById("pending-sick-notes");
        sickNotesContainer.innerHTML = "";

        if (!response.ok) {
            sickNotesContainer.innerHTML = "<p>No pending sick notes.</p>";
            return;
        }

        const data = await response.json();
        data.pending_sick_notes.forEach(note => {
            const sickNoteCard = document.createElement("div");
            sickNoteCard.classList.add("sick-note-card");

            sickNoteCard.innerHTML = `
                <p><strong>Username:</strong> ${note.username}</p>
                <p><strong>Date:</strong> ${note.date}</p>
                <p><strong>Reason:</strong> ${note.reason}</p>
                <p><strong>Status:</strong> ${note.status}</p>
                <p><strong>Submitted At:</strong> ${note.submitted_at}</p>
                <p><strong>File:</strong> <a href="/uploads/${note.file_name}" target="_blank">View File</a></p>
                <button onclick="approveSickNote('${note.attendance_id}')">Approve</button>
                <button onclick="rejectSickNote('${note.attendance_id}')">Reject</button>
            `;

            sickNotesContainer.appendChild(sickNoteCard);
        });
    } catch (error) {
        console.error("Error fetching pending sick notes:", error);
    }
}

// Approve sick note
async function approveSickNote(attendanceId) {
    const formData = new FormData();
    formData.append('status', 'Accepted');
    formData.append('review_comments', 'Approved by HR');

    try {
        const response = await fetch(`/attendance/hr/sick-note/${attendanceId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
            body: formData
        });

        if (response.ok) {
            showModal('Sick Note Approved Successfully!', 'success'); // Success message
            fetchHRAttendanceRecords();
        } else {
            showModal('Failed to Approve Sick Note !', 'failure'); // Handle failure
        }
    } catch (error) {
        console.error('Error approving sick note:', error);
        alert('An error occurred while approving the sick note.');
    }
}

// Reject sick note
async function rejectSickNote(attendanceId) {
    // Open modal
    document.getElementById("reviewModal").style.display = "block";

    // Handle modal submission
    document.getElementById("submitReview").onclick = async function () {
        const reviewComments = document.getElementById("reviewComments").value.trim();
        const reason = document.getElementById("reason").value.trim();

        if (!reviewComments || !reason) {
            alert("Please enter both reason and review comments.");
            return;
        }

        const formData = new FormData();
        formData.append('status', 'Rejected');
        formData.append('review_comments', reviewComments);
        formData.append('reason', reason);

        try {
            const response = await fetch(`/attendance/hr/sick-note/${attendanceId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData
            });

            if (response.ok) {
                showModal('Sick Note Rejected Successfully!', 'success'); 
                fetchHRAttendanceRecords(); 
            } else {
                showModal('Failed to Reject Sick Note!', 'failure'); 
            }
        } catch (error) {
            console.error('Error rejecting sick note:', error);
            alert('An error occurred while rejecting the sick note.');
        }

        // Close modal after submission
        document.getElementById("reviewModal").style.display = "none";
    };

    // Handle modal cancellation
    document.getElementById("closeModal").onclick = function () {
        document.getElementById("reviewModal").style.display = "none";
    };
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



// Initially Hide Sections
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("attendanceSection").style.display = "none";
    document.getElementById("sickNotesSection").style.display = "none";
});