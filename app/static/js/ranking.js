/**
 * Sales Quest — Ranking Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    if (app.isAuthenticated()) {
        loadRanking();
    }
});
async function loadRanking() {
    const tbody = document.getElementById('rankingTableBody');
    const podiumContainer = document.getElementById('podium-container');

    try {
        const data = await app.api('/ranking');
        const ranking = data.ranking;
        const currentUser = app.getUser();
        if (ranking.length === 0) {
            podiumContainer.innerHTML = '';
            tbody.innerHTML = `<tr><td colspan="5" class="text-center">Nenhum dado de ranking.</td></tr>`;
            return;
        }
        // ─── Renderiza o Pódio (Top 3) ───
        const top3 = ranking.slice(0, 3);

        let podiumHtml = '<div class="podium">';

        // Renderiza na ordem visual (2º, 1º, 3º)
        const order = [1, 0, 2]; // Índices do array

        order.forEach(idx => {
            const user = top3[idx];
            if (!user) return;

            const isFirst = idx === 0;
            const classes = isFirst ? 'gold' : (idx === 1 ? 'silver' : 'bronze');
            const medal = isFirst ? '🥇' : (idx === 1 ? '🥈' : '🥉');
            const isMe = user.user_id === currentUser.id;

            podiumHtml += `
                <div class="podium-item ${classes}" ${isFirst ? 'style="transform: scale(1.1); z-index: 2;"' : ''}>
                    <div class="podium-position">${medal}</div>
                    <div class="podium-avatar">${user.avatar}</div>
                    <div class="podium-name ${isMe ? 'text-primary-color' : ''}">${user.nome} ${isMe ? '(Você)' : ''}</div>
                    <div class="podium-xp">${user.xp_total.toLocaleString('pt-BR')} XP</div>
                    <div class="podium-level mt-1">Nvl ${user.nivel}</div>
                </div>
            `;
        });

        podiumHtml += '</div>';
        podiumContainer.innerHTML = podiumHtml;
        // ─── Renderiza a Tabela (Todos) ───
        tbody.innerHTML = ranking.map(u => {
            const isMe = u.user_id === currentUser.id;
            let rowClass = isMe ? 'style="background: var(--bg-glass-strong); border-left: 3px solid var(--color-primary);"' : '';

            let posIcon = u.posicao;
            if (u.posicao === 1) posIcon = '🥇';
            else if (u.posicao === 2) posIcon = '🥈';
            else if (u.posicao === 3) posIcon = '🥉';
            return `
                <tr ${rowClass}>
                    <td class="text-center fw-800" style="font-size: 1.1rem;">${posIcon}</td>
                    <td>
                        <div class="flex-gap" style="align-items: center;">
                            <div style="font-size: 1.5rem;">${u.avatar}</div>
                            <div>
                                <div class="fw-700 ${isMe ? 'text-primary-color' : ''}">${u.nome} ${isMe ? '(Você)' : ''}</div>
                                <div class="text-muted" style="font-size: 0.8rem;">${u.titulo}</div>
                            </div>
                        </div>
                    </td>
                    <td><span class="nav-badge" style="position: static;">${u.nivel}</span></td>
                    <td class="text-right fw-700">${u.total_vendas}</td>
                    <td class="text-right fw-800 text-gold">${u.xp_total.toLocaleString('pt-BR')} XP</td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error("Erro ao carregar ranking", error);
        podiumContainer.innerHTML = '';
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-red">Erro ao carregar dados.</td></tr>`;
    }
}
