/**
 * Sales Quest — Clients CRUD Logic
 */
let searchTimeout = null;
document.addEventListener('DOMContentLoaded', () => {
    if (app.isAuthenticated()) {
        loadClients();
    }
});
async function loadClients(searchQuery = '') {
    const tbody = document.getElementById('clientsTableBody');
    try {
        const data = await app.api(`/clients?search=${encodeURIComponent(searchQuery)}`);

        if (data.clients.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5">
                        <div class="empty-state">
                            <div class="empty-icon"><i class='bx bx-user-x'></i></div>
                            <p>${searchQuery ? 'Nenhum cliente encontrado.' : 'Você ainda não possui clientes cadastrados.'}</p>
                            ${!searchQuery ? `<button class="btn btn-primary mt-1" onclick="openClientModal()">Cadastrar Primeiro Cliente</button>` : ''}
                        </div>
                    </td>
                </tr>
            `;
            return;
        }
        tbody.innerHTML = data.clients.map(c => `
            <tr>
                <td>
                    <div class="fw-700">${c.nome}</div>
                    <div class="text-muted" style="font-size: 0.8rem;">Cadastrado em: ${new Date(c.created_at).toLocaleDateString('pt-BR')}</div>
                </td>
                <td>
                    ${c.email ? `<div><i class='bx bx-envelope text-muted'></i> ${c.email}</div>` : ''}
                    ${c.telefone ? `<div><i class='bx bx-phone text-muted'></i> ${c.telefone}</div>` : ''}
                    ${!c.email && !c.telefone ? '<span class="text-muted">-</span>' : ''}
                </td>
                <td>
                    ${c.endereco ? `<i class='bx bx-map text-muted'></i> ${c.endereco}` : '<span class="text-muted">-</span>'}
                </td>
                <td>
                    <div class="fw-700 text-accent">${c.total_vendas} vendas</div>
                    <div style="font-size: 0.85rem;">R$ ${c.valor_total.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
                </td>
                <td>
                    <div class="table-actions">
                        <button class="btn btn-secondary btn-icon" title="Editar" onclick="editClient(${c.id})">
                            <i class='bx bx-edit'></i>
                        </button>
                        <button class="btn btn-secondary btn-icon text-red" style="color: #ff6b6b;" title="Excluir" onclick="deleteClient(${c.id})">
                            <i class='bx bx-trash'></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error("Erro ao carregar clientes", error);
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-red">Erro ao carregar dados.</td></tr>`;
    }
}
function debounceSearch() {
    clearTimeout(searchTimeout);
    const searchVal = document.getElementById('searchInput').value;
    searchTimeout = setTimeout(() => {
        loadClients(searchVal);
    }, 500);
}
// ─── Modal ───
function openClientModal() {
    document.getElementById('clientForm').reset();
    document.getElementById('clientId').value = '';
    document.getElementById('modalTitle').textContent = 'Novo Cliente';
    document.getElementById('clientModal').classList.add('active');
}
function closeClientModal() {
    document.getElementById('clientModal').classList.remove('active');
}
async function saveClient(event) {
    event.preventDefault();

    const id = document.getElementById('clientId').value;
    const isEdit = !!id;

    const payload = {
        nome: document.getElementById('clientName').value,
        email: document.getElementById('clientEmail').value || null,
        telefone: document.getElementById('clientPhone').value || null,
        endereco: document.getElementById('clientAddress').value || null,
        notas: document.getElementById('clientNotes').value || null
    };
    const btn = event.target.querySelector('button[type="submit"]');
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "<i class='bx bx-loader-alt bx-spin'></i> Salvando...";
    try {
        let result;
        if (isEdit) {
            result = await app.api(`/clients/${id}`, {
                method: 'PUT',
                body: JSON.stringify(payload)
            });
            app.toast('Sucesso', 'Cliente atualizado.', 'success');
        } else {
            result = await app.api('/clients', {
                method: 'POST',
                body: JSON.stringify(payload)
            });
            app.toast('Sucesso', 'Cliente cadastrado com sucesso!', 'success');

            // Processa conquistas se for novo cliente (gamification)
            if (result.conquistas) {
                gamification.processRewards(null, null, result.conquistas);
            }
        }

        closeClientModal();
        loadClients(document.getElementById('searchInput').value);

    } catch (error) {
        app.toast('Erro', error.data?.detail || 'Falha ao salvar cliente.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHtml;
    }
}
async function editClient(id) {
    try {
        const client = await app.api(`/clients/${id}`);

        document.getElementById('clientId').value = client.id;
        document.getElementById('clientName').value = client.nome;
        document.getElementById('clientEmail').value = client.email || '';
        document.getElementById('clientPhone').value = client.telefone || '';
        document.getElementById('clientAddress').value = client.endereco || '';
        document.getElementById('clientNotes').value = client.notas || '';

        document.getElementById('modalTitle').textContent = 'Editar Cliente';
        document.getElementById('clientModal').classList.add('active');
    } catch (error) {
        app.toast('Erro', 'Falha ao carregar dados do cliente.', 'error');
    }
}
async function deleteClient(id) {
    if (!confirm("Tem certeza que deseja excluir este cliente? O histórico de vendas será mantido, mas o cliente será desativado.")) return;

    try {
        await app.api(`/clients/${id}`, { method: 'DELETE' });
        app.toast('Sucesso', 'Cliente excluído.', 'success');
        loadClients(document.getElementById('searchInput').value);
    } catch (error) {
        app.toast('Erro', 'Falha ao excluir cliente.', 'error');
    }
}
