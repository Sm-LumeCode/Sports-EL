// ===== CONFIG =====
const API = window.location.origin;

// ===== STATE =====
let allPlayers = [];
let allPerformances = [];
let deleteTargetId = null;

// ===== DOM REFERENCES =====
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initForms();
    initSearch();
    initModal();
    loadData();
});

// ===== TABS =====
function initTabs() {
    $$('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            $$('.tab-btn').forEach(b => b.classList.remove('active'));
            $$('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const tab = btn.dataset.tab;
            $(`#tab-${tab}`).classList.add('active');
            // Refresh player dropdown when switching to performance tab
            if (tab === 'performance') populatePlayerDropdown();
        });
    });
}

// ===== DATA LOADING =====
async function loadData() {
    try {
        const [playersRes, perfRes] = await Promise.all([
            fetch(`${API}/players/`),
            fetch(`${API}/performances/`)
        ]);
        
        if (playersRes.ok) {
            allPlayers = await playersRes.json();
        } else {
            allPlayers = [];
        }
        
        if (perfRes.ok) {
            allPerformances = await perfRes.json();
        } else {
            allPerformances = [];
        }

        updateStats();
        renderPlayersTable(allPlayers);
        populatePlayerDropdown();
        updateConnectionStatus(true);
    } catch (err) {
        console.error('Failed to load data:', err);
        updateConnectionStatus(false);
        showToast('Cannot connect to API server. Is the backend running?', 'error');
    }
}

function updateConnectionStatus(connected) {
    const badge = $('.status-badge');
    if (connected) {
        badge.innerHTML = '<span class="status-dot"></span> API Connected';
        badge.style.background = 'rgba(16, 185, 129, 0.1)';
        badge.style.color = '#10b981';
        badge.style.borderColor = 'rgba(16, 185, 129, 0.2)';
    } else {
        badge.innerHTML = '<span class="status-dot" style="background:#ef4444"></span> API Offline';
        badge.style.background = 'rgba(239, 68, 68, 0.1)';
        badge.style.color = '#ef4444';
        badge.style.borderColor = 'rgba(239, 68, 68, 0.2)';
    }
}

// ===== STATS =====
function updateStats() {
    animateCounter('statTotalPlayers', allPlayers.length);
    
    const uniqueSports = new Set(allPlayers.map(p => p.sport));
    animateCounter('statSports', uniqueSports.size);
    
    const uniqueTeams = new Set(allPlayers.map(p => p.team));
    animateCounter('statTeams', uniqueTeams.size);
    
    animateCounter('statRecords', allPerformances.length);
}

function animateCounter(elementId, target) {
    const el = document.getElementById(elementId);
    const current = parseInt(el.textContent) || 0;
    if (current === target) return;
    
    const duration = 600;
    const start = performance.now();
    
    function tick(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const value = Math.round(current + (target - current) * eased);
        el.textContent = value;
        if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}

// ===== PLAYER TABLE RENDERING =====
function renderPlayersTable(players) {
    const container = $('#playersTableBody');
    
    if (players.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">👥</div>
                <h3>No players found</h3>
                <p>Add your first player by switching to the "Add Player" tab.</p>
            </div>
        `;
        return;
    }

    const avatarColors = [
        '#6366f1', '#8b5cf6', '#ec4899', '#ef4444', '#f59e0b',
        '#10b981', '#06b6d4', '#3b82f6', '#a855f7', '#14b8a6'
    ];

    const sportClass = (sport) => {
        const s = sport.toLowerCase();
        if (s.includes('football') || s.includes('soccer')) return 'football';
        if (s.includes('basketball')) return 'basketball';
        if (s.includes('cricket')) return 'cricket';
        if (s.includes('tennis')) return 'tennis';
        if (s.includes('rugby')) return 'rugby';
        return 'football';
    };

    const sportEmoji = (sport) => {
        const s = sport.toLowerCase();
        if (s.includes('football') || s.includes('soccer')) return '⚽';
        if (s.includes('basketball')) return '🏀';
        if (s.includes('cricket')) return '🏏';
        if (s.includes('tennis')) return '🎾';
        if (s.includes('rugby')) return '🏈';
        return '🏅';
    };

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Age</th>
                    <th>Sport</th>
                    <th>Position</th>
                    <th>Team</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    players.forEach((player, i) => {
        const initials = player.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        const color = avatarColors[i % avatarColors.length];

        html += `
            <tr>
                <td>
                    <div class="player-name">
                        <div class="player-avatar" style="background:${color}">${initials}</div>
                        <span class="player-name-text">${escapeHtml(player.name)}</span>
                    </div>
                </td>
                <td>${player.age}</td>
                <td><span class="sport-badge ${sportClass(player.sport)}">${sportEmoji(player.sport)} ${escapeHtml(player.sport)}</span></td>
                <td>${escapeHtml(player.position)}</td>
                <td>${escapeHtml(player.team)}</td>
                <td>
                    <div class="action-btns">
                        <button class="action-btn delete" title="Delete player" onclick="openDeleteModal(${player.id}, '${escapeHtml(player.name)}')">🗑️</button>
                    </div>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

// ===== SEARCH =====
function initSearch() {
    $('#searchInput').addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            renderPlayersTable(allPlayers);
            return;
        }
        const filtered = allPlayers.filter(p =>
            p.name.toLowerCase().includes(query) ||
            p.sport.toLowerCase().includes(query) ||
            p.position.toLowerCase().includes(query) ||
            p.team.toLowerCase().includes(query)
        );
        renderPlayersTable(filtered);
    });
}

