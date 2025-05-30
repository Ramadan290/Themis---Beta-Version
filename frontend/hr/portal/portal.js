
document.addEventListener('DOMContentLoaded', () => {
    // Decode the access token to get the username
    const token = localStorage.getItem('token');
    const usernameElement = document.getElementById('username');
  
    if (token) {
      try {
        // Decode the JWT token
        const payload = JSON.parse(atob(token.split('.')[1])); // Decode the payload
        const username = payload.sub; // 'sub' contains the username
        usernameElement.textContent = username;
      } catch (error) {
        console.error('Invalid token:', error);
        usernameElement.textContent = 'hr';
      }
    }
  
    // Add click events to boxes for navigation
    document.getElementById('payroll-box').addEventListener('click', () => {
      window.location.href = '/frontend/hr/payroll/payroll.html';
    });
  
    document.getElementById('attendance-box').addEventListener('click', () => {
      window.location.href = '/frontend/hr/attendance/attendance.html';
    });
  
    document.getElementById('news-box').addEventListener('click', () => {
      window.location.href = '/frontend/hr/news/news.html';
    });
  
    document.getElementById('status-box').addEventListener('click', () => {
      window.location.href = '/frontend/hr/status/hr_status.html';
    });
      
    document.getElementById('ai-box').addEventListener('click', () => {
      window.location.href = '/../frontend/ai_powered_analysis/Menu.html';
    });

  
    // Logout button functionality
    document.getElementById('logout-button').addEventListener('click', () => {
      localStorage.removeItem('token'); // Clear the access token
      window.location.href = '/frontend/authorization/login/login.html'; // Redirect to login page
    });
  });