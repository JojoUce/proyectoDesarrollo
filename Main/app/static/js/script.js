// Función para alternar el sidebar entre colapsado y expandido
document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.querySelector(".toggle-btn"); // Botón para colapsar
    const sidebar = document.querySelector(".sidebar"); // Barra lateral

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("collapsed");
        });
    }
});
