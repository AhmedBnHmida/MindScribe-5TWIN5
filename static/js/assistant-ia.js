// communication/static/js/assistant-ia.js
class AssistantIAChat {
    constructor() {
        this.sessionId = document.getElementById('session-id').value;
        this.selectedJournalId = document.getElementById('selected-journal').value;
        this.selectedJournalData = null;
        this.isProcessing = false;
        this.modal = new bootstrap.Modal(document.getElementById('journalModal'));
        this.detailsModal = new bootstrap.Modal(document.getElementById('journalDetailsModal'));
        this.isDragging = false;
        this.draggedJournal = null;
        this.touchStartX = 0;
        this.touchStartY = 0;

        this.initializeEventListeners();
        this.initializeDragAndDrop();
        this.loadSessionHistory();
    }

    initializeEventListeners() {
        document.getElementById('message-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        document.getElementById('attach-journal-btn').addEventListener('click', () => {
            this.showJournalList();
        });

        document.getElementById('confirm-journal-selection').addEventListener('click', () => {
            this.confirmJournalSelection();
        });

        document.getElementById('clear-context')?.addEventListener('click', () => {
            this.clearJournalContext();
        });

        document.getElementById('analyze-journal-btn')?.addEventListener('click', () => {
            this.quickAnalyzeJournal();
        });

