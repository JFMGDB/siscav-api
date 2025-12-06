/**
 * Componente: PDFExporter
 * Responsabilidade: Exportar apresentação para PDF
 * Princípio SOLID: Single Responsibility
 * 
 * Decisões de Implementação:
 * - Usa o container original da apresentação para garantir renderização correta
 * - Processa slides individualmente para evitar problemas de memória
 * - Garante que imagens estejam carregadas antes de exportar
 * - Implementa fallback para impressão nativa em caso de falha
 */

class PDFExporter {
    constructor() {
        this.isProcessing = false;
    }

    /**
     * Obtém a classe jsPDF de forma compatível com diferentes versões do html2pdf.js
     * @returns {Promise<Function>} Classe jsPDF
     */
    async getJsPDF() {
        // Tentar múltiplas formas de acessar jsPDF
        let jsPDF = null;
        let attempts = 0;
        const maxAttempts = 15; // Aumentado para dar mais tempo
        
        while (!jsPDF && attempts < maxAttempts) {
            // Método 1: window.jspdf.jsPDF (jsPDF.umd.min.js - mais comum)
            if (window.jspdf && window.jspdf.jsPDF) {
                jsPDF = window.jspdf.jsPDF;
                console.log('jsPDF encontrado via window.jspdf.jsPDF');
                break;
            }
            // Método 2: window.jsPDF (jsPDF carregado separadamente - formato antigo)
            if (window.jsPDF) {
                jsPDF = window.jsPDF;
                console.log('jsPDF encontrado via window.jsPDF');
                break;
            }
            // Método 3: html2pdf pode ter exposto jsPDF
            if (window.html2pdf && window.html2pdf.jsPDF) {
                jsPDF = window.html2pdf.jsPDF;
                console.log('jsPDF encontrado via window.html2pdf.jsPDF');
                break;
            }
            // Método 4: Tentar acessar via jspdf diretamente (sem .jsPDF)
            if (window.jspdf && typeof window.jspdf === 'function') {
                jsPDF = window.jspdf;
                console.log('jsPDF encontrado via window.jspdf (função direta)');
                break;
            }
            
            attempts++;
            if (attempts < maxAttempts) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }

        if (!jsPDF) {
            const errorMsg = 'jsPDF não está disponível. Verifique se os scripts estão carregados.';
            console.error(errorMsg);
            console.error('Tentativas:', attempts);
            console.error('window.jspdf:', window.jspdf);
            console.error('window.jsPDF:', window.jsPDF);
            console.error('window.html2pdf:', window.html2pdf);
            console.error('Tipo de window.jspdf:', typeof window.jspdf);
            if (window.jspdf) {
                console.error('Propriedades de window.jspdf:', Object.keys(window.jspdf));
            }
            throw new Error(errorMsg);
        }

        return jsPDF;
    }

    /**
     * Prepara o ambiente para exportação PDF
     * Oculta navegação e ajusta estilos
     */
    prepareForExport() {
        const navigation = document.getElementById('navigation');
        if (navigation) {
            navigation.style.display = 'none';
        }

        // Garantir que o container esteja visível e posicionado corretamente
        const container = document.querySelector('.presentation-container');
        if (container) {
            container.style.position = 'relative';
            container.style.visibility = 'visible';
            container.style.display = 'block';
        }

        // Garantir que todos os slides estejam visíveis
        const slides = document.querySelectorAll('.slide');
        slides.forEach(slide => {
            slide.style.visibility = 'visible';
            slide.style.display = 'block';
            slide.style.position = 'relative';
            slide.style.pageBreakAfter = 'always';
            slide.style.pageBreakInside = 'avoid';
        });
    }

    /**
     * Restaura o ambiente após exportação
     */
    restoreAfterExport() {
        const navigation = document.getElementById('navigation');
        if (navigation) {
            navigation.style.display = 'flex';
        }
    }

