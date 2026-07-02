/**
 * Sales Quest — Dashboard Logic
 */
document.addEventListener('DOMContentLoaded', async () => {
    if (!app.isAuthenticated()) return;
    try {
        // 1. Carrega dados do usuário (Profile)
        const user = await app.api('/me');
        updateDashboardCards(user);
        // 2. Carrega Recomendações da IA
        loadAIRecommendations();
        // 3. Carrega Estatísticas de Vendas (Gráfico)
        loadSalesStats();
        // 4. Carrega Histórico de XP
        loadXPHistory();
    } catch (e) {
        console.error("Erro ao inicializar dashboard", e);
    }
});
function updateDashboardCards(user) {
    // Top Cards
    document.getElementById('stat-valor-vendas').textContent =
        new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(user.valor_vendas);

    document.getElementById('stat-total-vendas').textContent = user.total_vendas;
    document.getElementById('stat-xp').textContent = user.xp_total;
    document.getElementById('stat-posicao').textContent = `${user.posicao_ranking}º`;
    document.getElementById('stat-total-clientes').textContent = user.total_clientes;
    // Profile Card (Progress)
    const li = user.level_info;
    document.getElementById('dash-avatar').textContent = user.avatar;
    document.getElementById('dash-nome').textContent = user.nome;
    document.getElementById('dash-titulo').textContent = li.titulo;
    document.getElementById('dash-nivel').textContent = li.nivel;
    document.getElementById('dash-xp-text').textContent = `${li.xp_no_nivel} / ${li.xp_necessario} XP`;

    // Anima a barra de progresso
    setTimeout(() => {
        document.getElementById('dash-xp-bar').style.width = `${li.percentual}%`;
    }, 100);
}
async function loadAIRecommendations() {
    const container = document.getElementById('ai-recommendations-container');
    try {
        const data = await app.api('/ai/recommendations');
        const recs = data.recommendations;
        if (recs.length === 0) {
            container.innerHTML = '';
            return;
        }
        container.innerHTML = recs.map(rec => `
            <div class="ai-card">
                <div class="ai-icon">${rec.icone}</div>
                <div>
                    <div class="ai-title">${rec.titulo}</div>
                    <div class="ai-message">${rec.mensagem}</div>
                </div>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = '';
    }
}
async function loadSalesStats() {
    try {
        const data = await app.api('/sales/stats');
        const daily = data.daily_sales;
        if (!daily || daily.length === 0) return;
        const ctx = document.getElementById('salesChart');
        if (!ctx) return;
        // Prepara dados
        const labels = daily.map(d => `${d.dia_semana} (${d.data})`);
        const values = daily.map(d => d.valor);
        // Cria o gradiente
        const canvasCtx = ctx.getContext('2d');
        const gradient = canvasCtx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(124, 92, 252, 0.5)'); // primary
        gradient.addColorStop(1, 'rgba(124, 92, 252, 0.0)');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Vendas (R$)',
                    data: values,
                    borderColor: '#7c5cfc',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    pointBackgroundColor: '#06d6a0',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.4 // Curva suave
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(20, 20, 40, 0.9)',
                        titleFont: { family: "'Outfit', sans-serif", size: 14 },
                        bodyFont: { family: "'Inter', sans-serif", size: 13 },
                        padding: 10,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(context.parsed.y);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                        ticks: { color: '#a0a0c0' }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
                        ticks: {
                            color: '#a0a0c0',
                            callback: function(value) {
                                return 'R$ ' + (value / 1000 >= 1 ? (value/1000) + 'k' : value);
                            }
                        }
                    }
                }
            }
        });
    } catch (e) {
        console.error("Erro no gráfico", e);
    }
}
async function loadXPHistory() {
    const list = document.getElementById('xp-history-list');
    try {
        const data = await app.api('/xp/history');
        const logs = data.logs.slice(0, 5); // Pega apenas os 5 últimos
        if (logs.length === 0) return;
        list.innerHTML = logs.map(log => {
            const date = new Date(log.created_at);
            const timeStr = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

            let icon = 'bx-star text-gold';
            if (log.fonte === 'missao') icon = 'bx-flag-alt text-primary-color';
            if (log.fonte === 'conquista') icon = 'bx-medal text-accent';

            return `
                <div class="flex-between mb-1" style="padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-color);">
                    <div class="flex-gap" style="align-items: center;">
                        <i class='bx ${icon}' style="font-size: 1.2rem; background: var(--bg-glass-strong); padding: 8px; border-radius: 8px;"></i>
                        <div>
                            <div class="fw-700" style="font-size: 0.9rem;">${log.descricao}</div>
                            <div class="text-muted" style="font-size: 0.75rem;">Hoje, ${timeStr}</div>
                        </div>
                    </div>
                    <div class="text-gold fw-800" style="font-size: 1.1rem;">+${log.quantidade}</div>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error("Erro no histórico XP", e);
    }
}
