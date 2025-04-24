// Credit Card Particles - Interactive Background Animation
class CardParticles {
    constructor(containerId, options = {}) {
        // Container for particles
        this.container = document.getElementById(containerId);
        if (!this.container) return;
        
        // Configuration options with defaults
        this.options = Object.assign({
            particleCount: Math.floor(Math.random() * 17) + 3,
            minSize: 40,
            maxSize: 160,
            minOpacity: 0.8,
            maxOpacity: 1.0,
            minSpeed: 0.7,
            maxSpeed: 1.5,
            cursorRepelRadius: 180,
            cursorRepelForce: 1.5,
            collisionDamping: 0.85,
            defaultImages: []
        }, options);
        
        // Initialize properties
        this.particles = [];
        this.mouseX = -1000;
        this.mouseY = -1000;
        this.isInitialized = false;
        
        // First load available card images
        this.loadCardImages()
            .then(() => {
                // Set up container
                this.setupContainer();
                
                // Create particles
                this.createParticles();
                
                // Set up event listeners
                this.setupEventListeners();
                
                // Start animation
                this.animate();
                
                this.isInitialized = true;
            });
    }
    
    // Load card images dynamically
    loadCardImages() {
        return new Promise((resolve) => {
            // If card images are provided in options, use those
            if (this.options.cardImages && this.options.cardImages.length > 0) {
                this.cardImages = this.options.cardImages;
                resolve();
                return;
            }
            
            // Otherwise, load a list of card images from our card images directory
            fetch('/static/card-list.json')
                .then(response => response.json())
                .then(images => {
                    this.cardImages = images.map(img => '/static/images/cards/' + img);
                    resolve();
                })
                .catch(() => {
                    // If we can't load the card list, create generic cards
                    console.log('Using generic card colors');
                    const colors = ['#1a73e8', '#ea4335', '#34a853', '#fbbc04', '#673ab7', '#ff6d00'];
                    this.cardImages = colors.map(color => `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='125' viewBox='0 0 200 125'%3E%3Crect width='200' height='125' rx='8' fill='${color.replace('#', '%23')}' /%3E%3C/svg%3E`);
                    resolve();
                });
        });
    }
    
    setupContainer() {
        // Ensure container has position relative for absolute positioning of particles
        if (getComputedStyle(this.container).position === 'static') {
            this.container.style.position = 'relative';
        }
        
        this.container.style.overflow = 'hidden';
        
        // Container dimensions
        this.width = this.container.offsetWidth;
        this.height = this.container.offsetHeight;
    }
    
    setupEventListeners() {
        // Track mouse movement
        document.addEventListener('mousemove', (e) => {
            const rect = this.container.getBoundingClientRect();
            this.mouseX = e.clientX - rect.left;
            this.mouseY = e.clientY - rect.top;
        });
        
        // Reset mouse position when cursor leaves container
        document.addEventListener('mouseleave', () => {
            this.mouseX = -1000;
            this.mouseY = -1000;
        });
        
        // Handle window resize
        window.addEventListener('resize', () => {
            this.width = this.container.offsetWidth;
            this.height = this.container.offsetHeight;
            
            // Adjust particle positions if container size changes
            this.particles.forEach(particle => {
                particle.x = Math.min(particle.x, this.width - particle.width);
                particle.y = Math.min(particle.y, this.height - particle.height);
            });
        });
    }
    
    createParticles() {
        // Create specified number of particles
        for (let i = 0; i < this.options.particleCount; i++) {
            this.addParticle();
        }
    }
    
    addParticle() {
        if (!this.cardImages || this.cardImages.length === 0) {
            return; // Don't create particles if we don't have images
        }
        
        // Random size within range
        const size = Math.random() * (this.options.maxSize - this.options.minSize) + this.options.minSize;
        const width = size;
        const height = size * 0.63; // Typical card aspect ratio
        
        // Random position within container - ensure cards are fully within view
        const x = Math.random() * (this.width - width);
        const y = Math.random() * (this.height - height);
        
        // Random velocities - more substantial initial movement
        const vx = (Math.random() * 2 - 1) * this.options.maxSpeed;
        const vy = (Math.random() * 2 - 1) * this.options.maxSpeed;
        
        // Random opacity within range - now more solid
        const opacity = Math.random() * (this.options.maxOpacity - this.options.minOpacity) + this.options.minOpacity;
        
        // Random image from available card images
        const imageUrl = this.cardImages[Math.floor(Math.random() * this.cardImages.length)];
        
        // Random rotation
        const rotation = Math.random() * 360;
        
        // Create particle element
        const element = document.createElement('div');
        element.className = 'card-particle';
        element.style.position = 'absolute';
        element.style.left = `${x}px`;
        element.style.top = `${y}px`;
        element.style.width = `${width}px`;
        element.style.height = `${height}px`;
        element.style.backgroundImage = `url(${imageUrl})`;
        element.style.backgroundSize = 'cover';
        element.style.backgroundPosition = 'center';
        element.style.opacity = opacity;
        element.style.transform = `rotate(${rotation}deg)`;
        element.style.pointerEvents = 'none';
        element.style.zIndex = '1';
        element.style.borderRadius = '8px';
        element.style.boxShadow = 'none'; // Remove shadow
        
        // Add to container
        this.container.appendChild(element);
        
        // Add to particles array with more physics properties
        this.particles.push({
            element,
            x,
            y,
            vx,
            vy,
            width,
            height,
            opacity,
            rotation,
            rotationSpeed: (Math.random() * 2 - 1) * 1.5, // Increased rotation speed
            // Add mass based on size for collision physics
            mass: width * height / 1000,
            // Add elasticity for more dynamic collisions
            elasticity: 0.8 + Math.random() * 0.2
        });
    }
    
