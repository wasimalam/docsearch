document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const requestData = {
        username: username,
        password: password
    };

    fetch('/api/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.msg) {
            document.getElementById('message').textContent = 'Login successful!';
            document.getElementById('message').className = 'message success';
            // Redirect to another page with the token as a URL parameter
            window.location.href = `search`;
            // Store the token or use it as needed
        } else {
            throw new Error(data.detail || 'Login failed');
        }
    })
    .catch(error => {
        document.getElementById('message').textContent = error.message;
        document.getElementById('message').className = 'message error';
    });
});