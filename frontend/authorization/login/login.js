document.getElementById('login-form').addEventListener('submit', async (event) => {
  event.preventDefault(); // Prevent default form submission

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const errorMessage = document.getElementById('error-message');

  try {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token); // Save token for future requests

      // Decode role from token payload
      const payload = JSON.parse(atob(data.access_token.split('.')[1]));
      const role = payload.role; // Get the role (employee or hr)

      // Redirect based on role
      if (role === 'employee') {
        window.location.href = '/../frontend/employee/portal/portal.html';
      } else if (role === 'hr') {
        window.location.href = '/../frontend/hr/portal/portal.html';
      } else {
        throw new Error('Invalid role');
      }
    } else {
      const errorData = await response.json();
      errorMessage.textContent = errorData.detail || 'Login failed.';
    }
  } catch (error) {
    console.error('Error during login:', error);
    errorMessage.textContent = 'An error occurred. Please try again.';
  }
});