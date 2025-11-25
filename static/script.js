// ============================================================================
// SYNAPSE - JAVASCRIPT
// ============================================================================

const API_BASE = 'http://localhost:5000/api';

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    console.log('🧠 Synapse carregado!');
});

// ============================================================================
// NAVEGAÇÃO ENTRE TABS
// ============================================================================

function showTab(tabName) {
    // Remove active de todos os tabs
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Ativa tab selecionada
    event.target.classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Carrega dados se necessário
    if (tabName === 'list') {
        loadAllNotes();
    }
}

// ============================================================================
// ESTATÍSTICAS
// ============================================================================

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('total-notes').textContent = 
                data.stats.total_notes_neo4j || 0;
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// ============================================================================
// CRIAR ANOTAÇÃO
// ============================================================================

async function createNote(event) {
    event.preventDefault();
    
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    const tagsInput = document.getElementById('note-tags').value;
    
    // Processa tags
    const tags = tagsInput
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/notes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, content, tags })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showFeedback('success', '✅ Anotação criada com sucesso!');
            
            // Limpa formulário
            document.getElementById('note-form').reset();
            
            // Atualiza estatísticas
            loadStats();
        } else {
            showFeedback('error', `❌ Erro: ${data.error}`);
        }
    } catch (error) {
        showFeedback('error', `❌ Erro ao criar anotação: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// ============================================================================
// BUSCAR ANOTAÇÕES
// ============================================================================

async function searchNotes() {
    const query = document.getElementById('search-query').value.trim();
    const topK = parseInt(document.getElementById('search-limit').value);
    
    if (!query) {
        alert('Por favor, digite uma consulta!');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query, top_k: topK })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.results, query);
        } else {
            alert(`Erro: ${data.error}`);
        }
    } catch (error) {
        alert(`Erro ao buscar: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function displaySearchResults(results, query) {
    const container = document.getElementById('search-results');
    
    if (results.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <h3>Nenhum resultado encontrado</h3>
                <p>Tente buscar com termos diferentes ou crie uma nova anotação!</p>
            </div>
        `;
        return;
    }
    
    let html = `<h3>Resultados para: "${query}"</h3>`;
    
    results.forEach((note, index) => {
        const score = (note.similarity_score * 100).toFixed(1);
        const tags = note.tags || [];
        
        html += `
            <div class="result-card" style="animation-delay: ${index * 0.1}s">
                <div class="result-header">
                    <h3 class="result-title">${escapeHtml(note.title)}</h3>
                    <span class="similarity-badge">${score}% similar</span>
                </div>
                
                <p class="result-content">${escapeHtml(note.content)}</p>
                
                ${tags.length > 0 ? `
                    <div class="result-tags">
                        ${tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                    </div>
                ` : ''}
                
                <div class="result-meta">
                    📅 ${formatDate(note.created_at)} | 
                    🆔 ${note.id.substring(0, 8)}...
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// ============================================================================
// LISTAR ANOTAÇÕES
// ============================================================================

async function loadAllNotes() {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/notes?limit=100`);
        const data = await response.json();
        
        if (data.success) {
            displayNotesList(data.notes);
        } else {
            alert(`Erro: ${data.error}`);
        }
    } catch (error) {
        alert(`Erro ao carregar anotações: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function displayNotesList(notes) {
    const container = document.getElementById('notes-list');
    
    if (notes.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <h3>Nenhuma anotação ainda</h3>
                <p>Comece criando sua primeira anotação!</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    notes.forEach((note, index) => {
        const tags = note.tags || [];
        
        html += `
            <div class="note-card" style="animation-delay: ${index * 0.05}s">
                <div class="note-card-header">
                    <h3 class="note-card-title">${escapeHtml(note.title)}</h3>
                    <button onclick="deleteNote('${note.id}')" class="btn btn-danger" title="Deletar">
                        🗑️
                    </button>
                </div>
                
                <p class="note-card-content">${escapeHtml(note.content)}</p>
                
                ${tags.length > 0 ? `
                    <div class="result-tags">
                        ${tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                    </div>
                ` : ''}
                
                <div class="result-meta">
                    📅 ${formatDate(note.created_at)}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// ============================================================================
// DELETAR ANOTAÇÃO
// ============================================================================

async function deleteNote(noteId) {
    if (!confirm('Tem certeza que deseja deletar esta anotação?')) {
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/notes/${noteId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Recarrega lista
            loadAllNotes();
            loadStats();
        } else {
            alert(`Erro: ${data.error}`);
        }
    } catch (error) {
        alert(`Erro ao deletar: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// ============================================================================
// UTILS
// ============================================================================

function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'flex' : 'none';
}

function showFeedback(type, message) {
    const feedback = document.getElementById('create-feedback');
    feedback.className = `feedback show ${type}`;
    feedback.textContent = message;
    
    setTimeout(() => {
        feedback.classList.remove('show');
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return dateString;
    }
}

// ============================================================================
// ATALHOS DE TECLADO
// ============================================================================

document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K para focar na busca
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        showTab('search');
        document.getElementById('search-query').focus();
    }
    
    // Ctrl/Cmd + N para nova anotação
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        showTab('create');
        document.getElementById('note-title').focus();
    }
});
