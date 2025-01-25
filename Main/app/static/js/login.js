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
            'Accept': 'application/json',  // Asegúrate de que aceptas JSON
        },
        body: JSON.stringify({
            nombre_usuario: nombre_usuario,
            contrasena: contrasena,
        }),
        credentials: 'include' // Necesario para incluir las cookies de sesión
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(data.message); // Si el login es exitoso
            window.location.href = 'index.html';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Hubo un error al procesar el login');
    });
    
});
