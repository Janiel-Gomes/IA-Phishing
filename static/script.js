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

    // --- State & Persistence ---
    let selectedModel = localStorage.getItem('phishing_model') || 'ollama';
    let currentLang = localStorage.getItem('phishing_lang') || 'PT';
    let hasContext = false;
    const modelDropdownItems = document.querySelectorAll('.dropdown-item[data-model]');
    const activeModelName = document.getElementById('active-model-name');

    function applyModelSettings(model) {
        selectedModel = model;
        localStorage.setItem('phishing_model', model);

        const item = document.querySelector(`.dropdown-item[data-model="${model}"]`);
        if (item) {
            modelDropdownItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            const friendlyName = item.querySelector('.fw-bold').innerText;
            activeModelName.innerText = friendlyName.split(' ')[0];
        }
        if (window.lucide) lucide.createIcons();
    }

    modelDropdownItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            applyModelSettings(item.getAttribute('data-model'));
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

    // --- Dark Mode ---
    function applyTheme(isDark) {
        if (isDark) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('phishing_theme', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('phishing_theme', 'light');
        }
        if (darkBtn) {
            darkBtn.innerHTML = isDark ? '<i data-lucide="sun"></i>' : '<i data-lucide="moon"></i>';
        }
        if (window.lucide) lucide.createIcons();
    }

    if (darkBtn) {
        darkBtn.addEventListener('click', () => {
            const isDark = !document.body.classList.contains('dark-mode');
            applyTheme(isDark);
        });
    }

    // --- Language ---
    const welcomeTitleElement = document.querySelector('.welcome-section-gpt h1');

    function applyLanguage(lang) {
        currentLang = lang;
        localStorage.setItem('phishing_lang', lang);

        const langText = langBtn ? langBtn.querySelector('span') : null;
        if (langText) langText.innerText = lang;

        if (lang === 'EN') {
            mainInput.placeholder = "Paste a link or message here...";
            if (welcomeTitleElement) welcomeTitleElement.innerText = "How can I help?";
            newChatBtn.setAttribute('title', 'New Chat');

            document.querySelectorAll('.suggestion-card').forEach(card => {
                const span = card.querySelector('span');
                if (span.innerText === "Verificar um link suspeito") {
                    span.innerText = "Check a suspicious link";
                    card.dataset.query = "I want to check a suspicious link";
                    card.dataset.intent = "link";
                } else if (span.innerText === "Analisar texto de e-mail") {
                    span.innerText = "Analyze email text";
                    card.dataset.query = "I want to analyze an email text";
                    card.dataset.intent = "text";
                } else if (span.innerText === "Dicas de segurança") {
                    span.innerText = "Security tips";
                    card.dataset.query = "Give me some security tips against phishing";
                    card.dataset.intent = "tips";
                } else if (span.innerText === "Sobre certificados SSL") {
                    span.innerText = "About SSL certificates";
                    card.dataset.query = "Tell me about SSL certificates";
                    card.dataset.intent = "ssl";
                }
            });
        } else {
            mainInput.placeholder = "Cole um link ou mensagem aqui...";
            if (welcomeTitleElement) welcomeTitleElement.innerText = "Como posso ajudar?";
            newChatBtn.setAttribute('title', 'Novo Chat');

            document.querySelectorAll('.suggestion-card').forEach(card => {
                const span = card.querySelector('span');
                if (span.innerText === "Check a suspicious link") {
                    span.innerText = "Verificar um link suspeito";
                    card.dataset.query = "Quero verificar um link suspeito";
                    card.dataset.intent = "link";
                } else if (span.innerText === "Analyze email text") {
                    span.innerText = "Analisar texto de e-mail";
                    card.dataset.query = "Quero analisar um texto de e-mail";
                    card.dataset.intent = "text";
                } else if (span.innerText === "Security tips") {
                    span.innerText = "Dicas de segurança";
                    card.dataset.query = "Me dê algumas dicas de segurança contra phishing";
                    card.dataset.intent = "tips";
                } else if (span.innerText === "About SSL certificates") {
                    span.innerText = "Sobre certificados SSL";
                    card.dataset.query = "Me fale sobre certificados SSL";
                    card.dataset.intent = "ssl";
                }
            });
        }
    }

    if (langBtn) {
        langBtn.addEventListener('click', () => {
            const nextLang = currentLang === 'PT' ? 'EN' : 'PT';
            applyLanguage(nextLang);
        });
    }

    // --- INITIALIZATION ---
    const savedTheme = localStorage.getItem('phishing_theme');
    if (savedTheme === 'dark') applyTheme(true);

    applyModelSettings(selectedModel);
    applyLanguage(currentLang);

    // Handle Quick Suggestions
    document.querySelectorAll('.suggestion-card').forEach(card => {
        card.addEventListener('click', () => {
            const query = card.dataset.query;
            const intent = card.dataset.intent;
            mainInput.value = query;
            // Dispatch submit event with extra detail to force chat for these suggestions
            analysisForm.dispatchEvent(new CustomEvent('submit', {
                detail: { forceChat: true, intent: intent }
            }));
        });
    });

    // --- Auto-expanding Textarea & Enter to Submit ---
    mainInput.addEventListener('input', () => {
        mainInput.style.height = 'auto';
        mainInput.style.height = (mainInput.scrollHeight) + 'px';
    });

    mainInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            analysisForm.dispatchEvent(new Event('submit'));
        }
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
    const resetChat = () => {
        console.log("Resetando chat...");
        welcomeSection.style.display = 'block';
        chatMessages.innerHTML = '';
        mainInput.value = '';
        mainInput.style.height = 'auto';

        hasContext = false;
        imgInput.value = '';
        updateImageBadge(null);

        chatWrapper.scrollTo({ top: 0, behavior: 'instant' });
    };

    if (newChatBtn) newChatBtn.addEventListener('click', resetChat);

    // Also wire up the sidebar "Novo chat" item
    const sidebarNewChat = document.querySelector('.sidebar-nav .nav-item');
    if (sidebarNewChat) {
        sidebarNewChat.style.cursor = 'pointer';
        sidebarNewChat.addEventListener('click', resetChat);
    }

    // --- Form Submission ---
    analysisForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Capture ALL data immediately
        const userInput = mainInput.value.trim();
        const imageFile = imgInput.files.length > 0 ? imgInput.files[0] : null;
        const hasImage = !!imageFile;
        const isUrl = /^(http|https):\/\/[^ "]+$/.test(userInput);
        const isLongText = userInput.length > 500; // Text analysis is for long emails
        // Match keywords anywhere in the message for better flexibility
        const conversationalKeywords = /\b(o que|como|quem|onde|por que|what|how|why|who|where|is|can|posso|quero|me ajude|me diga|dicas|ajuda|olá|oi|exemplo|mostre|exemplos|show me|help|vulnerabilidade|segurança)\b/i;
        const looksLikeQuestion = conversationalKeywords.test(userInput) || userInput.includes('?') || userInput.length < 20;
        const forceChat = e.detail && e.detail.forceChat;

        if (!userInput && !hasImage) return;

        // 2. Prepare FormData immediately (capturing the file reference)
        const formData = new FormData();
        if (isUrl) formData.append('url', userInput);
        else formData.append('text', userInput);
        if (hasImage) formData.append('image', imageFile);
        formData.append('model', selectedModel);
        formData.append('lang', currentLang);

        // 3. Show User Message (UI transition)
        welcomeSection.style.display = 'none';
        if (hasImage) {
            const reader = new FileReader();
            reader.onload = (event) => {
                appendUserMessage(userInput || "[Análise de Imagem]", event.target.result);
            };
            reader.readAsDataURL(imageFile);
        } else {
            appendUserMessage(userInput);
        }

        // 4. Clear UI inputs
        mainInput.value = '';
        mainInput.style.height = 'auto';
        imgInput.value = '';
        updateImageBadge(null);

        // 5. Logic: Is this a scan or a question?
        // Route to chat if: has context, OR specifically requested, OR looks like a general question (and NOT a URL)
        if ((hasContext || looksLikeQuestion || forceChat) && !isUrl && !isLongText && !hasImage) {
            const loadingId = appendLoadingMessage();
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: userInput,
                        model: selectedModel,
                        lang: currentLang
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

        // 6. Send Analysis (Scan) using the prepared formData
        const loadingId = appendLoadingMessage();
        try {
            console.log("Enviando análise...", { hasImage, userInput, selectedModel });
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            removeLoadingMessage(loadingId);

            if (data.error) throw new Error(data.error);

            showResultCard(data);
            hasContext = true;
            loadHistory();
        } catch (err) {
            removeLoadingMessage(loadingId);
            appendAiMessage("Erro na análise: " + err.message);
            console.error("Erro fetch /predict:", err);
        }
    });

    function appendUserMessage(text, imgSrc = null) {
        const div = document.createElement('div');
        div.className = 'message-bubble-user-gpt mb-4 px-4 text-end';

        let content = `<span class="user-bubble-content p-3 rounded-4 d-inline-block shadow-sm" style="max-width: 80%; text-align: left;">`;
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

        // Handle Suggested Question
        if (data.suggested_question) {
            const suggestionContainer = chatMessages.lastElementChild.querySelector('.suggestion-container');
            const suggestionPill = suggestionContainer.querySelector('.suggestion-pill');
            const suggestionText = suggestionContainer.querySelector('.suggestion-text');

            suggestionText.innerText = data.suggested_question;
            suggestionContainer.classList.remove('d-none');
            setTimeout(() => suggestionPill.classList.add('suggestion-pill-active'), 500);

            suggestionPill.addEventListener('click', () => {
                const question = data.suggested_question;
                mainInput.value = question;
                // Dispatch enter key or call form submit
                analysisForm.dispatchEvent(new Event('submit'));
            });
        }

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

    // --- Check for URL parameter to trigger auto-analysis ---
    const urlParams = new URLSearchParams(window.location.search);
    const searchParam = urlParams.get('search');
    if (searchParam) {
        mainInput.value = searchParam;
        // Wait a bit for everything to load then trigger submit
        setTimeout(() => {
            analysisForm.dispatchEvent(new Event('submit'));
            // Remove the param from URL without reloading to keep it clean
            window.history.replaceState({}, document.title, "/");
        }, 500);
    }
});
