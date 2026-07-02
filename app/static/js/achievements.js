/**
 * Sales Quest — Achievements Logic
 */
document.addEventListener('DOMContentLoaded', () => {
    if (app.isAuthenticated()) {
        loadAchievements();
    }
});
async function loadAchievements() {
    const grid = document.getElementById('achievementsGrid');
    const progressText = document.getElementById('achievementsProgress');

    try {
        const data = await app.api('/achievements');
        const achievements = data.achievements;
        if (achievements.length === 0) {
            grid.innerHTML = `<div class="text-center text-muted py-2" style="grid-column: 1 / -1;">Nenhuma conquista disponível no momento.</div>`;
            return;
        }
        const unlockedCount = achievements.filter(a => a.desbloqueada).length;
        progressText.textContent = `${unlockedCount}/${achievements.length}`;
        grid.innerHTML = achievements.map(a => `
            <div class="achievement-card ${a.desbloqueada ? 'unlocked' : 'locked'}">
                <div class="achievement-icon">${a.icone}</div>
                <div class="achievement-title ${a.desbloqueada ? 'text-gold' : ''}">${a.titulo}</div>
                <div class="achievement-desc">${a.descricao}</div>
                <div class="achievement-xp">+${a.xp_recompensa} XP</div>
                ${a.desbloqueada && a.data_desbloqueio ? `
                    <div class="text-muted mt-1" style="font-size: 0.7rem;">
                        <i class='bx bx-check-double'></i> ${new Date(a.data_desbloqueio).toLocaleDateString('pt-BR')}
                    </div>
                ` : ''}
            </div>
        `).join('');
    } catch (error) {
        console.error("Erro ao carregar conquistas", error);
        grid.innerHTML = `<div class="text-center text-red py-2" style="grid-column: 1 / -1;">Erro ao carregar conquistas.</div>`;
    }
}