        document.querySelectorAll('.quick-prompt').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.getElementById('message-input').value = e.target.dataset.prompt;
                this.sendMessage();
            });
        });

        document.getElementById('message-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        document.getElementById('journals-list').addEventListener('click', (e) => {
            const journalItem = e.target.closest('.journal-item');
            if (journalItem && !e.target.closest('.drag-handle') && !this.isDragging) {
                this.handleJournalClick(journalItem);
            }
        });

        document.getElementById('journals-list').addEventListener('keydown', (e) => {
            const journalItems = document.querySelectorAll('.journal-item');
            if (journalItems.length === 0) return;

            const activeElement = document.activeElement;
            if (!activeElement.classList.contains('journal-item')) return;

            const index = Array.from(journalItems).indexOf(activeElement);

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                const nextIndex = (index + 1) % journalItems.length;
                journalItems[nextIndex].focus();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                const prevIndex = (index - 1 + journalItems.length) % journalItems.length;
                journalItems[prevIndex].focus();
            } else if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.handleJournalClick(activeElement);
            }
        });

        document.getElementById('message-input').focus();

    }

    initializeDragAndDrop() {
        const journalsList = document.getElementById('journals-list');
        const inputArea = document.getElementById('message-input-area');
        const dropZone = document.getElementById('drop-zone');
        const mobileDropZone = document.getElementById('mobile-drop-zone');

        journalsList.style.touchAction = 'none';

        journalsList.addEventListener('dragstart', (e) => {
            const journal = e.target.closest('.draggable-journal');
            if (journal) {
                this.handleDragStart(e, journal);
            }
        });

        journalsList.addEventListener('dragend', (e) => {
            const journal = e.target.closest('.draggable-journal');
            if (journal) {
                this.handleDragEnd(e);
            }
        });

        journalsList.addEventListener('touchstart', (e) => {
            const journal = e.target.closest('.draggable-journal');
            if (journal && !e.target.closest('.drag-handle')) {
                this.handleDragStart(e, journal);
                journal.classList.add('dragging');
                this.touchStartX = e.touches[0].clientX;
                this.touchStartY = e.touches[0].clientY;
            }
        }, { passive: false });

        journalsList.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const journal = this.draggedJournal;
            if (journal) {
                journal.style.position = 'absolute';
                journal.style.left = `${touch.clientX - 50}px`;
                journal.style.top = `${touch.clientY - 50}px`;
                if (this.isElementInInputArea(touch) || this.isElementInMobileDropZone(touch)) {
                    inputArea.classList.add('drop-zone-active');
                    mobileDropZone.classList.add('drop-zone-active');
                    this.showDropZone();
                } else {
                    inputArea.classList.remove('drop-zone-active');
                    mobileDropZone.classList.remove('drop-zone-active');
                }
            }
        }, { passive: false });

        journalsList.addEventListener('touchend', (e) => {
            const touch = e.changedTouches[0];
            const journal = this.draggedJournal;
            if (journal) {
                journal.style.position = '';
                journal.style.left = '';
                journal.style.top = '';
                journal.classList.remove('dragging');
                if (this.isElementInInputArea(touch) || this.isElementInMobileDropZone(touch)) {
                    this.selectJournalFromDrag(journal);
                }
                this.handleDragEnd(e);
            }
        });

        if (inputArea) {
            inputArea.addEventListener('dragover', (e) => this.handleDragOver(e));
            inputArea.addEventListener('dragenter', (e) => this.handleDragEnter(e));
            inputArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            inputArea.addEventListener('drop', (e) => this.handleDrop(e));
        }

        if (mobileDropZone) {
            mobileDropZone.addEventListener('touchend', (e) => {
                if (this.draggedJournal) {
                    this.selectJournalFromDrag(this.draggedJournal);
                    this.handleDragEnd(e);
                }
            });
        }
    }

    async refreshJournals() {
        try {
            document.getElementById('journals-list-loading').style.display = 'block';
            document.getElementById('journals-list').style.display = 'none';
            const response = await fetch('/communication/assistant-ia/refresh-journals/', {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                }
            });
            const data = await response.json();
            if (data.success) {
                this.updateJournalsList(data.journals);
            } else {
                console.error('Erreur chargement journaux:', data.error);
                this.addSystemMessage('❌ Erreur lors du chargement des journaux');
            }
        } catch (error) {
            console.error('Erreur refresh journaux:', error);
            this.addSystemMessage('❌ Erreur réseau lors du chargement des journaux');
        } finally {
            document.getElementById('journals-list-loading').style.display = 'none';
            document.getElementById('journals-list').style.display = 'block';
        }
    }

    updateJournalsList(journals) {
        const journalsList = document.getElementById('journals-list');
        journalsList.innerHTML = '';

        if (journals.length === 0) {
            journalsList.innerHTML = `
                <div class="list-group-item text-center py-5 border-0">
                    <div class="text-muted">
                        <i class="fas fa-book-open fa-3x mb-3 text-primary opacity-50"></i>
                        <h6 class="fw-semibold mb-2">Aucun journal récent</h6>
                        <p class="small mb-3">Commencez votre voyage d'écriture</p>
                        <a href="/journal/creer/" class="btn btn-primary btn-sm rounded-pill px-4">
                            <i class="fas fa-plus me-1"></i>Créer un journal
                        </a>
                    </div>
                </div>
            `;
            return;
        }

        journals.forEach(journal => {
            const journalElement = document.createElement('div');
            journalElement.className = 'list-group-item journal-item draggable-journal border-0';
            journalElement.tabIndex = 0;
            journalElement.draggable = true;
            journalElement.dataset.journalId = journal.id;
            journalElement.dataset.journalTitre = journal.titre;
            journalElement.dataset.journalDate = journal.date_creation;
            journalElement.dataset.journalContenu = journal.contenu;
            journalElement.dataset.journalType = journal.type_entree;
            journalElement.dataset.journalCategorie = journal.categorie;

            journalElement.innerHTML = `
                <div class="journal-content">
                    <div class="d-flex w-100 justify-content-between align-items-start mb-2">
                        <h6 class="mb-1 fw-semibold text-dark">${journal.titre}</h6>
                        <small class="text-muted fw-medium">${journal.date_creation.split('/').slice(0, 2).join('/')}</small>
                    </div>
                    <p class="mb-2 text-muted small lh-sm">${this.truncateText(journal.contenu, 60)}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge bg-primary bg-opacity-10 text-primary border-0 px-2 py-1">
                            <i class="fas fa-${journal.type_entree === 'texte' ? 'file-text' : journal.type_entree === 'audio' ? 'microphone' : 'image'} me-1"></i>${journal.type_entree}
                        </span>
                        ${journal.categorie !== 'Non catégorisé' ? `<span class="badge bg-success bg-opacity-10 text-success border-0 px-2 py-1">${journal.categorie}</span>` : ''}
                    </div>
                </div>
                <div class="drag-handle">
                    <i class="fas fa-grip-vertical text-muted"></i>
                </div>
            `;

            journalsList.appendChild(journalElement);
        });

        this.updateJournalListState();
    }

    handleJournalClick(journalElement) {
        if (this.isDragging) return;
        journalElement.classList.add('selecting');
        setTimeout(() => {
            journalElement.classList.remove('selecting');
        }, 400);

        this.selectedJournalData = {
            id: journalElement.dataset.journalId,
            titre: journalElement.dataset.journalTitre,
            date: journalElement.dataset.journalDate,
            contenu: journalElement.dataset.journalContenu,
            type: journalElement.dataset.journalType,
            categorie: journalElement.dataset.journalCategorie
        };

        this.selectedJournalId = this.selectedJournalData.id;
        document.getElementById('selected-journal').value = this.selectedJournalId;
        this.showJournalInInputArea();
        this.updateJournalListState();
    }

    showJournalInInputArea() {
        const inputArea = document.getElementById('message-input-area');
        const existingAttachment = document.getElementById('journal-attachment');
        if (existingAttachment) {
            existingAttachment.remove();
        }

        const journalAttachment = document.createElement('div');
        journalAttachment.id = 'journal-attachment';
        journalAttachment.className = 'journal-attachment';
        journalAttachment.innerHTML = `
            <div class="journal-attachment-header">
                <h6 class="journal-attachment-title">📄 ${this.selectedJournalData.titre}</h6>
                <div class="journal-attachment-meta">
                    <span class="badge journal-attachment-badge">${this.selectedJournalData.type}</span>
                    <small class="text-muted">${this.selectedJournalData.date}</small>
                </div>
            </div>
            <div class="journal-attachment-content">
                <p>${this.truncateText(this.selectedJournalData.contenu, 120)}</p>
            </div>
            <div class="journal-attachment-actions">
                <button class="btn btn-outline-primary btn-sm journal-attachment-btn" onclick="window.assistantChat.showJournalDetails()">
                    <i class="fas fa-eye me-1"></i>Détails
                </button>
                <button class="btn btn-outline-success btn-sm journal-attachment-btn" onclick="window.assistantChat.analyzeSelectedJournal()">
                    <i class="fas fa-magic me-1"></i>Analyser
                </button>
                <button class="btn btn-outline-danger btn-sm journal-attachment-btn" onclick="window.assistantChat.removeSelectedJournal()">
                    <i class="fas fa-times me-1"></i>Retirer
                </button>
            </div>
        `;

        const messageForm = document.getElementById('message-form');
        inputArea.insertBefore(journalAttachment, messageForm);

        document.getElementById('message-input').placeholder = `Posez une question sur "${this.selectedJournalData.titre}"...`;
        inputArea.classList.add('journal-attached');
    }

    showJournalDetails() {
        if (!this.selectedJournalData) return;

        document.getElementById('journal-details-title').textContent = this.selectedJournalData.titre;
        document.getElementById('journal-details-date').textContent = this.selectedJournalData.date;
        document.getElementById('journal-details-type').textContent = this.selectedJournalData.type;
        document.getElementById('journal-details-category').textContent = this.selectedJournalData.categorie;
        document.getElementById('journal-details-content').textContent = this.selectedJournalData.contenu;

        this.detailsModal.show();
    }

    analyzeSelectedJournal() {
        if (!this.selectedJournalId) return;

        const messageInput = document.getElementById('message-input');
        messageInput.value = "Peux-tu analyser ce journal et me donner tes observations détaillées ?";
        this.sendMessage();
    }

    removeSelectedJournal() {
        const journalAttachment = document.getElementById('journal-attachment');
        if (journalAttachment) {
            journalAttachment.remove();
        }

        this.selectedJournalId = '';
        this.selectedJournalData = null;
        document.getElementById('selected-journal').value = '';

        this.updateJournalListState();

        const inputArea = document.getElementById('message-input-area');
        inputArea.classList.remove('journal-attached');

        document.getElementById('message-input').placeholder = "Posez votre question ou demandez une analyse...";

        this.addSystemMessage('❌ Journal retiré de la conversation');
    }

    updateJournalListState() {
        document.querySelectorAll('.journal-item').forEach(item => {
            item.classList.remove('active', 'selected');
        });

        if (this.selectedJournalId) {
            const selectedJournal = document.querySelector(`[data-journal-id="${this.selectedJournalId}"]`);
            if (selectedJournal) {
                selectedJournal.classList.add('selected');
            }
        }
    }

    handleDragStart(e, journal) {
        console.log('Drag start:', journal.dataset.journalId);
        this.isDragging = true;
        this.draggedJournal = journal;

        if (e.dataTransfer) {
            e.dataTransfer.setData('text/plain', journal.dataset.journalId);
            e.dataTransfer.setData('application/json', JSON.stringify({
                id: journal.dataset.journalId,
                titre: journal.dataset.journalTitre,
                date: journal.dataset.journalDate,
                contenu: journal.dataset.journalContenu,
                type: journal.dataset.journalType,
                categorie: journal.dataset.journalCategorie
            }));
            e.dataTransfer.effectAllowed = 'move';
        }

        journal.classList.add('dragging');
        this.showDropZone();
    }

    handleDragEnd(e) {
        console.log('Drag end');
        this.isDragging = false;
        if (this.draggedJournal) {
            this.draggedJournal.classList.remove('dragging');
            this.draggedJournal.style.position = '';
            this.draggedJournal.style.left = '';
            this.draggedJournal.style.top = '';
            this.draggedJournal = null;
        }
        document.getElementById('message-input-area').classList.remove('drop-zone-active');
        document.getElementById('mobile-drop-zone').classList.remove('drop-zone-active');
        this.hideDropZone();
    }

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }

    handleDragEnter(e) {
        e.preventDefault();
        const inputArea = document.getElementById('message-input-area');
        if (inputArea && this.isElementInInputArea(e)) {
            inputArea.classList.add('drop-zone-active');
            this.showDropZone();
        }
    }

    handleDragLeave(e) {
        const inputArea = document.getElementById('message-input-area');
        if (inputArea && !this.isElementInInputArea(e)) {
            inputArea.classList.remove('drop-zone-active');
        }
    }

    handleDrop(e) {
        console.log('Drop:', e.dataTransfer.getData('text/plain'));
        e.preventDefault();
        const inputArea = document.getElementById('message-input-area');
        if (inputArea) {
            inputArea.classList.remove('drop-zone-active');
        }
        const journalId = e.dataTransfer.getData('text/plain');
        const journal = document.querySelector(`.draggable-journal[data-journal-id="${journalId}"]`);
        if (journal) {
            this.selectJournalFromDrag(journal);
        } else {
            console.error('Journal not found for ID:', journalId);
        }
        this.hideDropZone();
    }

    selectJournalFromDrag(journalElement) {
        this.selectedJournalData = {
            id: journalElement.dataset.journalId,
            titre: journalElement.dataset.journalTitre,
            date: journalElement.dataset.journalDate,
            contenu: journalElement.dataset.journalContenu,
            type: journalElement.dataset.journalType,
            categorie: journalElement.dataset.journalCategorie
        };

        this.selectedJournalId = this.selectedJournalData.id;
        document.getElementById('selected-journal').value = this.selectedJournalId;

        this.showJournalInInputArea();
        this.updateJournalListState();
        this.addSystemMessage(`🎯 Journal "${this.selectedJournalData.titre}" ajouté par glisser-déposer`);
    }

    isElementInInputArea(e) {
        const inputArea = document.getElementById('message-input-area');
        if (!inputArea) return false;

        const rect = inputArea.getBoundingClientRect();
        const clientX = e.clientX || (e.touches && e.touches[0]?.clientX) || (e.changedTouches && e.changedTouches[0]?.clientX);
        const clientY = e.clientY || (e.touches && e.touches[0]?.clientY) || (e.changedTouches && e.changedTouches[0]?.clientY);

        const padding = 10;
        return (
            clientX >= rect.left - padding &&
            clientX <= rect.right + padding &&
            clientY >= rect.top - padding &&
            clientY <= rect.bottom + padding
        );
    }

    isElementInMobileDropZone(e) {
        const mobileDropZone = document.getElementById('mobile-drop-zone');
        if (!mobileDropZone) return false;

        const rect = mobileDropZone.getBoundingClientRect();
        const clientX = e.clientX || (e.touches && e.touches[0]?.clientX) || (e.changedTouches && e.changedTouches[0]?.clientX);
        const clientY = e.clientY || (e.touches && e.touches[0]?.clientY) || (e.changedTouches && e.changedTouches[0]?.clientY);

        const padding = 10;
        return (
            clientX >= rect.left - padding &&
            clientX <= rect.right + padding &&
            clientY >= rect.top - padding &&
            clientY <= rect.bottom + padding
        );
    }

    showDropZone() {
        const dropZone = document.getElementById('drop-zone');
        if (dropZone) {
            dropZone.style.display = 'block';
        }
    }

    hideDropZone() {
        const dropZone = document.getElementById('drop-zone');
        if (dropZone) {
            dropZone.style.display = 'none';
            dropZone.classList.remove('drop-zone-active');
        }
    }

    showJournalModal(journalElement) {
        this.selectedJournalData = {
            id: journalElement.dataset.journalId,
            titre: journalElement.dataset.journalTitre,
            date: journalElement.dataset.journalDate,
            contenu: journalElement.dataset.journalContenu,
            type: journalElement.dataset.journalType,
            categorie: journalElement.dataset.journalCategorie
        };

        document.getElementById('modal-journal-title').textContent = this.selectedJournalData.titre;
        document.getElementById('modal-journal-date').textContent = this.selectedJournalData.date;
        document.getElementById('modal-journal-type').textContent = this.selectedJournalData.type;
        document.getElementById('modal-journal-category').textContent = this.selectedJournalData.categorie;
        document.getElementById('modal-journal-content').textContent = 
            this.selectedJournalData.contenu.length > 500 
            ? this.selectedJournalData.contenu.substring(0, 500) + '...' 
            : this.selectedJournalData.contenu;

        this.modal.show();
    }

    confirmJournalSelection() {
        if (!this.selectedJournalData) return;

        this.selectedJournalId = this.selectedJournalData.id;
        document.getElementById('selected-journal').value = this.selectedJournalId;

        this.showJournalInInputArea();
        this.updateJournalListState();
        this.modal.hide();
    }

    clearJournalContext() {
        this.removeSelectedJournal();
    }

    showJournalList() {
        const firstJournal = document.querySelector('.journal-item');
        if (firstJournal) {
            this.showJournalModal(firstJournal);
        } else {
            this.addSystemMessage('Aucun journal disponible. Créez d\'abord un journal.');
        }
    }

    quickAnalyzeJournal() {
        if (!this.selectedJournalId) {
            this.addSystemMessage('❌ Veuillez d\'abord sélectionner un journal à analyser.');
            return;
        }

        const messageInput = document.getElementById('message-input');
        messageInput.value = "Peux-tu analyser ce journal et me donner tes observations détaillées ?";
        this.sendMessage();
    }

    async loadSessionHistory() {
        try {
            const response = await fetch(`/communication/assistant-ia/session/${this.sessionId}/`);
            if (response.ok) {
                const data = await response.json();
                this.displaySessionHistory(data.conversations);
            } else {
                console.error('Failed to load session history:', response.status);
            }
        } catch (error) {
            console.error('Erreur chargement historique:', error);
        }
    }

    displaySessionHistory(conversations) {
        const chatMessages = document.getElementById('chat-messages');

        if (conversations.length > 0) {
            const welcomeMessage = chatMessages.querySelector('.text-center');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }

            conversations.forEach(conv => {
                this.addMessageToChat(conv.message_utilisateur, 'user', conv.date_interaction);
                this.addMessageToChat(conv.reponse_ia, 'assistant', conv.date_interaction, conv.type_interaction);
            });
        }
    }

    async sendMessage() {
        if (this.isProcessing) return;

        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();

        if (!message) return;

        this.isProcessing = true;
        this.setUIState('loading');

        try {
            this.addMessageToChat(message, 'user');
            messageInput.value = '';

            const response = await fetch('/communication/assistant-ia/envoyer_message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    message: message,
                    journal_id: this.selectedJournalId,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                this.addMessageToChat(
                    data.reponse,
                    'assistant',
                    data.date_interaction,
                    data.type_interaction,
                    data.statistiques
                );
            } else {
                this.showError(data.error || 'Erreur inconnue du serveur');
            }
        } catch (error) {
            console.error('Erreur envoi message:', error);
            this.showError(`Erreur de connexion: ${error.message}`);
        } finally {
            this.isProcessing = false;
            this.setUIState('ready');
            messageInput.focus();
        }
    }

    addMessageToChat(text, sender, time = null, type = null, stats = null) {
        const chatMessages = document.getElementById('chat-messages');

        if (sender === 'user') {
            const welcomeMessage = chatMessages.querySelector('.text-center');
            if (welcomeMessage) {
                welcomeMessage.remove();
            }
        }

        const timeDisplay = time || new Date().toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const messageDiv = document.createElement('div');
        messageDiv.className = `message-container ${sender}-message`;

        let statsHTML = '';
        if (stats && sender === 'assistant') {
            statsHTML = `
                <div class="message-stats">
                    <small class="text-muted">
                        <i class="fas fa-clock me-1"></i>${stats.duree_generation}
                        <i class="fas fa-code me-1 ms-2"></i>${stats.tokens_utilises} tokens
                        <i class="fas fa-chart-line me-1 ms-2"></i>${(stats.score_confiance * 100).toFixed(0)}% confiance
                    </small>
                </div>
            `;
        }

        let typeBadge = '';
        if (type && sender === 'assistant') {
            const typeLabels = {
                'analyse_journal': '📊 Analyse Journal',
                'suggestion_ecriture': '✍️ Suggestion Écriture',
                'support_emotionnel': '💖 Support Émotionnel',
                'reflexion_guidee': '🧠 Réflexion Guidée',
                'question': '💬 Question',
                'autre': '🔗 Autre'
            };
            typeBadge = `<span class="badge message-type-badge">${typeLabels[type] || type}</span>`;
        }

        messageDiv.innerHTML = `
            <div class="message ${sender}-message">
                <div class="message-header">
                    <div class="message-sender">
                        <i class="fas fa-${sender === 'user' ? 'user' : 'robot'} me-2"></i>
                        <strong>${sender === 'user' ? 'Vous' : 'MindScribe'}</strong>
                    </div>
                    <div class="message-meta">
                        ${typeBadge}
                        <small class="message-time">${timeDisplay}</small>
                    </div>
                </div>
                <div class="message-content">${this.formatMessage(text)}</div>
                ${statsHTML}
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    addSystemMessage(text) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'text-center my-3';
        messageDiv.innerHTML = `
            <div class="alert alert-info d-inline-block">
                <i class="fas fa-info-circle me-2"></i>${text}
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    formatMessage(text) {
        text = text.replace(/\n/g, '<br>');
        text = text.replace(/\•\s*(.+?)(?=\n|$)/g, '<li>$1</li>');
        text = text.replace(/(<li>.*<\/li>)/s, '<ul class="message-list">$1</ul>');
        return text;
    }

    truncateText(text, length) {
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
    }

    setUIState(state) {
        const sendBtn = document.getElementById('send-btn');
        const messageInput = document.getElementById('message-input');

        if (state === 'loading') {
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            messageInput.disabled = true;
            messageInput.placeholder = "L'assistant réfléchit...";
        } else {
            sendBtn.disabled = false;
            sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
            messageInput.disabled = false;
        }
    }

    showError(message) {
        this.addMessageToChat(
            `❌ Désolé, une erreur s'est produite: ${message}`,
            'assistant'
        );
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    window.assistantChat = new AssistantIAChat();
});