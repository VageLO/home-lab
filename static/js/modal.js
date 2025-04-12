function modal_for_table() {
    const modal = document.getElementById('myDialog');
    const modalTitle = document.getElementById('modalTitle');
    const modalContent = document.getElementById('modalContent');
    const closeButton = document.getElementById('closeDialog');

    document.querySelectorAll('.row').forEach(row => {
        row.addEventListener('click', function() {
            const item = JSON.parse(this.dataset.item);
            console.log(item)
            modalTitle.textContent = "Edit Transaction";
            modalContent.innerHTML = `
                <p class="text-gray-800 mb-4">${item.transaction.date}</p>
            `;
            
            modal.classList.remove('hidden');
        });
    });

    closeButton.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    // Close modal if clicking outside of it
    window.addEventListener('click', function(event) {
        if (event.target === modal)
            modal.classList.add('hidden');
    });
}
