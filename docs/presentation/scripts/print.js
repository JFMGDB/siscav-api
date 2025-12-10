/**
 * Script para otimização de impressão
 * Ajusta estilos e layout para melhor resultado em PDF
 */

// Função para preparar impressão
function preparePrint() {
    // Adicionar classe de impressão ao body
    document.body.classList.add('printing');
    
    // Remover navegação
    const navigation = document.getElementById('navigation');
    if (navigation) {
        navigation.style.display = 'none';
    }
    
    // Ajustar estilos de slides para impressão
    const slides = document.querySelectorAll('.slide');
    slides.forEach((slide, index) => {
        // Garantir que cada slide ocupe uma página
        slide.style.pageBreakAfter = index < slides.length - 1 ? 'always' : 'auto';
        slide.style.pageBreakInside = 'avoid';
    });
}

// Função para restaurar após impressão
function restoreAfterPrint() {
    document.body.classList.remove('printing');
    
    const navigation = document.getElementById('navigation');
    if (navigation) {
        navigation.style.display = 'flex';
    }
}

// Event listeners para impressão
if (window.matchMedia) {
    const mediaQueryList = window.matchMedia('print');
    mediaQueryList.addListener((mql) => {
        if (mql.matches) {
            preparePrint();
        } else {
            restoreAfterPrint();
        }
    });
}

// Fallback para navegadores que não suportam matchMedia
window.addEventListener('beforeprint', preparePrint);
window.addEventListener('afterprint', restoreAfterPrint);

// Atalho de teclado para impressão (Ctrl+P)
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        preparePrint();
        window.print();
    }
});

// Função auxiliar para exportar usando impressão nativa (fallback)
function exportToPDFNative() {
    preparePrint();
    window.print();
}

// Tornar função global se necessário
if (typeof window !== 'undefined') {
    window.exportToPDFNative = exportToPDFNative;
}

