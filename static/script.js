document.addEventListener('DOMContentLoaded', () => {
    const askForm = document.getElementById('ask-form');
    const uploadForm = document.getElementById('upload-form');
    const responseDiv = document.getElementById('response');
    const summaryDiv = document.getElementById('summary');

    askForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(askForm);

        fetch('/ask', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            responseDiv.innerHTML = `<h3>Response:</h3><p>${data.response}</p>`;
        })
        .catch(error => console.error('Error:', error));
    });

    uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(uploadForm);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            summaryDiv.innerHTML = `<h3>Summary:</h3><p>${data.summary}</p>`;
        })
        .catch(error => console.error('Error:', error));
    });
});
