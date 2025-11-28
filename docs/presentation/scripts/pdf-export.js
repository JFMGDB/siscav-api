/**
 * Script para exportar apresentação em PDF
 * Utiliza html2pdf.js para conversão
 */

/**
 * Exporta a apresentação completa para PDF
 */
async function exportToPDF() {
    const pdfButton = document.getElementById('pdfBtn');
    const originalText = pdfButton.innerHTML;
    
    try {
        // Desabilitar botão durante o processamento
        pdfButton.disabled = true;
        pdfButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando PDF...';
        
        // Ocultar navegação temporariamente
        const navigation = document.getElementById('navigation');
        const navDisplay = navigation.style.display;
        navigation.style.display = 'none';
        
        // Obter todos os slides
        const slides = document.querySelectorAll('.slide');
        const slidesArray = Array.from(slides);
        
        // Opções de configuração do PDF
        const opt = {
            margin: [0, 0, 0, 0],
            filename: 'SISCAV_Reconhecimento_Placas_IA.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { 
                scale: 2,
                useCORS: true,
                letterRendering: true,
                logging: false,
                windowWidth: 1123, // 297mm em pixels (A4 paisagem)
                windowHeight: 794  // 210mm em pixels (A4 paisagem)
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
        
        // Criar container temporário para os slides
        const tempContainer = document.createElement('div');
        tempContainer.style.position = 'absolute';
        tempContainer.style.left = '-9999px';
        tempContainer.style.width = '297mm';
        tempContainer.style.height = '210mm';
        document.body.appendChild(tempContainer);
        
        // Processar slides em lotes para evitar problemas de memória
        const batchSize = 5;
        const pdfPromises = [];
        
        for (let i = 0; i < slidesArray.length; i += batchSize) {
            const batch = slidesArray.slice(i, i + batchSize);
            
            // Clonar slides do batch
            batch.forEach(slide => {
                const clone = slide.cloneNode(true);
                clone.style.pageBreakAfter = 'always';
                clone.style.pageBreakInside = 'avoid';
                tempContainer.appendChild(clone);
            });
        }
        
        // Gerar PDF
        await html2pdf().set(opt).from(tempContainer).save();
        
        // Limpar container temporário
        document.body.removeChild(tempContainer);
        
        // Restaurar navegação
        navigation.style.display = navDisplay;
        
        // Restaurar botão
        pdfButton.disabled = false;
        pdfButton.innerHTML = originalText;
        
        // Mostrar mensagem de sucesso
        showNotification('PDF gerado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro ao gerar PDF:', error);
        
        // Restaurar botão
        pdfButton.disabled = false;
        pdfButton.innerHTML = originalText;
        
        // Restaurar navegação
        const navigation = document.getElementById('navigation');
        navigation.style.display = 'flex';
        
        // Mostrar mensagem de erro
        showNotification('Erro ao gerar PDF. Tente novamente.', 'error');
    }
}

/**
 * Exporta um slide específico para PDF
 * @param {number} slideIndex - Índice do slide (1-based)
 */
async function exportSlideToPDF(slideIndex) {
    const slide = document.querySelector(`[data-slide="${slideIndex}"]`);
    
    if (!slide) {
        showNotification('Slide não encontrado!', 'error');
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
        showNotification(`Slide ${slideIndex} exportado com sucesso!`, 'success');
        
    } catch (error) {
        console.error('Erro ao exportar slide:', error);
        showNotification('Erro ao exportar slide.', 'error');
    }
}

/**
 * Mostra notificação de feedback
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo: 'success' ou 'error'
 */
function showNotification(message, type = 'success') {
    // Remover notificação anterior se existir
    const existing = document.querySelector('.pdf-notification');
    if (existing) {
        existing.remove();
    }
    
    // Criar notificação
    const notification = document.createElement('div');
    notification.className = `pdf-notification pdf-notification-${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remover após 3 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

/**
 * Exporta usando a API nativa de impressão do navegador
 * Útil como fallback se html2pdf.js não funcionar
 */
function exportToPDFNative() {
    if (typeof preparePrint === 'function') {
        preparePrint();
    }
    window.print();
}

// Tornar funções globais
if (typeof window !== 'undefined') {
    window.exportToPDF = exportToPDF;
    window.exportSlideToPDF = exportSlideToPDF;
    window.exportToPDFNative = exportToPDFNative;
}

