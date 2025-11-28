# Decisões de Arquitetura - Apresentação SISCAV

## Documentação Técnica das Decisões

Este documento detalha as decisões arquiteturais tomadas durante o desenvolvimento da apresentação, explicando o "porquê" de cada escolha.

---

## 1. Arquitetura de Componentes

### Decisão
Implementar uma arquitetura baseada em componentes JavaScript independentes, cada um com responsabilidade única.

### Contexto
A apresentação original utilizava scripts monolíticos com funções globais, dificultando manutenção e testes.

### Alternativas Consideradas
1. **Scripts Monolíticos** (rejeitado): Difícil manutenção e teste
2. **Framework Completo** (React/Vue) (rejeitado): Overhead desnecessário para apresentação estática
3. **Componentes Vanilla JS** (escolhido): Balance entre simplicidade e organização

### Consequências
- ✅ **Positivas**: Código mais organizado, testável e manutenível
- ⚠️ **Negativas**: Requer conhecimento de classes ES6 (mitigado com documentação)

### Implementação
```javascript
// Cada componente é uma classe independente
class SlideManager {
    constructor() { /* ... */ }
    // Métodos específicos de navegação
}
```

---

## 2. Organização de Pastas por Categoria

### Decisão
Criar estrutura de pastas categorizada: `assets/images/`, `components/`, `styles/modules/`.

### Contexto
Arquivos estavam na raiz, dificultando localização e organização conforme o projeto crescia.

### Alternativas Consideradas
1. **Estrutura Plana** (rejeitado): Dificulta escalabilidade
2. **Organização por Tipo** (escolhido): Facilita localização e manutenção
3. **Organização por Feature** (rejeitado): Overhead para apresentação simples

### Consequências
- ✅ **Positivas**: Fácil localizar arquivos, escalável, profissional
- ⚠️ **Negativas**: Mais níveis de diretório (mitigado com documentação)

---

## 3. Variáveis CSS Centralizadas

### Decisão
Utilizar variáveis CSS (`:root`) para todas as cores, espaçamentos e dimensões.

### Contexto
Código CSS tinha valores hardcoded repetidos, dificultando mudanças de tema.

### Alternativas Consideradas
1. **Valores Hardcoded** (rejeitado): Dificulta manutenção
2. **Variáveis CSS** (escolhido): Padrão moderno, suportado nativamente
3. **Pré-processadores** (SASS/LESS) (rejeitado): Dependência adicional desnecessária

### Consequências
- ✅ **Positivas**: Fácil mudança de tema, consistência visual, DRY
- ✅ **Sem negativas significativas**

### Implementação
```css
:root {
    --color-primary: #3b82f6;
    --spacing-md: 1.5rem;
    --slide-width: 297mm;
}
```

---

## 4. Formato A4 Paisagem

### Decisão
Otimizar apresentação para impressão em formato A4 paisagem (297mm x 210mm).

### Contexto
Requisito do cliente para apresentação impressa em formato padrão.

### Alternativas Consideradas
1. **A4 Retrato** (rejeitado): Menos espaço horizontal
2. **A4 Paisagem** (escolhido): Mais espaço para conteúdo visual
3. **Formato Customizado** (rejeitado): Não padrão, dificulta impressão

### Consequências
- ✅ **Positivas**: Formato padrão, fácil impressão, mais espaço horizontal
- ⚠️ **Negativas**: Menos espaço vertical (mitigado com design responsivo)

### Implementação
```css
:root {
    --slide-width: 297mm;  /* A4 largura */
    --slide-height: 210mm;  /* A4 altura */
}
```

---

## 5. Evidências Visuais em Slides Dedicados

### Decisão
Adicionar slides específicos (7.5 e 22.5) com imagens de evidências do sistema funcionando.

### Contexto
Apresentação técnica necessita de demonstração prática para validar conceitos teóricos.

