document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Evita el envío por defecto del formulario

    // Obtener los valores del formulario
    const nombreUsuario = document.getElementById('exampleFirstName').value;
    const email = document.getElementById('exampleInputEmail').value;
    const password = document.getElementById('exampleInputPassword').value;
    const edad = document.getElementById('edad').value;
    const altura = document.getElementById('altura').value;

    // Validar contraseñas
    const confirmPassword = document.getElementById('exampleRepeatPassword').value;
    if (password !== confirmPassword) {
        alert('Las contraseñas no coinciden.');
        return;
    }

    // Crear un objeto con los datos del formulario
    const formData = {
        nombre_usuario: nombreUsuario,
        correo_electronico: email,
        contrasena: password,  // Enviar la contraseña en texto sin procesar
        edad: edad,
        altura: altura
    };

    // Enviar la solicitud al backend usando AJAX
    fetch('http://localhost:5000/users', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert('Usuario creado exitosamente');
            window.location.href = 'login.html';  // Redirigir al login
        } else {
            alert('Error al crear usuario: ' + data.error);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Hubo un error al enviar los datos.');
    });
});