// Add a subtle mouse follow effect to the glass container
document.addEventListener('mousemove', (e) => {
    const container = document.querySelector('.glass-container');
    if (!container) return;
    
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;
    
    // Very subtle tilt
    const tiltX = (y - 0.5) * 5; // max 2.5deg
    const tiltY = (x - 0.5) * -5;
    
    container.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
});

// Reset transform on mouse leave
document.addEventListener('mouseleave', () => {
    const container = document.querySelector('.glass-container');
    if (container) {
        container.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
    }
});
