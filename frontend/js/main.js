// DOM Elements
let currentCard = null;
let currentQuestionIndex = 0;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initSearch();
  initTrainer();
});

// Tab switching
function initTabs() {
  const tabs = document.querySelectorAll('.tab-button');
  const contents = document.querySelectorAll('.tab-content');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetTab = tab.dataset.tab;
      
      tabs.forEach(t => t.classList.remove('active'));
      contents.forEach(c => c.classList.remove('active'));
      
      tab.classList.add('active');
      document.getElementById(`${targetTab}-tab`).classList.add('active');
      
      // Load initial data when switching to trainer tab
      if (targetTab === 'trainer') {
        loadNextQuestion();
      }
    });
  });
}

// Search functionality
function initSearch() {
  const searchForm = document.getElementById('search-form');
  const searchInput = document.getElementById('search-input');
  
  searchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = searchInput.value.trim();
    
    if (!query) {
      showError('Пожалуйста, введите поисковый запрос');
      return;
    }
    
    await performSearch(query);
    searchInput.value = '';
  });
  
  // Allow Ctrl+Enter to submit
  searchInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      searchForm.dispatchEvent(new Event('submit'));
    }
  });
}

async function performSearch(query) {
  showLoading();
  addMessageToChat('user', query);
  
  try {
    const result = await window.RAGAPI.searchRAG(query);
    hideLoading();
    
    if (result.terms && result.terms.length > 0) {
      displaySearchResults(result.terms);
    } else {
      addMessageToChat('bot', 'К сожалению, ничего не найдено по вашему запросу. Попробуйте переформулировать вопрос.');
    }
  } catch (error) {
    hideLoading();
    showError(error.message);
    addMessageToChat('bot', `Ошибка поиска: ${error.message}`);
  }
}

function displaySearchResults(terms) {
  terms.forEach(term => {
    const message = `
      <p><strong>Найдено:</strong> ${escapeHtml(term.front_text)}</p>
      ${term.back_text ? `<p><strong>Подробнее:</strong> ${escapeHtml(term.back_text)}</p>` : ''}
      ${term.source_info ? `<p><strong>Источник:</strong> ${escapeHtml(term.source_info)}</p>` : ''}
      <div class="message-meta">
        <strong>Совпадение:</strong> ${(term.similarity * 100).toFixed(1)}%
      </div>
    `;
    addMessageToChat('bot', message, true);
  });
}

function addMessageToChat(role, content, isHtml = false) {
  const chatMessages = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${role}`;
  
  messageDiv.innerHTML = `
    <div class="message-content">
      ${isHtml ? content : `<p>${escapeHtml(content)}</p>`}
    </div>
  `;
  
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Trainer functionality
async function initTrainer() {
  const answerForm = document.getElementById('answer-form');
  const nextButton = document.getElementById('next-question-btn');
  
  answerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await handleAnswerSubmit();
  });
  
  nextButton.addEventListener('click', async () => {
    await loadNextQuestion();
  });
  
  // Load first question
  await loadNextQuestion();
}

async function loadNextQuestion() {
  showLoading();
  resetTrainerUI();
  
  try {
    const card = await window.RAGAPI.getNextQuestion();
    hideLoading();
    
    if (card) {
      currentCard = card;
      currentQuestionIndex++;
      displayQuestion(card);
    } else {
      displayNoQuestionsMessage();
    }
  } catch (error) {
    hideLoading();
    showError(error.message);
    displayNoQuestionsMessage();
  }
}

function displayQuestion(card) {
  const questionText = document.getElementById('question-text');
  const cardNumberSpan = document.getElementById('card-number');
  
  questionText.textContent = card.front_text || 'Вопрос не найден';
  cardNumberSpan.textContent = `Карточка #${currentQuestionIndex}`;
  
  // Enable answer form
  const answerInput = document.getElementById('answer-input');
  const submitBtn = document.getElementById('submit-answer-btn');
  answerInput.disabled = false;
  answerInput.value = '';
  submitBtn.disabled = false;
}

function displayNoQuestionsMessage() {
  const questionText = document.getElementById('question-text');
  const answerInput = document.getElementById('answer-input');
  const submitBtn = document.getElementById('submit-answer-btn');
  
  questionText.textContent = 'Отлично! На сегодня нет карточек для повторения. Зайдите позже!';
  answerInput.disabled = true;
  submitBtn.disabled = true;
}

async function handleAnswerSubmit() {
  if (!currentCard) {
    showError('Нет активного вопроса');
    return;
  }
  
  const answerInput = document.getElementById('answer-input');
  const answer = answerInput.value.trim();
  
  if (!answer) {
    showError('Пожалуйста, введите ваш ответ');
    return;
  }
  
  showLoading();
  
  try {
    const result = await window.RAGAPI.submitAnswer(currentCard.card_id, answer);
    hideLoading();
    displayResult(result.similarity);
  } catch (error) {
    hideLoading();
    showError(error.message);
  }
}

function displayResult(similarity) {
  const resultBlock = document.getElementById('result-block');
  const similarityValue = document.getElementById('similarity-value');
  const similarityFill = document.getElementById('similarity-fill');
  // Убрана переменная resultIcon
  const resultTitle = document.getElementById('result-title');
  const explanationText = document.getElementById('explanation-text');
  
  const percentage = (similarity * 100).toFixed(1);
  const isCorrect = similarity > 0.7;
  
  similarityValue.textContent = `${percentage}%`;
  similarityFill.style.width = `${percentage}%`;
  
  if (isCorrect) {
    resultTitle.textContent = 'Правильно!';
    similarityFill.style.background = 'var(--success)';
  } else if (similarity > 0.4) {
    resultTitle.textContent = 'Частично правильно';
    similarityFill.style.background = 'var(--warning)';
  } else {
    resultTitle.textContent = 'Неправильно';
    similarityFill.style.background = 'var(--error)';
  }
  
  // Display reference text from the card
  explanationText.innerHTML = `
    <strong>Эталонный ответ:</strong><br>
    ${escapeHtml(currentCard.back_text || 'Нет эталонного текста')}
    ${currentCard.source_info ? `<br><br><strong>Источник:</strong> ${escapeHtml(currentCard.source_info)}` : ''}
  `;
  
  resultBlock.classList.remove('hidden');
  
  // Disable answer form after submission
  const submitBtn = document.getElementById('submit-answer-btn');
  submitBtn.disabled = true;
}

function resetTrainerUI() {
  const resultBlock = document.getElementById('result-block');
  const answerInput = document.getElementById('answer-input');
  const submitBtn = document.getElementById('submit-answer-btn');
  
  resultBlock.classList.add('hidden');
  answerInput.disabled = false;
  answerInput.value = '';
  submitBtn.disabled = false;
}

// Utility functions
function showLoading() {
  const overlay = document.getElementById('loading-overlay');
  overlay.classList.remove('hidden');
}

function hideLoading() {
  const overlay = document.getElementById('loading-overlay');
  overlay.classList.add('hidden');
}

function showError(message) {
  // Create temporary error toast
  const toast = document.createElement('div');
  toast.className = 'error-toast';
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: var(--error);
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    z-index: 2000;
    animation: slideIn 0.3s ease;
  `;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}