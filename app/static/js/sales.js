/**
 * Sales Quest — Sales Logic
 */
let searchTimeout = null;
document.addEventListener('DOMContentLoaded', async () => {
    if (!app.isAuthenticated()) return;

    // Carrega filtros primeiro
    await loadCategories();

    // Carrega vendas
    loadSales();
});
async function loadCategories() {
    try {
        const data = await app.api('/sales/stats');
        const select = document.getElementById('categoryFilter');
        const datalist = document.getElementById('categoriesList');

        if (data.all_categories) {
            // Fill filter select
            data.all_categories.forEach(cat => {
                const opt = document.createElement('option');
                opt.value = cat;
                opt.textContent = cat;
                select.appendChild(opt);
            });

            // Fill datalist for new sales
            if (datalist) {
                datalist.innerHTML = data.all_categories.map(cat => `<option value="${cat}">`).join('');
            }
        }
    } catch (e) {
        console.error("Erro ao carregar categorias", e);
    }
}
async function loadSales(searchQuery = '') {
    const tbody = document.getElementById('salesTableBody');
    const category = document.getElementById('categoryFilter').value;

    try {
        let url = `/sales?search=${encodeURIComponent(searchQuery)}`;
        if (category) url += `&categoria=${encodeURIComponent(category)}`;

        const data = await app.api(url);

        if (data.sales.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5">
                        <div class="empty-state">
                            <div class="empty-icon"><i class='bx bx-shopping-bag'></i></div>
                            <p>${searchQuery || category ? 'Nenhuma venda encontrada com estes filtros.' : 'Você ainda não realizou nenhuma venda.'}</p>
                            ${(!searchQuery && !category) ? `<button class="btn btn-primary mt-1" onclick="openSaleModal()">Cadastrar Primeira Venda</button>` : ''}
                        </div>
                    </td>
                </tr>
            `;
            return;
        }
        tbody.innerHTML = data.sales.map(s => `
            <tr>
                <td>
                    <div class="fw-700">${new Date(s.data_venda).toLocaleDateString('pt-BR')}</div>
                    <div class="text-muted" style="font-size: 0.8rem;">${new Date(s.data_venda).toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'})}</div>
                </td>
                <td>
                    <div class="fw-700">${s.produto}</div>
                    <div class="text-primary-color" style="font-size: 0.85rem;"><i class='bx bx-purchase-tag'></i> ${s.categoria}</div>
                </td>
                <td>
                    ${s.client_nome ? `<i class='bx bx-user text-muted'></i> ${s.client_nome}` : '<span class="text-muted">Sem cliente vinculado</span>'}
                </td>
                <td class="text-center">${s.quantidade}x</td>
                <td>
                    <div class="fw-800 text-accent" style="font-size: 1.1rem;">R$ ${(s.valor * s.quantidade).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
                    <div class="text-muted" style="font-size: 0.8rem;">(R$ ${s.valor.toLocaleString('pt-BR', {minimumFractionDigits: 2})} un.)</div>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error("Erro ao carregar vendas", error);
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-red">Erro ao carregar dados.</td></tr>`;
    }
}
function debounceSearch() {
    clearTimeout(searchTimeout);
    const searchVal = document.getElementById('searchInput').value;
    searchTimeout = setTimeout(() => {
        loadSales(searchVal);
    }, 500);
}
// ─── Modal Venda ───
async function openSaleModal() {
    document.getElementById('saleForm').reset();

    // Carrega clientes para o select
    try {
        const clientSelect = document.getElementById('saleClient');
        clientSelect.innerHTML = '<option value="">(Carregando clientes...)</option>';

        const data = await app.api('/clients?search='); // Pega todos

        let options = '<option value="">(Sem cliente vinculado)</option>';
        data.clients.forEach(c => {
            options += `<option value="${c.id}">${c.nome}</option>`;
        });
        clientSelect.innerHTML = options;

    } catch (e) {
        console.error("Erro ao carregar clientes pro select", e);
    }

    document.getElementById('saleModal').classList.add('active');
}
function closeSaleModal() {
    document.getElementById('saleModal').classList.remove('active');
}
async function saveSale(event) {
    event.preventDefault();

    const clientId = document.getElementById('saleClient').value;

    const payload = {
        client_id: clientId ? parseInt(clientId) : null,
        produto: document.getElementById('saleProduct').value,
        categoria: document.getElementById('saleCategory').value,
        quantidade: parseInt(document.getElementById('saleQuantity').value),
        valor: parseFloat(document.getElementById('saleValue').value)
    };
    const btn = event.target.querySelector('button[type="submit"]');
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "<i class='bx bx-loader-alt bx-spin'></i> Processando...";
    try {
        const result = await app.api('/sales', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        closeSaleModal();

        // Recarrega lista
        loadSales(document.getElementById('searchInput').value);

        // Processa recompensas (XP, Missões, Conquistas)
        gamification.processRewards(result.xp, result.missoes_completas, result.conquistas);

    } catch (error) {
        app.toast('Erro', error.data?.detail || 'Falha ao registrar venda.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHtml;
    }
}
