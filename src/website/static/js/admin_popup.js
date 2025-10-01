document.addEventListener('DOMContentLoaded', function() {
    const popupOverlay = document.createElement('div');
    popupOverlay.id = 'popup-overlay';
    popupOverlay.className = 'popup-overlay';
    popupOverlay.innerHTML = `
        <div class="popup-content">
            <span class="popup-close">&times;</span>
            <h2 id="popup-title"></h2>
            <p id="popup-text"></p>
        </div>
    `;
    document.body.appendChild(popupOverlay);

    const popupLinks = document.querySelectorAll('.popup-link');
    const popup = document.getElementById('popup-overlay');
    const popupTitle = document.getElementById('popup-title');
    const popupText = document.getElementById('popup-text');
    const closePopup = document.querySelector('.popup-close');

    popupLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            popupTitle.textContent = this.getAttribute('data-title');
            popupText.textContent = this.getAttribute('data-content');
            popup.style.display = 'flex';
        });
    });

    closePopup.addEventListener('click', function() {
        popup.style.display = 'none';
    });

    popupOverlay.addEventListener('click', function(e) {
        if (e.target === popupOverlay) {
            popup.style.display = 'none';
        }
    });
});