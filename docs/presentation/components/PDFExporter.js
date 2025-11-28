/**
 * Componente: PDFExporter
 * Responsabilidade: Exportar apresentação para PDF
 * Princípio SOLID: Single Responsibility
 */

class PDFExporter {
    constructor() {
        this.isProcessing = false;
    }

    async exportToPDF() {
        if (this.isProcessing) return;

        const pdfButton = document.getElementById('pdfBtn');
        if (!pdfButton) return;

        const originalText = pdfButton.innerHTML;

        try {
            this.isProcessing = true;
            pdfButton.disabled = true;
            pdfButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando PDF...';

            const navigation = document.getElementById('navigation');
            const navDisplay = navigation ? navigation.style.display : 'flex';
            if (navigation) navigation.style.display = 'none';

            const slides = document.querySelectorAll('.slide');
            const slidesArray = Array.from(slides);

            const opt = {
                margin: [0, 0, 0, 0],
                filename: 'SISCAV_Reconhecimento_Placas_IA.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: {
                    scale: 2,
                    useCORS: true,
                    letterRendering: true,
                    logging: false,
                    windowWidth: 1123,
                    windowHeight: 794
                },
                jsPDF: {
                    unit: 'mm',
                    format: 'a4',
                    orientation: 'landscape',
                    compress: true
                },
                pagebreak: {
                    mode: ['avoid-all', 'css', 'legacy'],
                    before: '.slide',
                    after: '.slide',
                    avoid: ['.slide']
                }
            };

            const tempContainer = document.createElement('div');
            tempContainer.style.position = 'absolute';
            tempContainer.style.left = '-9999px';
            tempContainer.style.width = '297mm';
            tempContainer.style.height = '210mm';
            document.body.appendChild(tempContainer);

            const batchSize = 5;
            for (let i = 0; i < slidesArray.length; i += batchSize) {
                const batch = slidesArray.slice(i, i + batchSize);
                batch.forEach(slide => {
                    const clone = slide.cloneNode(true);
                    clone.style.pageBreakAfter = 'always';
                    clone.style.pageBreakInside = 'avoid';
                    tempContainer.appendChild(clone);
                });
            }

            await html2pdf().set(opt).from(tempContainer).save();

            document.body.removeChild(tempContainer);

            if (navigation) navigation.style.display = navDisplay;

            pdfButton.disabled = false;
            pdfButton.innerHTML = originalText;

            NotificationManager.show('PDF gerado com sucesso!', 'success');

        } catch (error) {
            console.error('Erro ao gerar PDF:', error);

            const pdfButton = document.getElementById('pdfBtn');
            if (pdfButton) {
                pdfButton.disabled = false;
                pdfButton.innerHTML = originalText;
            }

            const navigation = document.getElementById('navigation');
            if (navigation) navigation.style.display = 'flex';

            NotificationManager.show('Erro ao gerar PDF. Tente novamente.', 'error');
        } finally {
            this.isProcessing = false;
        }
    }

    async exportSlideToPDF(slideIndex) {
        const slide = document.querySelector(`[data-slide="${slideIndex}"]`);

        if (!slide) {
            NotificationManager.show('Slide não encontrado!', 'error');
            return;
        }

        try {
            const opt = {
                margin: [0, 0, 0, 0],
                filename: `SISCAV_Slide_${slideIndex}.pdf`,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: {
                    scale: 2,
                    useCORS: true,
                    letterRendering: true,
                    windowWidth: 1123,
                    windowHeight: 794
                },
                jsPDF: {
                    unit: 'mm',
                    format: 'a4',
                    orientation: 'landscape'
                }
            };

            await html2pdf().set(opt).from(slide).save();
            NotificationManager.show(`Slide ${slideIndex} exportado com sucesso!`, 'success');

        } catch (error) {
            console.error('Erro ao exportar slide:', error);
            NotificationManager.show('Erro ao exportar slide.', 'error');
        }
    }
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.PDFExporter = PDFExporter;
}

