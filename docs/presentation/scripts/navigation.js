/**
 * Script de navegação entre slides
 * Permite navegação por teclado e botões
 */

let currentSlideIndex = 1;
const totalSlides = document.querySelectorAll('.slide').length;

// Atualizar contador
function updateSlideCounter() {
    document.getElementById('currentSlide').textContent = currentSlideIndex;
    document.getElementById('totalSlides').textContent = totalSlides;
    
    // Atualizar estado dos botões
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    prevBtn.disabled = currentSlideIndex === 1;
    nextBtn.disabled = currentSlideIndex === totalSlides;
}

// Ir para slide específico
function goToSlide(index) {
    if (index < 1 || index > totalSlides) {
        return;
    }
    
    currentSlideIndex = index;
    const slide = document.querySelector(`[data-slide="${index}"]`);
    
    if (slide) {
        slide.scrollIntoView({ behavior: 'smooth', block: 'start' });
        updateSlideCounter();
    }
}

// Próximo slide
function nextSlide() {
    if (currentSlideIndex < totalSlides) {
        goToSlide(currentSlideIndex + 1);
    }
}

// Slide anterior
function previousSlide() {
    if (currentSlideIndex > 1) {
        goToSlide(currentSlideIndex - 1);
    }
}

// Navegação por teclado
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === 'PageDown') {
        e.preventDefault();
        nextSlide();
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        e.preventDefault();
        previousSlide();
    } else if (e.key === 'Home') {
        e.preventDefault();
        goToSlide(1);
    } else if (e.key === 'End') {
        e.preventDefault();
        goToSlide(totalSlides);
    }
});

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    updateSlideCounter();
    
    // Scroll para o primeiro slide
    goToSlide(1);
    
    // Observar mudanças de scroll para atualizar slide atual
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            const slides = document.querySelectorAll('.slide');
            const scrollPosition = window.scrollY + window.innerHeight / 2;
            
            slides.forEach((slide, index) => {
                const rect = slide.getBoundingClientRect();
                const slideTop = rect.top + window.scrollY;
                const slideBottom = slideTop + rect.height;
                
                if (scrollPosition >= slideTop && scrollPosition <= slideBottom) {
                    currentSlideIndex = index + 1;
                    updateSlideCounter();
                }
            });
        }, 100);
    });
});

