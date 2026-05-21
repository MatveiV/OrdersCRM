export function initAnimatedBackground() {
    const container = document.getElementById('animated-bg');
    if (!container) return;

    const isMobile = window.innerWidth < 768;
    const particleCount = isMobile ? 15 : 30;

    for (let i = 0; i < particleCount; i++) {
        createParticle(container, isMobile);
    }
}

function createParticle(container, isMobile) {
    const particle = document.createElement('div');
    const isStar = Math.random() > 0.7;
    
    particle.className = `particle ${isStar ? 'star' : 'circle'}`;
    
    const size = isStar 
        ? Math.random() * 8 + 4 
        : Math.random() * 60 + 20;
    
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    particle.style.left = `${Math.random() * 100}%`;
    
    const duration = isMobile 
        ? Math.random() * 20 + 15 
        : Math.random() * 25 + 10;
    
    particle.style.animationDuration = `${duration}s`;
    particle.style.animationDelay = `${Math.random() * 10}s`;
    
    if (!isStar) {
        const opacity = Math.random() * 0.3 + 0.1;
        particle.style.opacity = opacity;
    }
    
    container.appendChild(particle);
}
