/**
 * Sales Quest — Auth Logic (Login, Register & Logout)
 */
const auth = {
    async login(event) {
        event.preventDefault();

        const btn = document.getElementById('loginBtn');
        const email = document.getElementById('email').value;
        const senha = document.getElementById('senha').value;

        btn.disabled = true;
        btn.innerHTML = "<i class='bx bx-loader-alt bx-spin'></i> Entrando...";

        try {
            const data = await app.api('/login', {
                method: 'POST',
                body: JSON.stringify({ email, senha })
            });

            localStorage.setItem('sq_token', data.access_token);
            localStorage.setItem('sq_user', JSON.stringify(data.user));

            window.location.href = '/dashboard';
        } catch (error) {
            btn.disabled = false;
            btn.innerHTML = "<i class='bx bx-log-in'></i> Entrar";

            const msg = error.data?.detail || 'Erro ao fazer login.';
            app.toast('Erro de Login', msg, 'error');
        }
    },

    async register(event) {
        event.preventDefault();

        const btn = document.getElementById('registerBtn');
        const nome = document.getElementById('nome').value;
        const email = document.getElementById('email').value;
        const senha = document.getElementById('senha').value;

        btn.disabled = true;
        btn.innerHTML = "<i class='bx bx-loader-alt bx-spin'></i> Cadastrando...";

        try {
            const data = await app.api('/register', {
                method: 'POST',
                body: JSON.stringify({ nome, email, senha })
            });

            localStorage.setItem('sq_token', data.access_token);
            localStorage.setItem('sq_user', JSON.stringify(data.user));

            window.location.href = '/dashboard';
        } catch (error) {
            btn.disabled = false;
            btn.innerHTML = "<i class='bx bx-user-plus'></i> Cadastrar";

            const msg = error.data?.detail || 'Erro ao criar conta.';
            app.toast('Erro no Cadastro', msg, 'error');
        }
    },

    logout() {
        localStorage.removeItem('sq_token');
        localStorage.removeItem('sq_user');
        window.location.href = '/login';
    }
};
