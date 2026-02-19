document.addEventListener('DOMContentLoaded', () => {
    const urlForm = document.getElementById('url-form');
    const urlInput = document.getElementById('url-input');
    const textInput = document.getElementById('text-input');
    const htmlInput = document.getElementById('html-input');
    const imageUpload = document.getElementById('image-upload');
    const imagePreview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    const removeImageBtn = document.getElementById('remove-image');

    const analyzeBtn = document.getElementById('analyze-btn');
    const loadingSpinner = document.getElementById('loading');
    const resultCard = document.getElementById('result-card');

    const omniPlusBtn = document.getElementById('omni-plus-btn');
    const omniMenu = document.getElementById('omni-menu');
    const omniMenuItems = document.querySelectorAll('.omni-menu-item');

    const sidebar = document.querySelector('.sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const navAnalyzer = document.getElementById('nav-analyzer');

    let currentMode = 'url';
    let selectedFile = null;

    // --- Sidebar & Navigation ---
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    document.body.appendChild(overlay);

    // All sidebar toggle buttons (analyzer page + stats page)
    document.querySelectorAll('.sidebar-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const isActive = sidebar.classList.toggle('active');
            overlay.style.display = isActive ? 'block' : 'none';
        });
    });

    overlay.addEventListener('click', () => {
        sidebar.classList.remove('active');
        overlay.style.display = 'none';
    });

    // Close button inside sidebar
    const sidebarClose = document.getElementById('sidebar-close');
    if (sidebarClose) {
        sidebarClose.addEventListener('click', () => {
            sidebar.classList.remove('active');
            overlay.style.display = 'none';
        });
    }

    if (navAnalyzer) {
        navAnalyzer.addEventListener('click', (e) => {
            e.preventDefault();
            showPage('analyzer');
            if (window.innerWidth <= 1024) sidebar.classList.remove('active');
            overlay.style.display = 'none';
        });
    }

    // --- Page Navigation ---
    const analyzerPage = document.querySelector('.main-content:not(#stats-page)');
    const statsPage = document.getElementById('stats-page');
    const navStats = document.getElementById('nav-stats');
    const statsBackBtn = document.getElementById('stats-back-btn');

    function showPage(page) {
        if (page === 'stats') {
            analyzerPage.classList.add('d-none');
            statsPage.classList.remove('d-none');
            navAnalyzer.classList.remove('active');
            navStats.classList.add('active');
            fetchStats();
        } else {
            statsPage.classList.add('d-none');
            analyzerPage.classList.remove('d-none');
            navStats.classList.remove('active');
            navAnalyzer.classList.add('active');
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    if (navStats) {
        navStats.addEventListener('click', (e) => {
            e.preventDefault();
            showPage('stats');
            if (window.innerWidth <= 1024) sidebar.classList.remove('active');
            overlay.style.display = 'none';
        });
    }

    if (statsBackBtn) {
        statsBackBtn.addEventListener('click', () => showPage('analyzer'));
    }

    // --- Omni-Menu Logic ---
    omniPlusBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        omniMenu.classList.toggle('active');
    });

    document.addEventListener('click', () => {
        omniMenu.classList.remove('active');
    });

    omniMenuItems.forEach(item => {
        item.addEventListener('click', () => {
            const mode = item.dataset.mode;
            if (mode) switchMode(mode);
            omniMenu.classList.remove('active');
        });
    });

    function switchMode(mode) {
        currentMode = mode;

        // Hide all
        urlInput.classList.add('d-none');
        textInput.classList.add('d-none');
        htmlInput.classList.add('d-none');

        // Remove 'required' from all
        urlInput.removeAttribute('required');
        textInput.removeAttribute('required');
        htmlInput.removeAttribute('required');

        // Show selected
        if (mode === 'url') {
            urlInput.classList.remove('d-none');
            urlInput.setAttribute('required', '');
            urlInput.focus();
        } else if (mode === 'text') {
            textInput.classList.remove('d-none');
            textInput.setAttribute('required', '');
            textInput.focus();
        } else if (mode === 'html') {
            htmlInput.classList.remove('d-none');
            htmlInput.setAttribute('required', '');
            htmlInput.focus();
        }
    }

    // --- File/Image Handling ---
    imageUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            selectedFile = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
                imagePreview.classList.remove('d-none');
            };
            reader.readAsDataURL(file);
        }
    });

    removeImageBtn.addEventListener('click', () => {
        selectedFile = null;
        imageUpload.value = '';
        imagePreview.classList.add('d-none');
    });

    // --- Analysis Submission ---
    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const url = urlInput.value.trim();
        const text = textInput.value.trim();
        const html = htmlInput.value.trim();

        if (currentMode === 'url' && !url && !selectedFile) return;
        if (currentMode === 'text' && !text) return;
        if (currentMode === 'html' && !html) return;

        // Reset UI
        resultCard.style.display = 'none';
        loadingSpinner.style.display = 'block';
        analyzeBtn.disabled = true;

        try {
            const formData = new FormData();
            if (currentMode === 'url' && url) formData.append('url', url);
            if (currentMode === 'text' && text) formData.append('text', text);
            if (currentMode === 'html' && html) formData.append('html', html);
            if (selectedFile) formData.append('image', selectedFile);

            const response = await fetch('/predict', {
                method: 'POST',
                body: formData // Fetch automatically sets content-type for FormData
            });

            const data = await response.json();

            if (data.error) {
                showError(data.error);
            } else {
                showResult(data);
                fetchHistory();
            }
        } catch (error) {
            showError('Erro ao conectar com o serviço de análise multi-modal.');
            console.error(error);
        } finally {
            loadingSpinner.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    });

    function showResult(data) {
        const isPhishing = data.result === 'Phishing';
        const isSuspect = data.result === 'Suspeito';
        const colorClass = isPhishing ? 'is-phishing' : (isSuspect ? 'text-warning' : 'is-safe');
        const borderColor = isPhishing ? 'var(--danger)' : (isSuspect ? 'orange' : 'var(--success)');
        const icon = isPhishing ? 'fa-shield-virus' : (isSuspect ? 'fa-exclamation-triangle' : 'fa-shield-check');
        const statusText = isPhishing ? 'Potencial Phishing' : (isSuspect ? 'Análise Suspeita' : 'URL Legítima');

        let agentsHtml = '';
        if (data.agent_details) {
            agentsHtml = `
                <div class="mt-4">
                    <h6 class="text-muted mb-3" style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Insights dos Agentes</h6>
                    <div class="d-flex flex-column gap-2">
                        ${data.agent_details.map(agent => `
                            <div class="glass p-2 px-3 rounded-3" style="border-left: 3px solid ${agent.result === 'Phishing' ? 'var(--danger)' : 'var(--success)'}; font-size: 0.85rem;">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <strong>${agent.agent}</strong>
                                    <span class="badge ${agent.result === 'Phishing' ? 'bg-danger' : (agent.result === 'Legítima' || agent.result === 'Safe' ? 'bg-success' : 'bg-secondary')}" style="font-size: 0.65rem;">${agent.result}</span>
                                </div>
                                ${agent.findings && agent.findings.length > 0 ? `
                                    <ul class="mb-0 ps-3 text-muted" style="font-size: 0.75rem;">
                                        ${agent.findings.map(f => `<li>${f}</li>`).join('')}
                                    </ul>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        resultCard.innerHTML = `
            <div class="result-header">
                <div class="status-icon glass ${colorClass}">
                    <i class="fas ${icon}"></i>
                </div>
                <div>
                    <h3 style="color: ${borderColor}">${statusText}</h3>
                    <p class="text-muted" style="font-size: 0.9rem; word-break: break-all;">${data.url}</p>
                </div>
            </div>
            ${data.confidence ? `
                <div class="confidence-meter mt-3">
                    <div class="d-flex justify-content-between mb-2">
                        <span>Score de Risco Consolidado</span>
                        <span>${data.confidence}%</span>
                    </div>
                    <div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;">
                        <div style="width: ${data.confidence}%; height: 100%; background: ${borderColor}; transition: width 1s ease-out;"></div>
                    </div>
                </div>
            ` : ''}
            <div class="mt-4 p-3 glass" style="border-radius: 12px; font-size: 0.85rem; color: var(--text-muted); border-left: 4px solid var(--primary);">
                <i class="fas fa-info-circle me-2"></i>
                Decisão consolidada: <strong>${data.description}</strong>
            </div>
            ${agentsHtml}
        `;
        resultCard.style.display = 'block';
    }

    function showError(message) {
        resultCard.innerHTML = `
            <div class="alert alert-danger glass" style="border-color: var(--danger); color: var(--danger);">
                <i class="fas fa-exclamation-triangle me-2"></i> ${message}
            </div>
        `;
        resultCard.style.display = 'block';
    }

    // --- History Logic ---
    const historyContainer = document.getElementById('history-container');
    const viewMoreContainer = document.getElementById('view-more-container');
    const viewMoreBtn = document.getElementById('view-more-btn');

    let allHistoryItems = [];
    let showingAll = false;

    async function fetchHistory() {
        try {
            const response = await fetch('/history');
            const data = await response.json();
            if (!data.error) {
                allHistoryItems = data;
                renderHistory();
            }
        } catch (error) {
            console.error('Erro ao buscar histórico:', error);
        }
    }

    function renderHistory() {
        if (!allHistoryItems || allHistoryItems.length === 0) {
            historyContainer.innerHTML = `
                <div class="text-center py-5 text-muted glass rounded-4">
                    <i class="fas fa-search mb-2 d-block fs-3"></i>
                    <p class="mb-0">Nenhuma busca recente encontrada.</p>
                </div>
            `;
            viewMoreContainer.classList.add('d-none');
            return;
        }

        const itemsToShow = showingAll ? allHistoryItems : allHistoryItems.slice(0, 2);

        historyContainer.innerHTML = itemsToShow.map(item => {
            const isPhishing = item.result === 'Phishing';
            const isSuspect = item.result === 'Suspeito';
            const colorClass = isPhishing ? 'phishing' : (isSuspect ? 'suspect' : 'safe');

            return `
                <div class="history-item glass" onclick="window.scrollTo({top: 0, behavior: 'smooth'}); switchMode('url'); document.getElementById('url-input').value='${item.url}'">
                    <div class="history-info">
                        <span class="history-url">${item.url}</span>
                        <div class="history-meta">
                            <span class="history-status-dot dot-${colorClass}"></span>
                            <span>${item.result}</span>
                            <span><i class="far fa-clock me-1"></i>${item.timestamp}</span>
                        </div>
                    </div>
                    <div class="history-badge badge-${colorClass}">
                        ${item.result}
                    </div>
                </div>
            `;
        }).join('');

        // Show/hide view more button
        if (allHistoryItems.length > 2) {
            viewMoreContainer.classList.remove('d-none');
            viewMoreBtn.innerHTML = showingAll ?
                'Ver Menos <i class="fas fa-chevron-up ms-1"></i>' :
                `Ver Mais (${allHistoryItems.length - 2} extras) <i class="fas fa-chevron-down ms-1"></i>`;
        } else {
            viewMoreContainer.classList.add('d-none');
        }
    }

    viewMoreBtn.addEventListener('click', () => {
        showingAll = !showingAll;
        renderHistory();
    });

    // --- Statistics Logic ---
    async function fetchStats() {
        try {
            const response = await fetch('/stats');
            const data = await response.json();
            if (!data.error) renderStats(data);
        } catch (error) {
            console.error('Erro ao buscar estatísticas:', error);
        }
    }

    function renderStats(data) {
        // KPI Values
        document.getElementById('stat-total').textContent = data.total;
        document.getElementById('stat-phishing').textContent = data.phishing;
        document.getElementById('stat-safe').textContent = data.safe;
        document.getElementById('stat-rate').textContent = data.detection_rate + '%';

        // Breakdown Bars
        const total = data.total || 1;
        const phishPct = (data.phishing / total * 100).toFixed(0);
        const suspPct = (data.suspect / total * 100).toFixed(0);
        const safePct = (data.safe / total * 100).toFixed(0);

        setTimeout(() => {
            document.getElementById('bar-phishing').style.width = phishPct + '%';
            document.getElementById('bar-suspect').style.width = suspPct + '%';
            document.getElementById('bar-safe').style.width = safePct + '%';
        }, 100);

        document.getElementById('bar-phishing-val').textContent = data.phishing;
        document.getElementById('bar-suspect-val').textContent = data.suspect;
        document.getElementById('bar-safe-val').textContent = data.safe;

        // Timeline
        const timelineEl = document.getElementById('stats-timeline');
        if (data.timeline && data.timeline.length > 0) {
            timelineEl.innerHTML = data.timeline.map(item => {
                const isPhishing = item.result === 'Phishing';
                const isSuspect = item.result === 'Suspeito';
                const color = isPhishing ? 'var(--danger)' : (isSuspect ? '#f59e0b' : 'var(--success)');
                const icon = isPhishing ? 'fa-exclamation-triangle' : (isSuspect ? 'fa-question-circle' : 'fa-check-circle');
                return `
                    <div class="timeline-item" style="border-left-color: ${color};">
                        <i class="fas ${icon}" style="color: ${color};"></i>
                        <span class="text-muted">${item.date}</span>
                        <span style="color: ${color}; font-weight: 600;">${item.result}</span>
                    </div>
                `;
            }).join('');
        } else {
            timelineEl.innerHTML = '<p class="text-muted text-center mb-0">Nenhuma análise registrada ainda.</p>';
        }
    }

    // Initialize
    fetchHistory();
});
