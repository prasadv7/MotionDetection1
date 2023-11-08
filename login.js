document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent default form submission

    // Validate ID and password (add your custom validation logic)
    const teacherID = document.getElementById('teacherID').value;
    const password = document.getElementById('password').value;

    // Here you can implement your logic to check credentials
    if (teacherID === '12345' && password === '12345') {
        // Credentials are correct, redirect to the dashboard
        window.location.href = 'index.html'; // Redirect to your dashboard
    } else {
        // Incorrect credentials, show an error message or handle accordingly
        alert('Invalid credentials. Please try again.');
    }
});
