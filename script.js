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

// Circuit routes remap between safe, grid-aligned paths after each completed pass.
// The constrained route library keeps the motion exploratory without crossing hero copy.
const circuitRouteOptions = {
    left: [
        [[20, 180], [100, 180], [100, 260], [180, 260], [180, 340]],
        [[20, 100], [60, 100], [60, 220], [140, 220], [140, 380], [220, 380]],
        [[20, 260], [140, 260], [140, 180], [220, 180], [220, 420], [180, 420]]
    ],
    top: [
        [[340, 100], [500, 100], [500, 180], [620, 180]],
        [[300, 140], [420, 140], [420, 100], [580, 100], [580, 220], [700, 220]],
        [[380, 220], [380, 140], [540, 140], [540, 100], [660, 100]]
    ],
    primary: [
        [[1420, 180], [1340, 180], [1340, 300], [1260, 300], [1260, 460], [1180, 460], [1180, 580], [1260, 580], [1260, 700], [1140, 700], [1140, 820], [1380, 820]],
        [[1420, 100], [1300, 100], [1300, 220], [1380, 220], [1380, 380], [1220, 380], [1220, 540], [1140, 540], [1140, 700], [1300, 700], [1300, 820], [1420, 820]],
        [[1380, 140], [1260, 140], [1260, 260], [1180, 260], [1180, 420], [1300, 420], [1300, 580], [1220, 580], [1220, 740], [1380, 740], [1380, 860], [1140, 860]]
    ],
    bottom: [
        [[20, 620], [100, 620], [100, 740], [220, 740], [220, 820], [420, 820]],
        [[20, 700], [140, 700], [140, 620], [260, 620], [260, 780], [500, 780]],
        [[60, 860], [60, 740], [180, 740], [180, 660], [340, 660], [340, 820], [500, 820]]
    ],
    mobile: [
        [[940, 340], [900, 340], [900, 460], [940, 460], [940, 580], [900, 580], [900, 700], [940, 700]],
        [[900, 300], [940, 300], [940, 420], [900, 420], [900, 620], [940, 620], [940, 740]],
        [[940, 260], [900, 260], [900, 380], [940, 380], [940, 500], [900, 500], [900, 660], [940, 660]]
    ]
};

const svgNamespace = 'http://www.w3.org/2000/svg';
const reduceCircuitMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

function circuitPathFromPoints(points) {
    return points.reduce((path, [x, y], index) => {
        if (index === 0) return `M${x} ${y}`;
        const [previousX, previousY] = points[index - 1];
        if (y === previousY) return `${path}H${x}`;
        if (x === previousX) return `${path}V${y}`;
        return `${path}L${x} ${y}`;
    }, '');
}

function renderCircuitRoute(route, points, animateMapping = true) {
    if (animateMapping) {
        const activeOffsets = [...route.querySelectorAll('.circuit-flow-tail, .circuit-flow-core')]
            .map(path => getComputedStyle(path).strokeDashoffset);
        const previousRoute = route.cloneNode(true);
        previousRoute.removeAttribute('data-circuit-route');
        previousRoute.classList.remove('is-remapping');
        previousRoute.classList.add('circuit-route-ghost');
        previousRoute.querySelectorAll('.circuit-flow-tail, .circuit-flow-core').forEach((path, index) => {
            path.style.animation = 'none';
            path.style.strokeDashoffset = activeOffsets[index];
        });
        route.parentNode.insertBefore(previousRoute, route);
        window.setTimeout(() => previousRoute.remove(), 900);
    }

    const pathData = circuitPathFromPoints(points);
    route.querySelectorAll('path').forEach(path => path.setAttribute('d', pathData));
    route.querySelectorAll('.circuit-node').forEach(node => node.remove());

    points.forEach(([x, y], index) => {
        const node = document.createElementNS(svgNamespace, 'circle');
        node.classList.add('circuit-node');
        node.setAttribute('cx', x);
        node.setAttribute('cy', y);
        node.setAttribute('r', '3');
        node.style.setProperty('--node-order', index);
        route.appendChild(node);
    });

    if (animateMapping) {
        route.classList.remove('is-remapping');
        void route.getBoundingClientRect();
        route.classList.add('is-remapping');
        window.setTimeout(() => route.classList.remove('is-remapping'), 1050);
    }
}

function chooseNextCircuitRoute(route) {
    const routeName = route.dataset.circuitRoute;
    const options = circuitRouteOptions[routeName];
    if (!options || options.length < 2) return;

    const currentIndex = Number(route.dataset.routeIndex ?? 0);
    let nextIndex = currentIndex;
    while (nextIndex === currentIndex) {
        nextIndex = Math.floor(Math.random() * options.length);
    }

    const nextPoints = [...options[nextIndex]];
    if (Math.random() > 0.5) nextPoints.reverse();
    route.dataset.routeIndex = nextIndex;
    renderCircuitRoute(route, nextPoints);
}

if (!reduceCircuitMotion.matches) {
    document.querySelectorAll('[data-circuit-route]').forEach(route => {
        const options = circuitRouteOptions[route.dataset.circuitRoute];
        const initialIndex = Math.floor(Math.random() * options.length);
        const initialPoints = [...options[initialIndex]];
        if (Math.random() > 0.5) initialPoints.reverse();
        route.dataset.routeIndex = initialIndex;
        renderCircuitRoute(route, initialPoints, false);

        route.querySelector('.circuit-flow-core').addEventListener('animationiteration', () => {
            chooseNextCircuitRoute(route);
        });
    });
}
