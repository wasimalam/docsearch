document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];
    if (!file) {
        document.getElementById('message').textContent = "Please select a file to upload.";
        document.getElementById('message').className = "error";
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/uploadfile', true);
    const token = localStorage.getItem('jwt_token');    
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                document.getElementById('message').textContent = "File uploaded successfully!";
                document.getElementById('message').className = "message";
            } else {
                document.getElementById('message').textContent = "File upload failed. Please try again.";
                document.getElementById('message').className = "error";
            }
        }
    };

    xhr.send(formData);
});

