// Manejo de formularios de contacto
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('submitBtn');
            const submitText = document.getElementById('submitText');
            const submitLoading = document.getElementById('submitLoading');
            const formSuccess = document.getElementById('formSuccess');
            const formError = document.getElementById('formError');
            
            // Validación básica
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const subject = document.getElementById('subject').value;
            const message = document.getElementById('message').value.trim();
            
            if (!name || !email || !subject || !message) {
                showFormMessage('Por favor, completa todos los campos obligatorios.', 'error');
                return;
            }
            
            if (!validateEmail(email)) {
                showFormMessage('Por favor, ingresa un correo electrónico válido.', 'error');
                return;
            }
            
            // Mostrar loading
            submitText.style.display = 'none';
            submitLoading.style.display = 'inline';
            submitBtn.disabled = true;
            
            // Simular envío (en producción, aquí iría AJAX/Fetch)
            setTimeout(() => {
                // Simular éxito (90% de probabilidad)
                if (Math.random() > 0.1) {
                    showFormMessage('¡Mensaje enviado con éxito! Te contactaremos pronto.', 'success');
                    contactForm.reset();
                } else {
                    showFormMessage('Error al enviar el mensaje. Por favor, intenta nuevamente.', 'error');
                }
                
                // Restaurar botón
                submitText.style.display = 'inline';
                submitLoading.style.display = 'none';
                submitBtn.disabled = false;
            }, 2000);
        });
    }

    function showFormMessage(message, type) {
        const formSuccess = document.getElementById('formSuccess');
        const formError = document.getElementById('formError');
        
        if (type === 'success') {
            formSuccess.textContent = message;
            formSuccess.style.display = 'block';
            formError.style.display = 'none';
        } else {
            formError.textContent = message;
            formError.style.display = 'block';
            formSuccess.style.display = 'none';
        }
        
        // Ocultar mensajes después de 5 segundos
        setTimeout(() => {
            formSuccess.style.display = 'none';
            formError.style.display = 'none';
        }, 5000);
    }

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    // Formulario para unirse al equipo
    window.showJoinForm = function() {
        const name = prompt('¿Cuál es tu nombre completo?');
        if (name) {
            const email = prompt('¿Cuál es tu correo electrónico?');
            if (email) {
                if (!validateEmail(email)) {
                    alert('Por favor, ingresa un correo electrónico válido.');
                    return;
                }
                
                const motivation = prompt('¿Por qué te gustaría unirte a HGC & Asociados?');
                if (motivation) {
                    alert(`¡Gracias ${name}! Hemos recibido tu solicitud.\n\nTe contactaremos en ${email} dentro de las próximas 48 horas.`);
                    
                    // Aquí podrías enviar los datos a un servidor
                    console.log('Solicitud de unión:', { name, email, motivation });
                }
            }
        }
    };
});