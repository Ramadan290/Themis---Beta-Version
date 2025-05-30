
/*******************************ATTENDANCE FUNCTIONALITIES *************************************************/

document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const attendanceRecordsElement = document.getElementById('attendance-records');
    const logAttendanceButton = document.getElementById('log-attendance-button');
    const sickNoteForm = document.getElementById('sick-note-form');
    const sickNoteMessage = document.getElementById('sick-note-message');


/************************************** Log Attendance ***************************************/

//  Read Endpoint {attendance/log}

logAttendanceButton.addEventListener('click', async () => {
try {
    const response = await fetch('/attendance/log', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
    },
    });

    if (response.ok) {
    const data = await response.json();
    alert(`Attendance logged successfully for ${data.timestamp}`);
    fetchAttendanceRecords(); // Refresh the attendance records
    } else {
    alert('Failed to log attendance.');
    }
} catch (error) {
    console.error('Error logging attendance:', error);
}
});

/******************************* Fetch Attendance for specific Employee *****************************/

//  Read Endpoint {attendance/log/{username}}

const fetchAttendanceRecords = async () => {
try {
    const username = JSON.parse(atob(token.split('.')[1])).sub; // Extract username from token
    const response = await fetch(`/attendance/${username}`, {
    headers: {
        'Authorization': `Bearer ${token}`,
    },
    });

    if (response.ok) {
    const records = await response.json();
    attendanceRecordsElement.innerHTML = ''; // Clear existing rows

    records.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
        <td>${record.attendance_id}</td>
        <td>${record.date}</td>
        <td>${record.status}</td>
        <td>${record.sick_note.status}</td>
        `;
        attendanceRecordsElement.appendChild(row);
    });
    } else {
    attendanceRecordsElement.innerHTML = '<tr><td colspan="4">No attendance records found.</td></tr>';
    }
} catch (error) {
    console.error('Error fetching attendance records:', error);
}
};


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
/******************************* Submit sick note Employee *****************************/

//  Read Endpoint {attendance/sick-note/}

sickNoteForm.addEventListener('submit', async (event) => {
    event.preventDefault(); // Prevent form submission

    const formData = new FormData(sickNoteForm);
    const attendanceId = formData.get('attendance-id');
    formData.delete('attendance-id'); // Remove ID from body since it's part of the URL

    try {
        const response = await fetch(`/attendance/sick-note/${attendanceId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
            body: formData,
        });

        if (response.ok) {
            sickNoteForm.reset(); // Clear the form fields
            showModal('Sick note submitted successfully!', 'success'); // Success message
            fetchAttendanceRecords(); // Refresh records
        } else {
            showModal('Failed to submit sick note.', 'error'); // Error message
        }
    } catch (error) {
        console.error('Error submitting sick note:', error);
        showModal('An error occurred. Please try again.', 'error'); // Error message
    }
});
// Initial Fetch of Attendance Records
fetchAttendanceRecords();
});


