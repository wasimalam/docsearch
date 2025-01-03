if(document.getElementById('logout')) {
    document.getElementById('logout').addEventListener('click', function(event) {
        event.preventDefault();
        localStorage.removeItem('jwt_token');
        logout();
    });
}

if(document.getElementById('login')) {
    document.getElementById('login').addEventListener('click', function(event) {
        window.location.href = "/";
    });
}

function convertToLocalDateTime(isoString) {
    // Create a new Date object from the ISO string
    const date = new Date(isoString);

    // Format the date and time as a local string
    const localDateTime = date.toLocaleString();

    return localDateTime;
}


document.addEventListener('DOMContentLoaded', function() {
    const profileButton = document.getElementById('profileButton');
    const dropdownMenu = document.getElementById('profile-dropdown');

    if(profileButton)
    {
        profileButton.addEventListener('click', function() {
            dropdownMenu.classList.toggle('show');
            });
            
            // Hide the dropdown if the user clicks outside of it
            window.addEventListener('click', function(event) {
                if (!profileButton.contains(event.target)) {
                    dropdownMenu.classList.remove('show');
                }
            });
    }

    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-icon');
    if(searchInput && searchButton) {
        // Handle the click event on the search button
        searchButton.addEventListener('click', () => {
            triggerSearch();
        });
        // Handle the "Enter" key press in the input field
        searchInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                triggerSearch();
            }
        });

        // Function to trigger the search
        function triggerSearch() {
            const query = searchInput.value.trim();
            if (query) {
                // Perform your search logic here (e.g., redirect, filter data, etc.)
                window.location.href = `/search?query=${query}`;
            } else {
                //alert('Please enter a search query.');
                window.location.href = "/search";
            }
        }
    }
});


function logout() {
    fetch('/api/logout', {
        method: 'POST',
        credentials: 'include' // Ensure cookies are included in the request
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Logged out successfully") {
            // Redirect the user to the login page or another route
            window.location.href = "/";
        }
    })
    .catch(error => console.error('Error:', error));
}