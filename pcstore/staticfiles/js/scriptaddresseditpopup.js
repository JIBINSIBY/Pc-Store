function togglePopup() {
    const popup = document.getElementById('popup');
    if (popup.classList.contains('hidden')) {
        popup.classList.remove('hidden');
    } else {
        popup.classList.add('hidden');
    }
}

// Close the popup if clicked outside of it
document.addEventListener('click', function(event) {
    const icon = document.querySelector('.icon');
    const popup = document.getElementById('popup');
    if (!icon.contains(event.target) && !popup.contains(event.target)) {
        popup.classList.add('hidden');
    }
});
