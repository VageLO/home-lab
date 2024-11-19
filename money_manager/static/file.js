const files = async() => {
    response = await fetch(`${location.origin}/money-manager/projects/list`, {
        method: 'GET',
    })
    console.log(await response.json(), response)
}

files()

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

    response = await fetch(`${location.origin}/money-manager/projects/upload`, {
        method: 'POST',
        body: formData,
    })
    response = await response.json();
    console.log(response)
    //alert(response.message);
}