// ===== FORMS =====
function initForms() {
    // Add Player form
    $('#addPlayerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = $('#submitPlayerBtn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Saving...';

        const payload = {
            name: $('#playerName').value.trim(),
            age: parseInt($('#playerAge').value),
            sport: $('#playerSport').value,
            position: $('#playerPosition').value.trim(),
            team: $('#playerTeam').value.trim()
        };

        try {
            const res = await fetch(`${API}/players/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                showToast(`${payload.name} registered successfully!`, 'success');
                $('#addPlayerForm').reset();
                await loadData();
                // Switch to roster tab
                $$('.tab-btn')[0].click();
            } else {
                const err = await res.text();
                showToast(`Error: ${err}`, 'error');
            }
        } catch (err) {
            showToast('Network error. Is the API running?', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '➕ Register Player';
        }
    });

    $('#resetPlayerForm').addEventListener('click', () => {
        $('#addPlayerForm').reset();
    });

    // Performance form
    $('#perfForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = $('#submitPerfBtn');
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Saving...';

        const payload = {
            player_id: parseInt($('#perfPlayerId').value),
            matches_played: parseInt($('#perfMatches').value) || 0,
            minutes_played: parseInt($('#perfMinutes').value) || 0,
            goals: parseInt($('#perfGoals').value) || 0,
            assists: parseInt($('#perfAssists').value) || 0,
            accuracy: parseFloat($('#perfAccuracy').value) || 0,
            efficiency: parseFloat($('#perfEfficiency').value) || 0,
            win_contribution: parseFloat($('#perfWinContrib').value) || 0
        };

        try {
            const res = await fetch(`${API}/performances/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                showToast('Performance record saved!', 'success');
                $('#perfForm').reset();
                await loadData();
            } else {
                const err = await res.text();
                showToast(`Error: ${err}`, 'error');
            }
        } catch (err) {
            showToast('Network error. Is the API running?', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '📊 Save Record';
        }
    });

    $('#resetPerfForm').addEventListener('click', () => {
        $('#perfForm').reset();
    });
}

// ===== PLAYER DROPDOWN =====
function populatePlayerDropdown() {
    const select = $('#perfPlayerId');
    const currentVal = select.value;
    select.innerHTML = '<option value="">Choose a player...</option>';
    allPlayers.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.id;
        opt.textContent = `${p.name} — ${p.team} (${p.sport})`;
        select.appendChild(opt);
    });
    if (currentVal) select.value = currentVal;
}

// ===== DELETE MODAL =====
function initModal() {
    $('#cancelDelete').addEventListener('click', closeDeleteModal);
    $('#deleteModal').addEventListener('click', (e) => {
        if (e.target === $('#deleteModal')) closeDeleteModal();
    });
    $('#confirmDelete').addEventListener('click', confirmDeletePlayer);
}

function openDeleteModal(id, name) {
    deleteTargetId = id;
    $('#deletePlayerName').textContent = name;
    $('#deleteModal').classList.add('active');
}

function closeDeleteModal() {
    $('#deleteModal').classList.remove('active');
    deleteTargetId = null;
}

async function confirmDeletePlayer() {
    if (!deleteTargetId) return;
    const btn = $('#confirmDelete');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>';

    try {
        const res = await fetch(`${API}/players/${deleteTargetId}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Player removed from roster.', 'success');
            closeDeleteModal();
            await loadData();
        } else {
            showToast('Failed to delete player.', 'error');
        }
    } catch (err) {
        showToast('Network error.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🗑️ Delete';
    }
}

// ===== TOASTS =====
function showToast(message, type = 'info') {
    const container = $('#toastContainer');
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'toastSlideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ===== UTILITIES =====
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
