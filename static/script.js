document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const mainInput = document.getElementById('main-input');
    const analysisForm = document.getElementById('analysis-form');
    const chatWrapper = document.getElementById('chat-wrapper');
    const welcomeSection = document.getElementById('welcome-section');
    const chatMessages = document.getElementById('chat-messages');
    const resultTemplate = document.getElementById('result-template');

    const sidebar = document.querySelector('.sidebar');
    const newChatBtn = document.getElementById('new-chat-btn');
    const historyList = document.getElementById('history-list');
    const sidebarToggle = document.querySelector('.btn-sidebar-toggle');

    const imgBtn = document.querySelector('.btn-plus');
    const imgInput = document.getElementById('image-upload');

    // --- Model Selection ---
    let selectedModel = 'ollama';
    const modelDropdownItems = document.querySelectorAll('.dropdown-item[data-model]');
    const activeModelName = document.getElementById('active-model-name');

    modelDropdownItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            selectedModel = item.getAttribute('data-model');

            // Update UI
            modelDropdownItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            const friendlyName = item.querySelector('.fw-bold').innerText;
            activeModelName.innerText = friendlyName.split(' ')[0]; // Show "Ollama" or "OpenAI"

            if (window.lucide) lucide.createIcons();
        });
    });

    // --- Sidebar Toggle ---
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.add('collapsed');
        });
    }

    const showSidebarBtn = document.createElement('button');
    showSidebarBtn.className = 'btn btn-show-sidebar';
    showSidebarBtn.innerHTML = '<i data-lucide="sidebar"></i>';
    document.querySelector('.main-content').appendChild(showSidebarBtn);
    if (window.lucide) lucide.createIcons();

    showSidebarBtn.addEventListener('click', () => {
        sidebar.classList.remove('collapsed');
    });

    // --- Header Controls (Language & Dark Mode) ---
    const darkBtn = document.getElementById('dark-mode-btn');
    const langBtn = document.getElementById('lang-toggle-btn');
    const welcomeTitle = document.querySelector('.welcome-section-gpt h1');

    // Dark Mode
    if (darkBtn) {
        darkBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            darkBtn.innerHTML = isDark ? '<i data-lucide="sun"></i>' : '<i data-lucide="moon"></i>';
            if (window.lucide) lucide.createIcons();
        });
    }

    // Language
    let currentLang = 'PT';
    if (langBtn) {
        langBtn.addEventListener('click', () => {
            currentLang = currentLang === 'PT' ? 'EN' : 'PT';
            langBtn.querySelector('span').innerText = currentLang;

            // Update UI Text
            if (currentLang === 'EN') {
                if (welcomeTitle) welcomeTitle.innerText = "How can I help?";
                mainInput.placeholder = "Ask anything...";
                newChatBtn.setAttribute('title', 'New Chat');
            } else {
                if (welcomeTitle) welcomeTitle.innerText = "Como posso ajudar?";
                mainInput.placeholder = "Pergunte alguma coisa";
                newChatBtn.setAttribute('title', 'Novo Chat');
            }
        });
    }

    // --- Auto-expanding Textarea ---
    mainInput.addEventListener('input', () => {
        mainInput.style.height = 'auto';
        mainInput.style.height = (mainInput.scrollHeight) + 'px';
    });

    // --- Image Upload (Triggered by Plus icon) ---
    if (imgBtn) {
        imgBtn.addEventListener('click', () => imgInput.click());
    }

    // --- Image Upload (Triggered by Plus icon or Paste) ---
    if (imgBtn) {
        imgBtn.addEventListener('click', () => imgInput.click());
    }

    const currentModeBadge = document.getElementById('current-mode-badge');
    const modeBadgesContainer = document.querySelector('.mode-badges');

    function updateImageBadge(fileName) {
        if (fileName) {
            modeBadgesContainer.classList.remove('d-none');
            currentModeBadge.innerHTML = `<i data-lucide="image" class="me-1 h-12 w-12"></i> ${fileName}`;
            currentModeBadge.classList.replace('bg-light', 'bg-primary');
            currentModeBadge.classList.replace('text-dark', 'text-white');
        } else {
            modeBadgesContainer.classList.add('d-none');
            currentModeBadge.innerHTML = 'Modo: URL';
            currentModeBadge.classList.replace('bg-primary', 'bg-light');
            currentModeBadge.classList.replace('text-white', 'text-dark');
        }
        if (window.lucide) lucide.createIcons();
    }

    imgInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            updateImageBadge(file.name);
        }
    });

    // Support for Pasting Images (Ctrl+V)
    mainInput.addEventListener('paste', (e) => {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const blob = items[i].getAsFile();

                // Assign to file input using DataTransfer
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(blob);
                imgInput.files = dataTransfer.files;

                updateImageBadge("Imagem colada");
                e.preventDefault(); // Don't paste the image text/junk if any
                break;
            }
        }
    });

    // --- New Chat Reset ---
    newChatBtn.addEventListener('click', () => {
        welcomeSection.style.display = 'block';
        chatMessages.innerHTML = '';
        mainInput.value = '';
        mainInput.style.height = 'auto';
    });

    let hasContext = false;

    // --- Form Submission ---
    analysisForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userInput = mainInput.value.trim();
        const hasImage = imgInput.files.length > 0;

        if (!userInput && !hasImage) return;

        // Transitions
        welcomeSection.style.display = 'none';

        // Use standard ChatGPT-style User Message
        if (hasImage) {
            const file = imgInput.files[0];
            const reader = new FileReader();
            reader.onload = (event) => {
                appendUserMessage(userInput || "[Análise de Imagem]", event.target.result);
            };
            reader.readAsDataURL(file);
        } else {
            appendUserMessage(userInput);
        }

        mainInput.value = '';
        mainInput.style.height = 'auto';
        imgInput.value = ''; // Clear file input after use
        updateImageBadge(null); // Clear the UI badge

        // Logic: Is this a scan or a question?
        const isUrl = /^(http|https):\/\/[^ "]+$/.test(userInput);
        const isLongText = userInput.length > 60;

        // If we have context and it looks like a question, call /chat
        if (hasContext && !isUrl && !isLongText && !hasImage) {
            const loadingId = appendLoadingMessage();
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: userInput,
                        model: selectedModel
                    })
                });
                const data = await response.json();
                removeLoadingMessage(loadingId);
                if (data.answer) {
                    appendAiMessage(data.answer);
                } else {
                    throw new Error(data.error || "Sem resposta");
                }
            } catch (err) {
                removeLoadingMessage(loadingId);
                appendAiMessage("Erro no chat: " + err.message);
            }
            return;
        }

        // Otherwise, it's a new analysis (Scan)
        const formData = new FormData();
        if (isUrl) formData.append('url', userInput);
        else formData.append('text', userInput);
        if (hasImage) formData.append('image', imgInput.files[0]);
        formData.append('model', selectedModel);

        const loadingId = appendLoadingMessage();
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            removeLoadingMessage(loadingId);

            if (data.error) throw new Error(data.error);

            showResultCard(data);
            hasContext = true; // Set context after first successful scan
            loadHistory();
        } catch (err) {
            removeLoadingMessage(loadingId);
            appendAiMessage("Erro na análise: " + err.message);
        }
    });

    function appendUserMessage(text, imgSrc = null) {
        const div = document.createElement('div');
        div.className = 'message-bubble-user-gpt mb-4 px-4 text-end';

        let content = `<span class="bg-light p-3 rounded-4 d-inline-block shadow-sm" style="max-width: 80%; text-align: left;">`;
        if (imgSrc) {
            content += `<img src="${imgSrc}" class="img-fluid rounded-3 mb-2 d-block" style="max-height: 200px; width: auto;">`;
        }
        content += `${text}</span>`;

        div.innerHTML = content;
        chatMessages.appendChild(div);
        scrollToBottom();
    }

    function appendAiMessage(text) {
        const div = document.createElement('div');
        div.className = 'result-entry-gpt mb-5';
        div.innerHTML = `
            <div class="gpt-avatar"><i data-lucide="shield-check"></i></div>
            <div class="gpt-response-content mt-1" style="line-height: 1.6;">${text}</div>
        `;
        chatMessages.appendChild(div);
        if (window.lucide) lucide.createIcons();
        scrollToBottom();
    }

    function appendLoadingMessage() {
        const id = 'loading-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'result-entry-gpt mb-5 opacity-50';
        div.innerHTML = `
            <div class="gpt-avatar"><i data-lucide="loader"></i></div>
            <div class="gpt-response-content mt-1" style="line-height: 1.6;">A IA está pensando... isso pode levar alguns segundos.</div>
        `;
        chatMessages.appendChild(div);
        if (window.lucide) lucide.createIcons();
        scrollToBottom();
        return id;
    }

    function removeLoadingMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function showResultCard(data) {
        const clone = resultTemplate.content.cloneNode(true);

        const verdict = data.result;
        clone.querySelector('.verdict-title').innerText = verdict;

        const bar = clone.querySelector('.progress-bar');
        const conf = data.confidence;
        bar.style.width = conf + '%';
        bar.classList.add(conf > 70 ? 'bg-danger' : (conf > 40 ? 'bg-warning' : 'bg-success'));

        clone.querySelector('.confidence-text').innerText = `Risco: ${conf}%`;
        clone.querySelector('.summary-text').innerText = data.description;

        const grid = clone.querySelector('.details-grid');
        grid.innerHTML = data.agent_details.map(agent => {
            const insightText = agent.summary || (agent.findings ? agent.findings.join('<br>') : 'Nenhum detalhe adicional');
            return `
                <div class="col-md-6">
                    <div class="p-3 border rounded-3 bg-light-subtle h-100">
                        <div class="small fw-bold opacity-50 text-uppercase mb-1" style="font-size: 0.7rem;">${agent.agent}</div>
                        <div class="fw-bold mb-2">${agent.result}</div>
                        <div class="small text-muted" style="line-height: 1.4;">${insightText}</div>
                    </div>
                </div>
            `;
        }).join('');

        chatMessages.appendChild(clone);
        if (window.lucide) lucide.createIcons();
        scrollToBottom();
    }

    function scrollToBottom() {
        chatWrapper.scrollTo({ top: chatWrapper.scrollHeight, behavior: 'smooth' });
    }

    // --- History ---
    async function loadHistory() {
        try {
            const res = await fetch('/history');
            const data = await res.json();
            if (historyList) {
                historyList.innerHTML = data.map((item, idx) => `
                    <div class="history-item-gpt" onclick="window.viewHistoryItem(${idx})">
                        ${item.url || item.description.substring(0, 30)}
                    </div>
                `).join('');
                // Store for quick viewing
                window.cachedHistory = data;
            }
        } catch (e) { }
    }

    window.viewHistoryItem = function (idx) {
        const item = window.cachedHistory[idx];
        if (!item) return;
        welcomeSection.style.display = 'none';
        chatMessages.innerHTML = '';
        appendUserMessage(item.url);
        showResultCard({
            result: item.result,
            confidence: item.confidence,
            description: item.description,
            agent_details: []
        });
    };

    loadHistory();
});
