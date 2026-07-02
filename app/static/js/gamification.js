/**
 * Sales Quest — Gamification Animations & Overlays
 */
const gamification = {
    // ─── Animação de XP Flutuante ───
    showFloatingXP(amount) {
        // Cria elemento de texto
        const el = document.createElement('div');
        el.className = 'xp-float-text';
        el.textContent = `+${amount} XP`;

        // Posição no centro da tela (um pouco acima)
        el.style.left = '50%';
        el.style.top = '40%';
        el.style.transform = 'translate(-50%, -50%)';

        document.body.appendChild(el);

        // Toca som suave (opcional - aqui só UI)

        // Remove após a animação (1.5s)
        setTimeout(() => el.remove(), 1500);
    },
    // ─── Level Up Overlay ───
    showLevelUp(newLevel, title) {
        const overlay = document.getElementById('levelUpOverlay');
        const text = document.getElementById('levelUpText');
        const subtitle = document.getElementById('levelUpSubtitle');

        if (!overlay) return;
        subtitle.textContent = `Você alcançou o Nível ${newLevel} • ${title}`;
        overlay.classList.add('active');

        // Confetti effect (se tivéssemos a lib, chamaria aqui)

        // Fecha clicando em qualquer lugar
        const closeHandler = () => {
            overlay.classList.remove('active');
            overlay.removeEventListener('click', closeHandler);
        };
        overlay.addEventListener('click', closeHandler);

        // Auto-close após 4 segundos
        setTimeout(() => {
            if (overlay.classList.contains('active')) {
                overlay.classList.remove('active');
                overlay.removeEventListener('click', closeHandler);
            }
        }, 4000);
    },
    // ─── Processa Resultados da API ───
    processRewards(xpResult, completedMissions, newAchievements) {
        // 1. XP Ganho
        if (xpResult && xpResult.xp_ganho > 0) {
            // Pequeno delay para a UI respirar
            setTimeout(() => {
                this.showFloatingXP(xpResult.xp_ganho);
                app.toast('XP Ganho!', `+${xpResult.xp_ganho} XP adicionados.`, 'xp');
            }, 300);
        }
        // 2. Missões Completas
        if (completedMissions && completedMissions.length > 0) {
            let delay = 1000; // Delay após o XP
            completedMissions.forEach(mission => {
                setTimeout(() => {
                    app.toast(
                        'Missão Concluída!',
                        `${mission.icone} ${mission.titulo} (+${mission.xp} XP)`,
                        'success'
                    );
                }, delay);
                delay += 1500;
            });
        }
        // 3. Novas Conquistas
        if (newAchievements && newAchievements.length > 0) {
            let delay = completedMissions && completedMissions.length > 0 ? 2500 : 1000;
            newAchievements.forEach(ach => {
                setTimeout(() => {
                    app.toast(
                        'Conquista Desbloqueada!',
                        `${ach.icone} ${ach.titulo} (+${ach.xp} XP)`,
                        'achievement'
                    );
                }, delay);
                delay += 1500;
            });
        }
        // 4. Level Up (O mais importante, vai por cima)
        if (xpResult && xpResult.level_up) {
            setTimeout(() => {
                this.showLevelUp(xpResult.nivel_atual, xpResult.titulo);
                app.loadUserSidebar(); // Atualiza a sidebar
            }, 800);
        }
    }
};