    removeParticle(particle) {
        // Fade out and remove
        particle.element.style.opacity = '0';
        particle.element.style.transition = 'opacity 0.5s';
        
        // Remove from DOM and particles array after fade out
        setTimeout(() => {
            if (particle.element.parentNode) {
                particle.element.parentNode.removeChild(particle.element);
            }
            this.particles = this.particles.filter(p => p !== particle);
            
            // Add new particle to replace the removed one
            if (this.isInitialized) {
                this.addParticle();
            }
        }, 500);
    }
    
    checkCollision(p1, p2) {
        // Calculate center positions
        const p1CenterX = p1.x + p1.width / 2;
        const p1CenterY = p1.y + p1.height / 2;
        const p2CenterX = p2.x + p2.width / 2;
        const p2CenterY = p2.y + p2.height / 2;
        
        // Calculate distance between centers
        const dx = p2CenterX - p1CenterX;
        const dy = p2CenterY - p1CenterY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        // Minimum distance before collision (average of the two particles' sizes)
        const minDistance = (Math.max(p1.width, p1.height) + Math.max(p2.width, p2.height)) / 2.2; // Adjusted for more accurate collisions
        
        // Check if collision occurred
        if (distance < minDistance) {
            // Calculate collision normal
            const nx = dx / distance;
            const ny = dy / distance;
            
            // Calculate relative velocity
            const vx = p2.vx - p1.vx;
            const vy = p2.vy - p1.vy;
            
            // Calculate relative velocity in terms of normal direction
            const velocityAlongNormal = vx * nx + vy * ny;
            
            // Do not resolve if velocities are separating
            if (velocityAlongNormal > 0) return;
            
            // Calculate restitution (bounciness) - use average of both particles' elasticity
            const restitution = (p1.elasticity + p2.elasticity) / 2;
            
            // Calculate impulse scalar
            let impulseScalar = -(1 + restitution) * velocityAlongNormal;
            impulseScalar /= 1/p1.mass + 1/p2.mass;
            
            // Apply impulse
            const impulseX = impulseScalar * nx;
            const impulseY = impulseScalar * ny;
            
            p1.vx -= impulseX / p1.mass;
            p1.vy -= impulseY / p1.mass;
            p2.vx += impulseX / p2.mass;
            p2.vy += impulseY / p2.mass;
            
            // Add a substantial random rotation for visual effect
            p1.rotationSpeed += (Math.random() - 0.5) * 2;
            p2.rotationSpeed += (Math.random() - 0.5) * 2;
            
            // Prevent particles from sticking by separating them slightly
            const overlap = minDistance - distance;
            const separationX = overlap * nx * 0.6; // More separation
            const separationY = overlap * ny * 0.6; // More separation
            
            p1.x -= separationX;
            p1.y -= separationY;
            p2.x += separationX;
            p2.y += separationY;
        }
    }
    
    updateParticles() {
        // Update each particle
        this.particles.forEach((particle, i) => {
            // Apply physics - cursor repulsion (stronger effect)
            const dx = particle.x + particle.width/2 - this.mouseX;
            const dy = particle.y + particle.height/2 - this.mouseY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            // Check if cursor is within repel radius - stronger repulsion
            if (distance < this.options.cursorRepelRadius) {
                // Calculate repulsion force (stronger when closer)
                const force = (this.options.cursorRepelRadius - distance) / this.options.cursorRepelRadius * this.options.cursorRepelForce * 2;
                
                // Apply force to velocity
                particle.vx += (dx / distance) * force;
                particle.vy += (dy / distance) * force;
                
                // Add a small "bonk" effect - slight rotation change
                particle.rotationSpeed += (Math.random() * 2 - 1) * 1.0;
            }
            
            // Check for collisions with other particles
            for (let j = i + 1; j < this.particles.length; j++) {
                this.checkCollision(particle, this.particles[j]);
            }
            
            // Update position based on velocity
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.rotation += particle.rotationSpeed;
            
            // Dampen velocity and rotation for stability (less damping for more movement)
            particle.vx *= 0.99;
            particle.vy *= 0.99;
            particle.rotationSpeed *= 0.97;
            
            // Boundary checks - bounce off edges with higher energy
            if (particle.x < 0) {
                particle.x = 0;
                particle.vx = Math.abs(particle.vx) * 0.9;
            } else if (particle.x > this.width - particle.width) {
                particle.x = this.width - particle.width;
                particle.vx = -Math.abs(particle.vx) * 0.9;
            }
            
            if (particle.y < 0) {
                particle.y = 0;
                particle.vy = Math.abs(particle.vy) * 0.9;
            } else if (particle.y > this.height - particle.height) {
                particle.y = this.height - particle.height;
                particle.vy = -Math.abs(particle.vy) * 0.9;
            }
            
            // Update element position and rotation - use direct left/top instead of transform for better positioning
            particle.element.style.left = `${particle.x}px`;
            particle.element.style.top = `${particle.y}px`;
            particle.element.style.transform = `rotate(${particle.rotation}deg)`;
        });
    }
    
    animate() {
        // Update particle positions
        this.updateParticles();
        
        // Request next frame
        requestAnimationFrame(() => this.animate());
    }
    
    // Method to trigger a fade out animation
    flyOff() {
        this.particles.forEach(particle => {
            // Just fade out gradually
            particle.element.style.opacity = '0';
            particle.element.style.transition = 'opacity 0.8s ease-out';
        });
    }
    
    // Method to add new card images
    addCardImages(imageUrls) {
        if (Array.isArray(imageUrls) && imageUrls.length > 0) {
            this.cardImages = this.cardImages.concat(imageUrls);
        }
    }
}

// Initialize the particle system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // We'll initialize this from base2.html
}); 