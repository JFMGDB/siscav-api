# Changelog - Apresentação SISCAV

## [2.0.0] - 2025-11-28

### Correções Críticas

#### Bug de Geração de PDF Corrigido
- **Problema**: PDF gerava apenas página em branco
- **Causa**: Container temporário invisível e configurações incorretas do html2canvas
- **Solução**: 
  - Uso do container original da apresentação
  - Aguarda carregamento completo de imagens
  - Configurações otimizadas do html2canvas
  - Implementação de fallback para impressão nativa

### Melhorias

#### Componente PDFExporter
- Adicionado método `waitForImages()` para garantir carregamento de imagens
- Adicionado método `prepareForExport()` para preparação do ambiente
- Adicionado método `restoreAfterExport()` para restauração do ambiente
- Adicionado método `exportToPDFNative()` como fallback
- Melhor tratamento de erros com logs detalhados
- Notificações de feedback em cada etapa do processo
- Prevenção de múltiplas execuções simultâneas

#### Documentação
- Criado `CORRECAO_PDF.md` com detalhes completos da correção
- Atualizado `README.md` com informações sobre exportação
- Documentação de decisões arquiteturais

### Mudanças Técnicas

- **html2canvas scale**: Reduzido de 2 para 1.5 (melhor performance)
- **image quality**: Ajustado para 0.95 (balance qualidade/tamanho)
- **Dimensões dinâmicas**: Baseadas no container real em vez de fixas
- **allowTaint**: Habilitado para melhor compatibilidade com imagens

## [1.0.0] - 2025-11-28

### Funcionalidades Iniciais

- Apresentação completa com 28 slides
- Navegação por teclado e mouse
- Exportação para PDF (com bug)
- Sistema de notificações
- Componentização JavaScript (SOLID, DRY)
- Estrutura organizada por categorias
- Evidências visuais integradas
- Formato A4 paisagem otimizado
- Documentação completa

---

**Formato**: [Versão] - Data  
**Tipos**: Correções, Melhorias, Mudanças Técnicas, Funcionalidades













