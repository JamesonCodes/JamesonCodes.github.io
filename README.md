# Jameson Campbell - Personal Brand Website

A clean, modern single-page portfolio website showcasing internal tools engineering, AI productivity projects, and systems integration work.

## 🌐 Live Site

Visit the live site at: [jamesoncodes.github.io](https://jamesoncodes.github.io)

## 🎯 Purpose

This website establishes my credibility as a builder of internal tools and AI-enabled systems who connects business pain points to technical solutions.

**Positioning:** Internal Tools Engineer / AI Productivity Builder / Systems Integrator

## 🛠️ Tech Stack

- **HTML5** - Semantic markup
- **Tailwind CSS** (via CDN) - Utility-first styling
- **Vanilla JavaScript** - Interactive features
- **GitHub Pages** - Hosting

## 📁 Project Structure

```
/
├── index.html          # Main single-page site
├── styles.css          # Custom CSS (animations, overrides)
├── script.js           # All JavaScript functionality
├── assets/             # Image assets folder
│   ├── projects/       # Project screenshots
│   └── diagrams/       # Architecture diagrams
└── README.md           # This file
```

## ✨ Features

- **Responsive Design** - Mobile-first approach, looks great on all devices
- **Dark Mode** - Toggle between light and dark themes (persisted in localStorage)
- **Smooth Animations** - Fade-in effects on scroll using Intersection Observer
- **Smooth Navigation** - Sticky navbar with smooth scrolling to sections
- **Performance Optimized** - Debounced scroll events, efficient animations
- **Accessible** - Semantic HTML, keyboard navigation, proper ARIA labels

## 📄 Sections

1. **Hero** - Bold headline with positioning statement and CTA buttons
2. **Featured Project** - Deep dive into Semantic Visual Search project
3. **What I Build** - Grid of work projects and personal experiments
4. **About Me** - Personal story and approach to building
5. **Philosophy** - 4-step process table (Discover → Prototype → Validate → Scale/Kill)
6. **Stack & Skills** - Technologies and philosophies organized by category
7. **Writing** - Blog placeholder for future posts
8. **Contact** - Clear CTA with email and social links

## 🎨 Design Principles

- Clean, minimal design with lots of white space
- Sans-serif font stack for readability
- Monospace accents for "builder" vibe
- Accent color: Muted electric blue (#2E9DFB)
- Rounded cards with subtle shadows
- Smooth transitions and hover effects

## 🚀 Getting Started

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/JamesonCodes/JamesonCodes.github.io.git
   cd JamesonCodes.github.io
   ```

2. Open `index.html` in your browser:
   ```bash
   open index.html
   # or
   python -m http.server 8000
   # then visit http://localhost:8000
   ```

3. Make your changes and test locally

### Deployment

The site is automatically deployed via GitHub Pages from the `main` branch.

To deploy your changes:
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

Changes will be live at `https://jamesoncodes.github.io` within a few minutes.

## 📝 Customization Guide

### Update Personal Information

1. **Name and Title** - Edit the hero section in `index.html`
2. **Projects** - Update project cards with your actual projects
3. **Contact Links** - Replace placeholder email, LinkedIn, GitHub links
4. **Technologies** - Update the Stack & Skills section with your tools

### Add Images

1. Add project screenshots to `assets/projects/`
2. Add architecture diagrams to `assets/diagrams/`
3. Update image placeholders in `index.html`:
   ```html
   <img src="assets/projects/your-image.png" alt="Description">
   ```

### Customize Colors

Edit the Tailwind config in `index.html`:
```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                accent: '#2E9DFB',  // Change this
                'accent-dark': '#1E7FC7',  // And this
            }
        }
    }
}
```

### Add Blog Posts

Replace the "Coming Soon" placeholders in the Writing section with actual blog post links.

## 🔧 JavaScript Features

- **Dark Mode Toggle** - Persisted in localStorage
- **Mobile Menu** - Hamburger menu for mobile devices
- **Smooth Scrolling** - Navigate to sections smoothly
- **Scroll Animations** - Fade-in effects using Intersection Observer
- **Active Section Highlighting** - Navigation updates based on scroll position
- **Performance Optimized** - Debounced scroll handlers

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 📄 License

MIT License - Feel free to use this as a template for your own portfolio!

## 🤝 Contributing

This is a personal portfolio site, but if you find bugs or have suggestions, feel free to open an issue.

---

**Built with ❤️ by Jameson Campbell**
