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
// Función para mostrar mensajes flash
function showFlashMessage(message, category) {
    const flashContainer = document.getElementById('flash-messages');
    const messageElement = document.createElement('div');
    messageElement.className = `flash-message flash-${category}`;
    messageElement.textContent = message;
    flashContainer.appendChild(messageElement);

    // Eliminar el mensaje después de 3 segundos
    setTimeout(() => {
        messageElement.remove();
        // Si no hay más mensajes, eliminar el contenedor
        if (flashContainer.children.length === 0) {
            flashContainer.remove();
        }
    }, 3000);
}

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
            showFlashMessage(data.error, 'danger'); // Mostrar mensaje de error
        } else {
            showFlashMessage(data.message, 'success'); // Mostrar mensaje de éxito
            window.location.href = 'index.html'; // Redirigir al inicio
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('Hubo un error al procesar el login', 'danger'); // Mostrar mensaje de error
    });
});
