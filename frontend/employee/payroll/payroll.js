document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const raiseMessage = document.getElementById('raise-message');
    const salaryElement = document.getElementById('salary');
    const benefitsElement = document.getElementById('benefits');
    const appraisalsElement = document.getElementById('appraisals');
    const penaltiesElement = document.getElementById('penalties');
    const raiseRequestsElement = document.getElementById('raise-requests');
    const raiseForm = document.getElementById('raise-form');
  

/**************************************************************************************************************/
// Fetch payroll details
// Read Endpoint {/payroll/get}

const fetchPayrollDetails = async () => {
    try {
        const response = await fetch('/payroll/get', {
            headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });

        if (response.ok) {
            const payroll = await response.json();

            // Display salary
            document.getElementById('salary').textContent = `$${payroll.salary.toLocaleString()}`;

            // Display benefits as a list
            const benefitsElement = document.getElementById('benefits');
            benefitsElement.innerHTML = '';
            payroll.benefits.forEach((benefit) => {
                const li = document.createElement('li');
                li.textContent = benefit;
                benefitsElement.appendChild(li);
            });

            // Display appraisals
            const appraisalsElement = document.getElementById('appraisals');
            appraisalsElement.innerHTML = '';
            payroll.appraisals.forEach((appraisal) => {
                const div = document.createElement('div');

                // Ensure date is valid, otherwise display default text
                let formattedDate = (appraisal.date && appraisal.date.trim() !== "")
                    ? new Date(appraisal.date).toLocaleDateString()
                    : "No Date Provided";

                div.textContent = `Amount: $${appraisal.amount} (Date: ${formattedDate})`;
                appraisalsElement.appendChild(div);
            });

            // Display penalties
            const penaltiesElement = document.getElementById('penalties');
            penaltiesElement.innerHTML = '';
            payroll.penalties.forEach((penalty) => {
                const div = document.createElement('div');
                div.textContent = `Amount: $${penalty.amount} - Reason: ${penalty.reason}`;
                penaltiesElement.appendChild(div);
            });

            // Display raise requests
            const raiseRequestsElement = document.getElementById('raise-requests');
            raiseRequestsElement.innerHTML = '';
            payroll.raise_requests.forEach((request) => {
                const row = document.createElement('tr');

                // Ensure `requested_at` is a valid ISO string, otherwise show "No Date Provided"
                let formattedRequestedAt = (request.requested_at && request.requested_at.trim() !== "")
                    ? new Date(request.requested_at).toLocaleString()
                    : "No Date Provided";

                row.innerHTML = `
                    <td>$${request.requested_amount.toLocaleString()}</td>
                    <td>${request.reason}</td>
                    <td>${request.status}</td>
                    <td>${formattedRequestedAt}</td>
                `;
                raiseRequestsElement.appendChild(row);
            });
        } else {
            document.getElementById('raise-message').textContent = 'Failed to load payroll details.';
        }
    } catch (error) {
        console.error('Error fetching payroll details:', error);
        document.getElementById('raise-message').textContent = 'An error occurred while fetching payroll details.';
    }
};
/**************************************************************************************************************/
// Submit raise request
// Read Endpoint {/payroll/raise-request}

raiseForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const requestedAmount = parseFloat(document.getElementById('requested-amount').value);
    const reason = document.getElementById('reason').value;
    const salary = parseFloat(salaryElement.textContent.replace(/[$,]/g, ''));

    console.log('Salary Element Content:', salaryElement.textContent);

    if (requestedAmount > salary * 0.1) {
        showModal('Requested amount cannot exceed 10% of your current salary.', false);
        return;
    }

    try {
        const response = await fetch('/payroll/raise-request', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ requested_amount: requestedAmount, reason }),
        });

        if (response.ok) {
            showModal('Raise request submitted successfully!', true);
            raiseForm.reset(); // Clear form fields
            fetchPayrollDetails(); // Refresh payroll details and raise history
        } else {
            showModal('Failed to submit raise request.', false);
        }
    } catch (error) {
        console.error('Error submitting raise request:', error);
        showModal('An error occurred while submitting your raise request.', false);
    }
});

// Initial fetch of payroll details
fetchPayrollDetails();
});

/**************************************************************************************************************/

function showModal(message, isSuccess = true) {
    const modal = document.getElementById('raiseModal');
    const modalMessage = document.getElementById('raise-modal-message');

    modalMessage.textContent = message;
    modal.style.backgroundColor = isSuccess ? '#28a745' : '#dc3545'; // Green for success, red for error
    modal.style.display = 'block';

    // Set timeout to fade out after 3 seconds
    setTimeout(() => {
        modal.classList.add('fade-out'); 
        setTimeout(() => {
            modal.style.display = 'none';
            modal.classList.remove('fade-out'); // Reset for next use
        }, 500); // Wait for fade-out transition
    }, 3000);
}