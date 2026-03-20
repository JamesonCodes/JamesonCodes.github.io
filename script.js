// Dark Mode Toggle
const themeToggleBtn = document.getElementById('theme-toggle');
const htmlElement = document.documentElement;
const darkIcon = document.getElementById('theme-toggle-dark-icon');
const lightIcon = document.getElementById('theme-toggle-light-icon');

// Check for saved theme preference or default to dark mode
const currentTheme = localStorage.getItem('theme') || 'dark';

// Set initial theme
if (currentTheme === 'dark') {
    htmlElement.classList.add('dark');
    darkIcon.classList.remove('hidden');
} else {
    htmlElement.classList.remove('dark');
    lightIcon.classList.remove('hidden');
}

// Toggle theme
themeToggleBtn.addEventListener('click', () => {
    if (htmlElement.classList.contains('dark')) {
        htmlElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
        darkIcon.classList.add('hidden');
        lightIcon.classList.remove('hidden');
    } else {
        htmlElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
        lightIcon.classList.add('hidden');
        darkIcon.classList.remove('hidden');
    }
    window.dispatchEvent(new CustomEvent('theme:changed'));
});

// Mobile Menu Toggle
const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');

function openMobileMenu() {
    mobileMenu.classList.remove('hidden');
    mobileMenu.classList.add('menu-enter');
    mobileMenuButton.setAttribute('aria-expanded', 'true');
    mobileMenu.setAttribute('aria-hidden', 'false');
    requestAnimationFrame(() => {
        mobileMenu.classList.add('menu-enter-active');
        mobileMenu.classList.remove('menu-enter');
    });
}

function closeMobileMenu() {
    mobileMenu.classList.add('menu-enter');
    mobileMenu.classList.remove('menu-enter-active');
    mobileMenuButton.setAttribute('aria-expanded', 'false');
    mobileMenu.setAttribute('aria-hidden', 'true');
    setTimeout(() => {
        mobileMenu.classList.add('hidden');
        mobileMenu.classList.remove('menu-enter');
    }, 180);
}

mobileMenuButton.addEventListener('click', () => {
    const isHidden = mobileMenu.classList.contains('hidden');
    if (isHidden) {
        openMobileMenu();
    } else {
        closeMobileMenu();
    }
});

// Close mobile menu when clicking a link
const mobileMenuLinks = document.querySelectorAll('#mobile-menu a');
mobileMenuLinks.forEach(link => {
    link.addEventListener('click', () => {
        closeMobileMenu();
    });
});

// Smooth Scrolling for Navigation Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offsetTop = target.offsetTop - 80; // Account for fixed navbar
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// Fade-in Animation on Scroll using Intersection Observer
const observerOptions = {
    root: null,
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

// Observe all elements with fade-in class
const fadeInElements = document.querySelectorAll('.fade-in');
fadeInElements.forEach(element => {
    observer.observe(element);
});

// Navbar Shadow on Scroll
const navbar = document.getElementById('navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    // Add shadow when scrolled
    if (currentScroll > 50) {
        navbar.classList.add('navbar-scrolled');
    } else {
        navbar.classList.remove('navbar-scrolled');
    }
    
    lastScroll = currentScroll;
});

// Active Section Highlighting in Navigation
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');
const navLinksMobile = document.querySelectorAll('.nav-link-mobile');

function highlightNavigation() {
    const scrollPosition = window.pageYOffset + 100;
    let activeHref = null;

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            activeHref = `#${sectionId}`;
        }
    });

    navLinks.forEach(link => {
        link.classList.toggle('active', link.getAttribute('href') === activeHref);
    });
    navLinksMobile.forEach(link => {
        link.classList.toggle('active', link.getAttribute('href') === activeHref);
    });
}

window.addEventListener('scroll', highlightNavigation);

// Initial call to set active section on page load
highlightNavigation();

// Prevent FOUC (Flash of Unstyled Content) on page load
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});

// Console Easter Egg for fellow developers
console.log('%c👋 Hey there, fellow builder!', 'font-size: 20px; font-weight: bold; color: #171717;');
console.log('%cIf you\'re curious about how this site was built, check out the source on GitHub!', 'font-size: 14px; color: #666;');
console.log('%chttps://github.com/JamesonCodes/JamesonCodes.github.io', 'font-size: 14px; color: #52525b; text-decoration: underline;');

// Performance: Debounce scroll events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply debounce to scroll-heavy functions
const debouncedHighlight = debounce(highlightNavigation, 100);
window.removeEventListener('scroll', highlightNavigation);
window.addEventListener('scroll', debouncedHighlight);

