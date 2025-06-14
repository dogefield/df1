// Performance monitoring
const performance = {
    marks: {},
    start: function(name) {
        this.marks[name] = performance.now();
    },
    end: function(name) {
        if (this.marks[name]) {
            const duration = performance.now() - this.marks[name];
            console.log(`${name} took ${duration.toFixed(2)}ms`);
            delete this.marks[name];
        }
    }
};

// Error handling
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    // You could send this to a logging service
});

// Page load optimization
document.addEventListener('DOMContentLoaded', function() {
    performance.start('pageLoad');
    
    // Lazy load images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Add loading states to links
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', function(e) {
            if (!this.classList.contains('no-loading')) {
                document.body.classList.add('loading');
            }
        });
    });

    performance.end('pageLoad');
});

// Cache management
const cache = {
    set: function(key, value, ttl = 3600) {
        const item = {
            value: value,
            expiry: Date.now() + (ttl * 1000)
        };
        localStorage.setItem(key, JSON.stringify(item));
    },
    get: function(key) {
        const item = localStorage.getItem(key);
        if (!item) return null;
        
        const data = JSON.parse(item);
        if (Date.now() > data.expiry) {
            localStorage.removeItem(key);
            return null;
        }
        return data.value;
    }
}; 