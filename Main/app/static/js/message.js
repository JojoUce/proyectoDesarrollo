// message.js

// Función para mostrar el mensaje flash
function showFlashMessage(message, type) {
    const flashMessageElement = document.getElementById('flash-message');
    flashMessageElement.textContent = message;
    flashMessageElement.className = 'alert ' + type;  // Establecer el tipo de alerta (success, error)
    flashMessageElement.style.display = 'block'; // Mostrar el mensaje

    // Ocultar el mensaje después de 3 segundos
    setTimeout(() => {
        flashMessageElement.style.display = 'none';
    }, 3000);
}

// Mostrar un mensaje flash de ejemplo
// Esto puede ser llamado desde cualquier lugar en tu aplicación cuando lo necesites.
showFlashMessage('¡Bienvenido a la aplicación!', 'success');
