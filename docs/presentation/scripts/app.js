/**
 * Arquivo principal de inicialização da aplicação
 * Responsabilidade: Orquestrar inicialização de todos os componentes
 * Princípio SOLID: Dependency Inversion (componentes são instanciados aqui)
 */

// Instâncias globais dos componentes
let slideManager;
let pdfExporter;
let printManager;

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Inicializar gerenciador de slides
        slideManager = new SlideManager();

        // Configurar botões de navegação
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const pdfBtn = document.getElementById('pdfBtn');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => slideManager.previousSlide());
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => slideManager.nextSlide());
        }

        // Inicializar exportador de PDF
        pdfExporter = new PDFExporter();

        if (pdfBtn) {
            pdfBtn.addEventListener('click', () => pdfExporter.exportToPDF());
        }

        // Inicializar gerenciador de impressão
        printManager = new PrintManager();

        // Expor funções globais para acesso externo
        window.previousSlide = () => slideManager.previousSlide();
        window.nextSlide = () => slideManager.nextSlide();
        window.exportToPDF = () => pdfExporter.exportToPDF();

        console.log('Apresentação SISCAV inicializada com sucesso');

    } catch (error) {
        console.error('Erro ao inicializar apresentação:', error);
        NotificationManager.show('Erro ao inicializar apresentação. Verifique o console.', 'error');
    }
});

