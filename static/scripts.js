// static/script.js
function toggleDropdown() {
    var dropdownContent = document.getElementById('dropdownContent');
    dropdownContent.style.display = (dropdownContent.style.display === 'block') ? 'none' : 'block';
}

function logout() {
    // Perform logout logic, e.g., redirect to a logout route
    window.location.href = '/logout';
}
