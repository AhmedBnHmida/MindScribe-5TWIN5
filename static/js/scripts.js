// MindScribe - Enhanced JavaScript with Interactive Brain Background
// Dynamic interactions, animations, and mouse-responsive brain particles

// Hero Carousel Functionality
function initHeroCarousel() {
    const carousel = document.querySelector('.hero-carousel');
    const slides = document.querySelectorAll('.carousel-slide');
    const prevBtn = document.querySelector('.carousel-control.prev');
    const nextBtn = document.querySelector('.carousel-control.next');
    const indicators = document.querySelectorAll('.indicator');
    
    if (!carousel || slides.length === 0) {
        console.log('Carousel elements not found');
        return;
    }
    
    let currentSlide = 0;
    let autoPlayInterval;
    
    // Function to show specific slide
    function showSlide(index) {
        console.log('Showing slide:', index);
        
        // Remove active class from all slides
        slides.forEach(slide => {
            slide.classList.remove('active', 'prev');
        });
        indicators.forEach(indicator => indicator.classList.remove('active'));
        
        // Add active class to current slide
        slides[index].classList.add('active');
        indicators[index].classList.add('active');
        
        currentSlide = index;
    }
    
    // Function to go to next slide
    function nextSlide() {
        const nextIndex = (currentSlide + 1) % slides.length;
        showSlide(nextIndex);
    }
    
    // Function to go to previous slide
    function prevSlide() {
        const prevIndex = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(prevIndex);
    }
    
    // Auto-play functionality
    function startAutoPlay() {
        autoPlayInterval = setInterval(nextSlide, 5000); // Change slide every 5 seconds
        console.log('Auto-play started');
    }
    
    function stopAutoPlay() {
        if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
            console.log('Auto-play stopped');
        }
    }
    
    // Event listeners
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            console.log('Next button clicked');
            nextSlide();
            stopAutoPlay();
            startAutoPlay();
        });
    }
    
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            console.log('Previous button clicked');
            prevSlide();
            stopAutoPlay();
            startAutoPlay();
        });
    }
    
    // Indicator clicks
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            console.log('Indicator clicked:', index);
            showSlide(index);
            stopAutoPlay();
            startAutoPlay();
        });
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            prevSlide();
            stopAutoPlay();
            startAutoPlay();
        } else if (e.key === 'ArrowRight') {
            nextSlide();
            stopAutoPlay();
            startAutoPlay();
        }
    });
    
    // Pause auto-play on hover
    if (carousel) {
        carousel.addEventListener('mouseenter', stopAutoPlay);
        carousel.addEventListener('mouseleave', startAutoPlay);
    }
    
    // Touch swipe support for mobile
    let touchStartX = 0;
    let touchEndX = 0;
    
    if (carousel) {
        carousel.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });
        
        carousel.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });
    }
    
    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe left - next slide
                nextSlide();
            } else {
                // Swipe right - previous slide
                prevSlide();
            }
            stopAutoPlay();
            startAutoPlay();
        }
    }
    
    // Initialize carousel
    showSlide(0);
    startAutoPlay();
    console.log('Carousel initialized with', slides.length, 'slides');
}

// Navbar scroll effect
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Animation on scroll
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.feature-card, .process-step, .testimonial-card, .pricing-card').forEach(el => {
        observer.observe(el);
    });
}

