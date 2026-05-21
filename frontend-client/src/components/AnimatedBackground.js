export function initAnimatedBackground() {
    const container = document.getElementById('animated-bg');
    if (!container) return;
    
    const shapes = [];
    const shapeCount = 25;
    
    for (let i = 0; i < shapeCount; i++) {
        const shape = document.createElement('div');
        shape.classList.add('floating-shape');
        
        const isCircle = Math.random() > 0.5;
        shape.classList.add(isCircle ? 'circle' : 'star');
        
        const size = Math.random() * 20 + 8;
        shape.style.width = `${size}px`;
        shape.style.height = `${size}px`;
        shape.style.left = `${Math.random() * 100}%`;
        shape.style.top = `${Math.random() * 100}%`;
        shape.style.opacity = Math.random() * 0.15 + 0.05;
        
        const duration = Math.random() * 20 + 15;
        const delay = Math.random() * -20;
        shape.style.animation = `float ${duration}s ease-in-out ${delay}s infinite`;
        
        const isGold = Math.random() > 0.4;
        shape.style.background = isGold ? 'radial-gradient(circle, #D4AF37, transparent)' : 'radial-gradient(circle, #4A90D9, transparent)';
        
        container.appendChild(shape);
        shapes.push(shape);
    }
}
