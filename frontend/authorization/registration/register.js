document.getElementById('register-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const errorMessage = document.getElementById('error-message');
  
    if (password !== confirmPassword) {
      errorMessage.textContent = "Passwords do not match!";
      return;
    }
  
    try {
      const response = await fetch('/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });
  
      if (response.ok) {
        alert('Registration successful! Redirecting to login...');
        window.location.href = '/frontend/authorization/login/login.html';
      } else {
        const error = await response.json();
        errorMessage.textContent = error.detail || 'Registration failed.';
      }
    } catch (error) {
      errorMessage.textContent = 'An error occurred. Please try again.';
    }
  });