// Back to top button
function initBackToTop() {
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '<i class="fas fa-chevron-up"></i>';
    backToTop.className = 'btn btn-primary back-to-top';
    backToTop.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: none;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    `;
    document.body.appendChild(backToTop);

    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTop.style.display = 'block';
        } else {
            backToTop.style.display = 'none';
        }
    });
}

// Enhanced hover effects
function initHoverEffects() {
    document.querySelectorAll('.card-hover-lift').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });
}

// Mobile menu enhancement
function initMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });

        // Close mobile menu when clicking on a link
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            link.addEventListener('click', () => {
                if (navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        });
    }
}


// ========================================================================
// Universal Brain Background - For All Pages
// ========================================================================

function initUniversalBrainBackground(canvasId = 'brainCanvas', options = {}) {
    const canvas = document.getElementById(canvasId);
    
    if (!canvas) {
        console.log(`Canvas with ID "${canvasId}" not found on this page`);
        return null;
    }
    
    console.log(`Initializing brain background for: ${canvasId}`);
    
    const config = {
        // Default settings for all pages
        particleCount: 80,
        connectionDistance: 120,
        mouseRadius: 150,
        colors: [
            '95, 116, 169',    // Primary blue
            '255, 125, 125',   // Secondary coral  
            '58, 183, 149',    // Success green
            '100, 181, 246',   // Info blue
            '255, 183, 77'     // Warning orange
        ],
        particleSize: { min: 1, max: 3 },
        speed: { min: -0.3, max: 0.3 },
        alpha: { min: 0.2, max: 0.6 },
        // Override with custom options
        ...options
    };
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    let mouse = { x: 0, y: 0, radius: config.mouseRadius };
    let animationId = null;

    // Set canvas size
    function setCanvasSize() {
        if (canvasId === 'authBrainCanvas') {
            // Full screen for auth pages
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        } else {
            // Container-based for other pages
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
        }
        console.log(`Canvas "${canvasId}" size: ${canvas.width}x${canvas.height}`);
    }

    // Mouse movement tracking
    function initMouseTracking() {
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            mouse.x = e.clientX - rect.left;
            mouse.y = e.clientY - rect.top;
        });
        
        canvas.addEventListener('mouseleave', () => {
            mouse.x = undefined;
            mouse.y = undefined;
        });
    }

    // Particle class
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * (config.particleSize.max - config.particleSize.min) + config.particleSize.min;
            this.speedX = Math.random() * (config.speed.max - config.speed.min) + config.speed.min;
            this.speedY = Math.random() * (config.speed.max - config.speed.min) + config.speed.min;
            this.color = config.colors[Math.floor(Math.random() * config.colors.length)];
            this.alpha = Math.random() * (config.alpha.max - config.alpha.min) + config.alpha.min;
            this.originalAlpha = this.alpha;
        }
        
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            
            // Bounce off walls with energy preservation
            if (this.x > canvas.width || this.x < 0) {
                this.speedX = -this.speedX * 0.95;
            }
            if (this.y > canvas.height || this.y < 0) {
                this.speedY = -this.speedY * 0.95;
            }
            
            // Mouse interaction
            if (mouse.x && mouse.y) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < mouse.radius) {
                    const force = (mouse.radius - distance) / mouse.radius;
                    this.speedX -= dx * force * 0.02;
                    this.speedY -= dy * force * 0.02;
                    this.alpha = Math.min(1, this.originalAlpha + force * 0.5);
                } else {
                    this.alpha = this.originalAlpha;
                }
            }
        }
        
        draw() {
            ctx.save();
            ctx.globalAlpha = this.alpha;
            ctx.fillStyle = `rgb(${this.color})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    // Create particles
    function initParticles() {
        particles = [];
        const particleCount = Math.min(config.particleCount, Math.floor((canvas.width * canvas.height) / 3000));
        
        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }
        console.log(`Created ${particleCount} particles for ${canvasId}`);
    }

    // Draw neural connections
    function drawConnections() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < config.connectionDistance) {
                    const opacity = 1 - distance / config.connectionDistance;
                    ctx.save();
                    ctx.globalAlpha = opacity * 0.15;
                    ctx.strokeStyle = `rgb(95, 116, 169)`;
                    ctx.lineWidth = 0.3;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                    ctx.restore();
                }
            }
        }
    }

    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        drawConnections();
        animationId = requestAnimationFrame(animate);
    }

    // Initialize everything
    function init() {
        setCanvasSize();
        initMouseTracking();
        initParticles();
        animate();
        
        // Handle resize
        window.addEventListener('resize', () => {
            setCanvasSize();
            initParticles();
        });
        
        console.log(`Brain background "${canvasId}" initialized successfully`);
    }

    // Cleanup function
    function destroy() {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
        console.log(`Brain background "${canvasId}" destroyed`);
    }

    // Start the animation
    init();
    
    // Return cleanup function
    return destroy;
}

// ========================================================================
// Page-Specific Initialization
// ========================================================================

function initPageSpecificBrainBackgrounds() {
    // Check for different canvas IDs and initialize accordingly
    
    // For main pages (landing, home, etc.)
    if (document.getElementById('brainCanvas')) {
        initUniversalBrainBackground('brainCanvas', {
            particleCount: 120,
            connectionDistance: 150
        });
    }
    
    // For authentication pages (login, register)
    if (document.getElementById('authBrainCanvas')) {
        initUniversalBrainBackground('authBrainCanvas', {
            particleCount: 60,
            connectionDistance: 100,
            alpha: { min: 0.1, max: 0.4 }
        });
    }
    
    // For dashboard or other pages
    if (document.getElementById('dashboardBrainCanvas')) {
        initUniversalBrainBackground('dashboardBrainCanvas', {
            particleCount: 40,
            connectionDistance: 80
        });
    }
}

// ========================================================================
// Main Initialization - Universal
// ========================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    console.log('MindScribe - Initializing all components...');
    
    // Initialize all universal components
    initHeroCarousel();
    initNavbarScroll();
    initSmoothScrolling();
    initScrollAnimations();
    initBackToTop();
    initHoverEffects();
    initMobileMenu();
    
    // Initialize brain backgrounds for current page
    initPageSpecificBrainBackgrounds();
    
    console.log('MindScribe enhanced scripts loaded successfully!');
});

// ========================================================================
// Export for global usage (if needed)
// ========================================================================

// Make function available globally
window.MindScribe = {
    initBrainBackground: initUniversalBrainBackground,
    initAllComponents: function() {
        initPageSpecificBrainBackgrounds();
    }
};