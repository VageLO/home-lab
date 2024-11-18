function handleFile() {
    const input = document.getElementById("filepicker");
    const file = input.files[0];
    if (file && file.name.split('.').pop() != 'db') {
        alert('Only database file allowed!');
    } else {
        uploadFile(file);
    }
    input.value = '';
}

async function uploadFile(file) {
    const formData  = new FormData();
        
    formData.append('file', file);

    response = await fetch(`${location.origin}/money-manager/project`, {
        method: 'POST',
        body: formData,
    })
    response = await response.json();
    alert(response.message);
}
