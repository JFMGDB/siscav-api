/**
 * Componente: SlideManager
 * Responsabilidade: Gerenciar navegação e estado dos slides
 * Princípio SOLID: Single Responsibility
 */

class SlideManager {
    constructor() {
        this.currentSlideIndex = 1;
        this.slides = document.querySelectorAll('.slide');
        this.totalSlides = this.slides.length;
        this.init();
    }

    init() {
        this.updateSlideCounter();
        this.setupKeyboardNavigation();
        this.setupScrollObserver();
        this.goToSlide(1);
    }

    updateSlideCounter() {
        const currentSlideEl = document.getElementById('currentSlide');
        const totalSlidesEl = document.getElementById('totalSlides');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        if (currentSlideEl) currentSlideEl.textContent = this.currentSlideIndex;
        if (totalSlidesEl) totalSlidesEl.textContent = this.totalSlides;
        if (prevBtn) prevBtn.disabled = this.currentSlideIndex === 1;
        if (nextBtn) nextBtn.disabled = this.currentSlideIndex === this.totalSlides;
    }

    goToSlide(index) {
        if (index < 1 || index > this.totalSlides) return;

        this.currentSlideIndex = index;
        const slide = document.querySelector(`[data-slide="${index}"]`);

        if (slide) {
            slide.scrollIntoView({ behavior: 'smooth', block: 'start' });
            this.updateSlideCounter();
        }
    }

    nextSlide() {
        if (this.currentSlideIndex < this.totalSlides) {
            this.goToSlide(this.currentSlideIndex + 1);
        }
    }

    previousSlide() {
        if (this.currentSlideIndex > 1) {
            this.goToSlide(this.currentSlideIndex - 1);
        }
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === 'PageDown') {
                e.preventDefault();
                this.nextSlide();
            } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
                e.preventDefault();
                this.previousSlide();
            } else if (e.key === 'Home') {
                e.preventDefault();
                this.goToSlide(1);
            } else if (e.key === 'End') {
                e.preventDefault();
                this.goToSlide(this.totalSlides);
            }
        });
    }

    setupScrollObserver() {
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const scrollPosition = window.scrollY + window.innerHeight / 2;

                this.slides.forEach((slide, index) => {
                    const rect = slide.getBoundingClientRect();
                    const slideTop = rect.top + window.scrollY;
                    const slideBottom = slideTop + rect.height;

                    if (scrollPosition >= slideTop && scrollPosition <= slideBottom) {
                        this.currentSlideIndex = index + 1;
                        this.updateSlideCounter();
                    }
                });
            }, 100);
        });
    }
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.SlideManager = SlideManager;
}

