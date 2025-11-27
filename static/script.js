// InnerTube API - Interactive JavaScript

// Update endpoint example URL
function updateEndpointExample() {
    const select = document.getElementById('endpoint-select');
    const urlInput = document.getElementById('api-url');
    const baseUrl = window.location.origin;

    urlInput.value = baseUrl + select.value;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    updateEndpointExample();
});

// Test API endpoint
async function testEndpoint() {
    const urlInput = document.getElementById('api-url');
    const responseOutput = document.getElementById('response-output');
    const url = urlInput.value;

    // Show loading state
    responseOutput.innerHTML = '<code>Loading...</code>';

    try {
        const response = await fetch(url);
        const data = await response.json();

        // Pretty print JSON
        const formatted = JSON.stringify(data, null, 2);
        responseOutput.innerHTML = `<code>${escapeHtml(formatted)}</code>`;

        // Add success animation
        responseOutput.style.animation = 'fadeIn 0.5s ease';

    } catch (error) {
        responseOutput.innerHTML = `<code style="color: #ff6b6b;">Error: ${escapeHtml(error.message)}</code>`;
    }
}

// Copy code to clipboard
function copyCode(button, elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;

    navigator.clipboard.writeText(text).then(() => {
        // Show feedback
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.style.background = '#4ade80';

        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Escape HTML for safe display
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add smooth scrolling
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

// Add fade-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeIn 0.8s ease forwards';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all feature cards and sections
document.addEventListener('DOMContentLoaded', () => {
    const elements = document.querySelectorAll('.feature-card, .code-block, .stat-card');
    elements.forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
});
