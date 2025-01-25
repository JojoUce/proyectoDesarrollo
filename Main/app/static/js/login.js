// login.js

document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const nombre_usuario = document.getElementById('nombre_usuario').value;
    const contrasena = document.getElementById('contrasena').value;

    // Hacer una solicitud POST al backend
    fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            nombre_usuario: nombre_usuario,
            contrasena: contrasena,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error); 
        } else {
            alert(data.message); // Si el login es exitoso
            window.location.href = 'http://127.0.0.1:5500/Main/app/static/index.html';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Hubo un error al procesar el login');
    });
});
