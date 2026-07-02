/**
 * Sales Quest — Missions Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    if (app.isAuthenticated()) {
        loadMissions();
    }
});
async function loadMissions() {
    const activeGrid = document.getElementById('activeMissionsGrid');
    const completedGrid = document.getElementById('completedMissionsGrid');

    try {
        const data = await app.api('/missions');
        const missions = data.missions;
        const active = missions.filter(m => !m.completa);
        const completed = missions.filter(m => m.completa);
        // ─── Render Ativas ───
        if (active.length === 0) {
            activeGrid.innerHTML = `<div class="text-center text-muted py-2" style="grid-column: 1 / -1;">Nenhuma missão ativa no momento.</div>`;
        } else {
            activeGrid.innerHTML = active.map(m => `
                <div class="mission-card">
                    <div class="mission-icon">${m.icone}</div>
                    <div class="mission-info">
                        <div class="flex-between">
                            <div class="mission-title">${m.titulo}</div>
                            <div class="mission-xp">+${m.xp_recompensa} XP</div>
                        </div>
                        <div class="mission-desc">${m.descricao}</div>
                        <div class="progress-bar-container mt-1">
                            <div class="progress-bar" style="width: ${m.percentual}%"></div>
                        </div>
                        <div class="mission-progress mt-1">
                            <div style="flex: 1;">Progresso</div>
                            <div class="fw-700">${formatProgress(m.progresso, m.tipo)} / ${formatProgress(m.meta_valor, m.tipo)}</div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        // ─── Render Completas ───
        if (completed.length === 0) {
            completedGrid.innerHTML = `<div class="text-center text-muted py-2" style="grid-column: 1 / -1;">Você ainda não completou nenhuma missão.</div>`;
        } else {
            completedGrid.innerHTML = completed.map(m => `
                <div class="mission-card complete">
                    <div class="mission-icon" style="background: rgba(6, 214, 160, 0.1);">${m.icone}</div>
                    <div class="mission-info">
                        <div class="flex-between">
                            <div class="mission-title text-accent">${m.titulo}</div>
                            <div class="mission-xp"><i class='bx bx-check'></i> Concluída</div>
                        </div>
                        <div class="mission-desc">${m.descricao}</div>
                        <div class="progress-bar-container mt-1">
                            <div class="progress-bar complete" style="width: 100%"></div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error("Erro ao carregar missões", error);
        activeGrid.innerHTML = `<div class="text-center text-red py-2" style="grid-column: 1 / -1;">Erro ao carregar missões.</div>`;
    }
}
function formatProgress(value, tipo) {
    if (tipo === 'vendas_valor') {
        return `R$ ${value.toLocaleString('pt-BR', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`;
    }
    return Math.floor(value);
}
