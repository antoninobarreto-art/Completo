// RioAiki Application Interactive Javascript

document.addEventListener('DOMContentLoaded', () => {
    initReloadLogout();
    initThemeToggle();
    initFilters();
    initModals();
});

// Theme Toggle Functionality (Claro / Escuro com persistência localStorage)
function initThemeToggle() {
    const toggleBtn = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
    
    // Read saved theme or default to dark
    const savedTheme = localStorage.getItem('rioaiki_theme') || 'dark';
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        if (icon) icon.className = 'fa-solid fa-sun';
    } else {
        if (icon) icon.className = 'fa-solid fa-moon';
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            document.body.classList.toggle('light-theme');
            const isLight = document.body.classList.contains('light-theme');
            localStorage.setItem('rioaiki_theme', isLight ? 'light' : 'dark');
            if (icon) {
                icon.className = isLight ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
            }
        });
    }
}

// Generic Modal Handling
function initModals() {
    document.querySelectorAll('[data-modal]').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = trigger.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            if (modal) modal.classList.add('active');
        });
    });

    document.querySelectorAll('.modal-close, .modal-backdrop').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            if (e.target === closeBtn) {
                closeBtn.closest('.modal-backdrop').classList.remove('active');
            }
        });
    });
}

// Filters logic for pages
function initFilters() {
    const searchInput = document.getElementById('search-filter');
    const dojoFilter = document.getElementById('dojo-filter');
    const roleFilter = document.getElementById('role-filter');
    const statusFilter = document.getElementById('status-filter');
    const categoryFilter = document.getElementById('category-filter');

    const filterableCards = document.querySelectorAll('.filterable-item');

    function applyFilters() {
        const query = searchInput ? searchInput.value.toLowerCase() : '';
        const dojoVal = dojoFilter ? dojoFilter.value : 'all';
        const roleVal = roleFilter ? roleFilter.value : 'all';
        const statusVal = statusFilter ? statusFilter.value : 'all';
        const categoryVal = categoryFilter ? categoryFilter.value : 'all';

        filterableCards.forEach(card => {
            const text = card.textContent.toLowerCase();
            const cardDojo = card.getAttribute('data-dojo') || 'all';
            const cardRole = card.getAttribute('data-role') || 'all';
            const cardStatus = card.getAttribute('data-status') || 'all';
            const cardCategory = card.getAttribute('data-category') || 'all';

            const matchQuery = !query || text.includes(query);
            const matchDojo = dojoVal === 'all' || cardDojo === dojoVal;
            const matchRole = roleVal === 'all' || cardRole === roleVal;
            const matchStatus = statusVal === 'all' || cardStatus === statusVal;
            const matchCategory = categoryVal === 'all' || cardCategory === categoryVal;

            if (matchQuery && matchDojo && matchRole && matchStatus && matchCategory) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    [searchInput, dojoFilter, roleFilter, statusFilter, categoryFilter].forEach(el => {
        if (el) el.addEventListener('input', applyFilters);
        if (el) el.addEventListener('change', applyFilters);
    });
}

// API Action: Approve Guest Request
async function approveGuestRequest(approvalId, status) {
    try {
        const response = await fetch(`/api/guest-approvals/${approvalId}/status?status=${status}`, {
            method: 'POST'
        });
        if (response.ok) {
            window.location.reload();
        } else {
            alert('Erro ao atualizar aprovação de aluno convidado.');
        }
    } catch (err) {
        console.error(err);
        alert('Erro na requisição.');
    }
}

// API Action: Approve Classified
async function approveClassified(classifiedId, status) {
    try {
        const formData = new FormData();
        formData.append('status', status);
        const response = await fetch(`/api/classifieds/${classifiedId}/status`, {
            method: 'POST',
            body: formData
        });
        if (response.ok) {
            window.location.reload();
        } else {
            const errData = await response.json().catch(() => ({}));
            alert(errData.error || 'Erro ao atualizar anúncio.');
        }
    } catch (err) {
        console.error(err);
        alert('Erro na requisição.');
    }
}

// API Action: Toggle Student Active Status
async function toggleUserStatus(userId, currentStatus) {
    try {
        const newStatus = !currentStatus;
        const response = await fetch(`/api/users/${userId}/toggle-status?is_active=${newStatus}`, {
            method: 'POST'
        });
        if (response.ok) {
            window.location.reload();
        } else {
            alert('Erro ao alterar status do usuário.');
        }
    } catch (err) {
        console.error(err);
        alert('Erro de rede.');
    }
}

// Client-Side File Size Validation (Boas Práticas de Mercado)
function validateFileSize(inputElement, maxMB) {
    if (inputElement.files && inputElement.files[0]) {
        const file = inputElement.files[0];
        const maxBytes = maxMB * 1024 * 1024;
        if (file.size > maxBytes) {
            alert(`⚠️ Arquivo muito grande!\nO arquivo "${file.name}" tem ${(file.size / (1024 * 1024)).toFixed(2)} MB, que excede o limite máximo permitido de ${maxMB} MB.\n\nPor favor, escolha um arquivo menor.`);
            inputElement.value = ''; // Limpa a seleção
        }
    }
}

// Toggle Inline Single Class Guest Student Input
function toggleSingleClassGuestInput() {
    const panel = document.getElementById('single-class-guest-panel');
    const input = document.getElementById('single-guest-name-input');
    if (panel) {
        if (panel.style.display === 'none' || !panel.style.display) {
            panel.style.display = 'block';
            if (input) input.focus();
        } else {
            panel.style.display = 'none';
        }
    }
}

// Photo Insertion Method Switcher (Upload, URL, Paste, Webcam)
function switchPhotoMethod(selectElement) {
    const parent = selectElement.closest('.form-group') || selectElement.parentElement;
    const selected = selectElement.value;

    parent.querySelectorAll('.photo-method-panel').forEach(panel => {
        panel.style.display = 'none';
    });

    const activePanel = parent.querySelector(`.panel-${selected}`);
    if (activePanel) {
        activePanel.style.display = 'block';
    }
}

// Handle Clipboard Paste (Cut & Paste / Copiar e Colar Imagem)
function handleImagePaste(event, dropzone) {
    const items = (event.clipboardData || event.originalEvent.clipboardData).items;
    for (let index in items) {
        const item = items[index];
        if (item.kind === 'file' && item.type.startsWith('image/')) {
            const blob = item.getAsFile();
            const reader = new FileReader();
            reader.onload = function(e) {
                const base64Data = e.target.result;
                const hiddenInput = dropzone.querySelector('.paste-base64-input');
                const previewDiv = dropzone.querySelector('.paste-preview');
                if (hiddenInput) hiddenInput.value = base64Data;
                if (previewDiv) {
                    previewDiv.innerHTML = `<div style="display: flex; align-items: center; gap: 0.5rem; color: var(--accent-emerald); font-size: 0.8rem; font-weight: 700;">
                        <i class="fa-solid fa-circle-check"></i> Imagem Colada da Área de Transferência!
                    </div><img src="${base64Data}" style="max-height: 90px; border-radius: 8px; margin-top: 0.4rem; border: 2px solid var(--accent-emerald);">`;
                    previewDiv.style.display = 'block';
                }
            };
            reader.readAsDataURL(blob);
            event.preventDefault();
            break;
        }
    }
}

// Webcam Capture Helper
let activeStream = null;
async function startWebcam(btn) {
    const container = btn.closest('.photo-method-panel').querySelector('.webcam-container');
    const video = container.querySelector('.webcam-video');
    try {
        activeStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = activeStream;
        container.style.display = 'block';
        btn.style.display = 'none';
    } catch (err) {
        alert("⚠️ Não foi possível acessar a câmera. Verifique se o navegador possui permissão de uso da webcam.");
    }
}

function captureWebcam(btn) {
    const panel = btn.closest('.photo-method-panel');
    const video = panel.querySelector('.webcam-video');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const base64Data = canvas.toDataURL('image/jpeg');

    const form = btn.closest('form');
    let hiddenInput = form.querySelector('input[name="photo_base64"]');
    if (!hiddenInput) {
        hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'photo_base64';
        form.appendChild(hiddenInput);
    }
    hiddenInput.value = base64Data;

    if (activeStream) {
        activeStream.getTracks().forEach(track => track.stop());
    }

    panel.querySelector('.webcam-container').style.display = 'none';
    panel.innerHTML = `<div style="display: flex; align-items: center; gap: 0.5rem; color: var(--accent-emerald); font-weight: 700; padding: 0.5rem; background: rgba(16, 185, 129, 0.1); border-radius: 6px;">
        <i class="fa-solid fa-camera"></i> Foto Capturada com Sucesso da Câmera!
    </div><img src="${base64Data}" style="max-height: 90px; border-radius: 8px; margin-top: 0.4rem; border: 2px solid var(--accent-emerald);">`;
}

// Dynamic Grid Column Selector (1, 2, 3, 4, 5 columns)
function changeGridColumns(gridId, selectElement) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    const count = selectElement.value;
    grid.className = grid.className.replace(/\bgrid-cols-\d\b/g, '').trim();
    grid.classList.add(`grid-cols-${count}`);
}

// Tab Switching for Management (Dojos, Senseis, Alunos)
function switchManagementTab(tabName) {
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.style.display = 'none';
    });
    document.querySelectorAll('.subnav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    const activePane = document.getElementById(`tab-pane-${tabName}`);
    if (activePane) activePane.style.display = 'block';
    
    const activeTabBtn = document.getElementById(`tab-btn-${tabName}`);
    if (activeTabBtn) activeTabBtn.classList.add('active');
}

// Auto Logout on Page Reload / F5 / Ctrl+R / Cmd+R
function initReloadLogout() {
    if (window.location.pathname === '/login') return;

    // Check if page was reloaded (F5, Ctrl+R, or Refresh button)
    const navEntries = performance.getEntriesByType('navigation');
    if (navEntries.length > 0 && navEntries[0].type === 'reload') {
        window.location.href = '/logout';
        return;
    }

    // Intercept keyboard shortcuts for Refresh (F5, Ctrl+R, Cmd+R)
    window.addEventListener('keydown', (e) => {
        if (e.key === 'F5' || (e.ctrlKey && (e.key === 'r' || e.key === 'R')) || (e.metaKey && (e.key === 'r' || e.key === 'R'))) {
            e.preventDefault();
            window.location.href = '/logout';
        }
    });
}

// Password Visibility Toggle
function togglePasswordVisibility(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (input && icon) {
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
            icon.style.color = 'var(--accent-cyan)';
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
            icon.style.color = 'var(--text-dim)';
        }
    }
}

