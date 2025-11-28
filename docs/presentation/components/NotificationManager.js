/**
 * Componente: NotificationManager
 * Responsabilidade: Gerenciar notificações de feedback
 * Princípio SOLID: Single Responsibility
 */

class NotificationManager {
    static show(message, type = 'success') {
        const existing = document.querySelector('.pdf-notification');
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.className = `pdf-notification pdf-notification-${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.NotificationManager = NotificationManager;
}