    /**
     * Aguarda o carregamento de todas as imagens
     */
    async waitForImages() {
        const images = document.querySelectorAll('img');
        const imagePromises = Array.from(images).map(img => {
            if (img.complete) {
                return Promise.resolve();
            }
            return new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = resolve; // Continuar mesmo se houver erro
                setTimeout(resolve, 5000); // Timeout de 5 segundos
            });
        });
        await Promise.all(imagePromises);
    }

    /**
     * Captura um slide como canvas usando html2canvas
     * Captura as dimensões reais do conteúdo renderizado, incluindo overflow
     * @param {HTMLElement} slide - Elemento do slide
     * @returns {Promise<{canvas: HTMLCanvasElement, width: number, height: number}>} Canvas e dimensões reais
     */
    async captureSlideAsCanvas(slide) {
        // Obter dimensões reais do conteúdo renderizado
        // scrollWidth/scrollHeight capturam todo o conteúdo, incluindo overflow
        const contentWidth = Math.max(
            slide.scrollWidth,
            slide.offsetWidth,
            slide.clientWidth
        );
        const contentHeight = Math.max(
            slide.scrollHeight,
            slide.offsetHeight,
            slide.clientHeight
        );

        // html2pdf.js expõe html2canvas via window após carregar
        // Tentar acessar de diferentes formas
        let html2canvasFunc = null;
        
        // Método 1: Verificar se está disponível globalmente
        if (typeof window !== 'undefined' && window.html2canvas) {
            html2canvasFunc = window.html2canvas;
        }
        
        // Método 2: html2pdf pode ter exposto html2canvas
        if (!html2canvasFunc && window.html2pdf && window.html2pdf.html2canvas) {
            html2canvasFunc = window.html2pdf.html2canvas;
        }

        if (!html2canvasFunc) {
            throw new Error('html2canvas não está disponível. Certifique-se de que html2canvas.js e html2pdf.js estão carregados.');
        }

        // Capturar slide como canvas com dimensões reais
        // Usar scrollWidth/scrollHeight para capturar todo o conteúdo
        const canvas = await html2canvasFunc(slide, {
            scale: 2, // Alta resolução para qualidade
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff',
            logging: false,
            width: contentWidth,
            height: contentHeight,
            windowWidth: contentWidth,
            windowHeight: contentHeight,
            x: 0,
            y: 0,
            scrollX: 0,
            scrollY: 0
        });

        // Retornar canvas e dimensões reais capturadas
        return {
            canvas: canvas,
            width: canvas.width,
            height: canvas.height
        };
    }

    /**
     * Exporta a apresentação completa para PDF
     * Cada slide ocupa uma página completa, respeitando suas dimensões reais
     */
    async exportToPDF() {
        if (this.isProcessing) {
            NotificationManager.show('PDF já está sendo gerado. Aguarde...', 'error');
            return;
        }

        const pdfButton = document.getElementById('pdfBtn');
        if (!pdfButton) return;

        const originalText = pdfButton.innerHTML;

        try {
            this.isProcessing = true;
            pdfButton.disabled = true;
            pdfButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando PDF...';

            // Preparar ambiente
            this.prepareForExport();

            // Aguardar carregamento de imagens
            NotificationManager.show('Carregando imagens...', 'success');
            await this.waitForImages();

            // Aguardar renderização
            await new Promise(resolve => requestAnimationFrame(resolve));

            // Obter todos os slides
            const slides = document.querySelectorAll('.slide');
            if (!slides || slides.length === 0) {
                throw new Error('Nenhum slide encontrado');
            }

            NotificationManager.show(`Processando ${slides.length} slides...`, 'success');

            // Obter jsPDF de forma compatível
            const jsPDF = await this.getJsPDF();

            // Converter pixels para mm (96 DPI padrão: 1mm ≈ 3.779527559 pixels)
            const pixelsPerMm = 3.779527559;
            
            // Criar PDF inicial (será ajustado com a primeira página)
            let pdf = null;

            // Processar cada slide individualmente
            for (let i = 0; i < slides.length; i++) {
                const slide = slides[i];
                
                // Garantir que o slide esteja visível e renderizado corretamente
                const originalStyles = {
                    display: slide.style.display,
                    visibility: slide.style.visibility,
                    position: slide.style.position,
                    margin: slide.style.margin,
                    transform: slide.style.transform,
                    overflow: slide.style.overflow
                };

                slide.style.display = 'block';
                slide.style.visibility = 'visible';
                slide.style.position = 'relative';
                slide.style.margin = '0';
                slide.style.transform = 'none';
                slide.style.overflow = 'visible'; // Garantir que todo conteúdo seja visível

                // Scroll para garantir renderização completa
                slide.scrollIntoView({ behavior: 'instant', block: 'start' });
                await new Promise(resolve => setTimeout(resolve, 300)); // Aguardar renderização

                // Capturar slide como canvas com dimensões reais
                const { canvas, width: canvasWidth, height: canvasHeight } = await this.captureSlideAsCanvas(slide);
                const imgData = canvas.toDataURL('image/jpeg', 0.95);

                // Calcular dimensões reais em mm baseadas no canvas capturado
                // O canvas já tem as dimensões corretas do conteúdo renderizado
                const pageWidthMm = canvasWidth / pixelsPerMm;
                const pageHeightMm = canvasHeight / pixelsPerMm;

                // Criar ou adicionar página ao PDF com dimensões reais
                if (i === 0) {
                    // Primeira página: criar PDF com dimensões do primeiro slide
                    pdf = new jsPDF({
                        unit: 'mm',
                        format: [pageWidthMm, pageHeightMm],
                        compress: true
                    });
                } else {
                    // Páginas subsequentes: adicionar nova página com dimensões deste slide
                    pdf.addPage([pageWidthMm, pageHeightMm]);
                }

                // Adicionar imagem preenchendo toda a página (dimensões já são exatas)
                // Não precisa ajustar proporção pois a página foi criada com as dimensões exatas do canvas
                pdf.addImage(imgData, 'JPEG', 0, 0, pageWidthMm, pageHeightMm);

                // Restaurar estilos originais
                Object.keys(originalStyles).forEach(key => {
                    if (originalStyles[key] !== undefined && originalStyles[key] !== '') {
                        slide.style[key] = originalStyles[key];
                    } else {
                        slide.style.removeProperty(key);
                    }
                });

                // Atualizar progresso
                if ((i + 1) % 5 === 0 || i === slides.length - 1) {
                    NotificationManager.show(
                        `Processando slide ${i + 1} de ${slides.length}...`, 
                        'success'
                    );
                }
            }

            // Salvar PDF
            pdf.save('SISCAV_Reconhecimento_Placas_IA.pdf');

            // Restaurar ambiente
            this.restoreAfterExport();

            pdfButton.disabled = false;
            pdfButton.innerHTML = originalText;

            NotificationManager.show('PDF gerado com sucesso!', 'success');

        } catch (error) {
            console.error('Erro ao gerar PDF:', error);
            console.error('Detalhes do erro:', error.message, error.stack);

            pdfButton.disabled = false;
            pdfButton.innerHTML = originalText;
            this.restoreAfterExport();

            // Tentar fallback para impressão nativa
            NotificationManager.show('Tentando método alternativo...', 'error');
            
            try {
                this.exportToPDFNative();
            } catch (fallbackError) {
                console.error('Erro no fallback:', fallbackError);
                
                NotificationManager.show(
                    'Erro ao gerar PDF. Use Ctrl+P para imprimir. Detalhes no console.', 
                    'error'
                );
            }
        } finally {
            this.isProcessing = false;
        }
    }

    /**
     * Método alternativo usando impressão nativa do navegador
     */
    exportToPDFNative() {
        this.prepareForExport();
        
        // Aguardar um momento para renderização
        setTimeout(() => {
            window.print();
            this.restoreAfterExport();
        }, 500);
    }

    /**
     * Exporta um slide específico para PDF
     * @param {number} slideIndex - Índice do slide (1-based)
     */
    async exportSlideToPDF(slideIndex) {
        if (this.isProcessing) {
            NotificationManager.show('Operação em andamento. Aguarde...', 'error');
            return;
        }

        const slide = document.querySelector(`[data-slide="${slideIndex}"]`);

        if (!slide) {
            NotificationManager.show('Slide não encontrado!', 'error');
            return;
        }

        try {
            this.isProcessing = true;

            // Preparar slide para exportação
            const originalDisplay = slide.style.display;
            const originalVisibility = slide.style.visibility;
            const originalPosition = slide.style.position;

            slide.style.display = 'block';
            slide.style.visibility = 'visible';
            slide.style.position = 'relative';

            // Aguardar renderização
            await new Promise(resolve => requestAnimationFrame(resolve));
            await this.waitForImages();

            const opt = {
                margin: [0, 0, 0, 0],
                filename: `SISCAV_Slide_${slideIndex}.pdf`,
                image: { 
                    type: 'jpeg', 
                    quality: 0.95 
                },
                html2canvas: {
                    scale: 1.5,
                    useCORS: true,
                    allowTaint: true,
                    letterRendering: true,
                    logging: false,
                    backgroundColor: '#ffffff',
                    width: slide.scrollWidth,
                    height: slide.scrollHeight,
                    windowWidth: slide.scrollWidth,
                    windowHeight: slide.scrollHeight
                },
                jsPDF: {
                    unit: 'mm',
                    format: 'a4',
                    orientation: 'landscape'
                }
            };

            await html2pdf().set(opt).from(slide).save();

            // Restaurar estilos originais
            slide.style.display = originalDisplay;
            slide.style.visibility = originalVisibility;
            slide.style.position = originalPosition;

            NotificationManager.show(`Slide ${slideIndex} exportado com sucesso!`, 'success');

        } catch (error) {
            console.error('Erro ao exportar slide:', error);
            NotificationManager.show('Erro ao exportar slide. Verifique o console.', 'error');
        } finally {
            this.isProcessing = false;
        }
    }
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.PDFExporter = PDFExporter;
}