### Alternativas Consideradas
1. **Sem Evidências** (rejeitado): Apresentação apenas teórica
2. **Evidências em Slides Existentes** (rejeitado): Sobrecarrega slides
3. **Slides Dedicados** (escolhido): Foco claro, não interfere no fluxo

### Consequências
- ✅ **Positivas**: Validação prática, aumenta credibilidade, demonstra funcionamento
- ⚠️ **Negativas**: Aumenta número de slides (mitigado com numeração decimal)

---

## 6. Sistema de Notificações Centralizado

### Decisão
Criar componente `NotificationManager` para gerenciar todas as notificações.

### Contexto
Código de notificações estava duplicado em múltiplos arquivos.

### Alternativas Consideradas
1. **Notificações Inline** (rejeitado): Código duplicado
2. **Componente Centralizado** (escolhido): DRY, fácil manutenção
3. **Biblioteca Externa** (rejeitado): Dependência desnecessária

### Consequências
- ✅ **Positivas**: DRY, consistência visual, fácil manutenção
- ✅ **Sem negativas significativas**

### Implementação
```javascript
// Uso simples e consistente
NotificationManager.show('Mensagem', 'success');
```

---

## 7. Exportação PDF com html2pdf.js

### Decisão
Utilizar biblioteca `html2pdf.js` para exportação de PDF.

### Contexto
Necessidade de exportar apresentação completa para PDF mantendo formatação.

### Alternativas Consideradas
1. **Impressão Nativa** (rejeitado): Menos controle sobre formatação
2. **html2pdf.js** (escolhido): Bom controle, formato A4, fácil uso
3. **Puppeteer/Headless Browser** (rejeitado): Complexidade desnecessária

### Consequências
- ✅ **Positivas**: Bom controle de formatação, formato A4, qualidade
- ⚠️ **Negativas**: Dependência externa (mitigado com CDN confiável)

---

## 8. Navegação por Teclado

### Decisão
Implementar navegação completa por teclado (setas, Home, End).

### Contexto
Melhorar acessibilidade e experiência do usuário durante apresentação.

### Alternativas Consideradas
1. **Apenas Mouse** (rejeitado): Menos acessível
2. **Navegação Completa** (escolhido): Padrão de apresentações, acessível
3. **Navegação Customizada** (rejeitado): Confunde usuários

### Consequências
- ✅ **Positivas**: Acessibilidade, UX melhorada, padrão conhecido
- ✅ **Sem negativas significativas**

---

## Princípios Aplicados

### SOLID
- **S**: Cada componente uma responsabilidade única
- **O**: Componentes extensíveis sem modificação
- **L**: Componentes substituíveis por implementações alternativas
- **I**: Interfaces específicas (métodos públicos claros)
- **D**: Dependências injetadas via construtor

### DRY
- Variáveis CSS centralizadas
- Componentes reutilizáveis
- Funções utilitárias compartilhadas
- Estilos base reutilizados

### Componentização
- Componentes independentes
- Baixo acoplamento
- Alta coesão
- Interface clara e documentada

---

## Métricas de Qualidade

### Manutenibilidade
- ✅ Código organizado e documentado
- ✅ Componentes testáveis isoladamente
- ✅ Fácil adicionar novas funcionalidades

### Performance
- ✅ Carregamento otimizado
- ✅ Processamento eficiente de PDF
- ✅ Debounce em eventos de scroll

### Acessibilidade
- ✅ Navegação por teclado
- ✅ Estrutura semântica HTML5
- ✅ Atributos alt em imagens
- ✅ Contraste adequado

---

## Lições Aprendidas

1. **Componentização paga dividendos**: Mesmo em projetos pequenos, organização facilita manutenção
2. **Variáveis CSS são essenciais**: Facilitam mudanças de tema e consistência
3. **Evidências visuais aumentam credibilidade**: Slides com imagens reais são mais convincentes
4. **Documentação é investimento**: Facilita manutenção futura e onboarding

---

**Documentado por**: Equipe de Desenvolvimento SISCAV  
**Data**: Novembro 2025  
**Versão**: 1.0.0

