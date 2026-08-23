document.addEventListener('DOMContentLoaded', () => {
    // Determine current theme from localStorage
    const savedTheme = localStorage.getItem('colab-theme');
    const isMiniMode = document.body.classList.contains('mini-mode');
    
    // Default to bright if nothing saved
    if (savedTheme === 'tropical') {
        document.body.classList.add('theme-tropical');
    }

    // Only add toggle button if we are not in mini-mode
    if (!isMiniMode) {
        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'theme-toggle-btn';
        toggleBtn.className = 'theme-toggle';
        
        function updateBtnUI() {
            if (document.body.classList.contains('theme-tropical')) {
                toggleBtn.innerHTML = '🌴 Tropical';
            } else {
                toggleBtn.innerHTML = '<img src="../arai-icon.svg" class="toggle-icon" alt="Arai-eek Face"> Arai-eek';
            }
        }
        
        updateBtnUI();

        toggleBtn.addEventListener('click', () => {
            document.body.classList.toggle('theme-tropical');
            
            if (document.body.classList.contains('theme-tropical')) {
                localStorage.setItem('colab-theme', 'tropical');
            } else {
                localStorage.setItem('colab-theme', 'bright');
            }
            
            updateBtnUI();
        });

        document.body.appendChild(toggleBtn);
    }
});
