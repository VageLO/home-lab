const html = document.documentElement;
const toggleButton = document.getElementById('theme-toggle');

function updateButtonText() {
    if (html.classList.contains('dark')) {
        toggleButton.textContent = '🌙';
    } else {
        toggleButton.textContent = '💡';
    }
}

// Check for saved theme preference or use light by default
if (localStorage.getItem('theme') === 'dark') {
    html.classList.add('dark');
}

updateButtonText();

// Toggle theme on button click
toggleButton.addEventListener('click', () => {
    if (html.classList.contains('dark')) {
        html.classList.remove('dark');
        localStorage.setItem('theme', 'light');
    } else {
        html.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    }
    updateButtonText()
});
