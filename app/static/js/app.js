/**
 * Sales Quest — App Core
 * Gerencia autenticação, requisições à API, sidebar e UI comum (toasts).
 */
const app = {
    // ─── API Wrapper ───
    async api(endpoint, options = {}) {
        const token = localStorage.getItem('sq_token');
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        try {
            const response = await fetch(`/api${endpoint}`, {
                ...options,
                headers
            });
            const data = await response.json().catch(() => null);
            if (!response.ok) {
                if (response.status === 401 && !endpoint.includes('/login')) {
                    // Token expirado ou inválido
                    app.logout();
                }
                throw { status: response.status, data: data || { detail: 'Erro desconhecido' } };
            }
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    // ─── Auth ───
    isAuthenticated() {
        return !!localStorage.getItem('sq_token');
    },
    requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login';
        } else {
            this.loadUserSidebar();
        }
    },
    logout() {
        localStorage.removeItem('sq_token');
        localStorage.removeItem('sq_user');
        window.location.href = '/login';
    },
    getUser() {
        try {
            return JSON.parse(localStorage.getItem('sq_user') || '{}');
        } catch {
            return {};
        }
    },
    async loadUserSidebar() {
        try {
            const data = await this.api('/me');
            localStorage.setItem('sq_user', JSON.stringify(data));

            // Atualiza Sidebar
            const nameEl = document.getElementById('sidebar-name');
            const levelEl = document.getElementById('sidebar-level');
            const avatarEl = document.getElementById('sidebar-avatar');
            if (nameEl) nameEl.textContent = data.nome;
            if (levelEl) levelEl.textContent = `Nível ${data.nivel} • ${data.level_info.titulo}`;
            if (avatarEl) {
                if (data.avatar && data.avatar.startsWith('/')) {
                    avatarEl.innerHTML = `<img src="${data.avatar}" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
                } else {
                    avatarEl.textContent = data.avatar || '🧑‍💼';
                }
            }
        } catch (e) {
            console.error('Erro ao carregar usuário sidebar', e);
        }
    },
    // ─── Toasts ───
    toast(title, message, type = 'success') {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        let icon = 'bx-check-circle';
        if (type === 'error') icon = 'bx-error-circle';
        if (type === 'xp') icon = 'bx-star';
        if (type === 'achievement') icon = 'bx-medal';
        toast.innerHTML = `
            <i class='bx ${icon} toast-icon'></i>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                ${message ? `<div class="toast-message">${message}</div>` : ''}
            </div>
        `;
        container.appendChild(toast);
        // Remove após 4 segundos
        setTimeout(() => {
            toast.style.animation = 'slide-out-right 0.4s ease forwards';
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    },

    // ─── Upload Avatar ───
    async uploadAvatar(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const token = localStorage.getItem('sq_token');
            const response = await fetch('/api/upload-avatar', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            const data = await response.json();
            
            if (response.ok) {
                this.toast('Sucesso', 'Foto de perfil atualizada!', 'success');
                this.loadUserSidebar();
                return data.avatar;
            } else {
                this.toast('Erro', data.detail || 'Falha ao enviar foto.', 'error');
            }
        } catch (error) {
            console.error('Erro de upload', error);
            this.toast('Erro', 'Falha na comunicação com servidor.', 'error');
        }
        return null;
    }
};

// ─── Sidebar Toggle ───
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}
