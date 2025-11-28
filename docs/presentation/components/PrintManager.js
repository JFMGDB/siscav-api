/**
 * Componente: PrintManager
 * Responsabilidade: Gerenciar otimização de impressão
 * Princípio SOLID: Single Responsibility
 */

class PrintManager {
    constructor() {
        this.isPrinting = false;
        this.init();
    }

    init() {
        this.setupPrintListeners();
        this.setupKeyboardShortcut();
    }

    preparePrint() {
        this.isPrinting = true;
        document.body.classList.add('printing');

        const navigation = document.getElementById('navigation');
        if (navigation) {
            navigation.style.display = 'none';
        }

        const slides = document.querySelectorAll('.slide');
        slides.forEach((slide, index) => {
            slide.style.pageBreakAfter = index < slides.length - 1 ? 'always' : 'auto';
            slide.style.pageBreakInside = 'avoid';
        });
    }

    restoreAfterPrint() {
        this.isPrinting = false;
        document.body.classList.remove('printing');

        const navigation = document.getElementById('navigation');
        if (navigation) {
            navigation.style.display = 'flex';
        }
    }

    setupPrintListeners() {
        if (window.matchMedia) {
            const mediaQueryList = window.matchMedia('print');
            mediaQueryList.addListener((mql) => {
                if (mql.matches) {
                    this.preparePrint();
                } else {
                    this.restoreAfterPrint();
                }
            });
        }

        window.addEventListener('beforeprint', () => this.preparePrint());
        window.addEventListener('afterprint', () => this.restoreAfterPrint());
    }

    setupKeyboardShortcut() {
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
                e.preventDefault();
                this.preparePrint();
                window.print();
            }
        });
    }

    exportToPDFNative() {
        this.preparePrint();
        window.print();
    }
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.PrintManager = PrintManager;
}

