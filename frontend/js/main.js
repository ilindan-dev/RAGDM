document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSearch();
  initTrainer();
});

function initTabs() {
  const buttons = document.querySelectorAll(".tab-button");
  const tabs = document.querySelectorAll(".tab-content");

  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      buttons.forEach((b) => b.classList.remove("active"));
      tabs.forEach((t) => t.classList.remove("active"));

      btn.classList.add("active");
      const tabId = btn.dataset.tab + "-tab";
      document.getElementById(tabId).classList.add("active");
    });
  });
}

// Инициализация поиска
function initSearch() {
  const searchForm = document.getElementById('search-form');
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  const loadingIndicator = document.getElementById('loading-indicator');

  if (!searchForm) return;

  searchForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const query = searchInput.value.trim();
    if (!query) {
      alert('Пожалуйста, введите поисковый запрос');
      return;
    }

    if (loadingIndicator) {
      loadingIndicator.style.display = 'block';
    }
    
    if (searchResults) {
      searchResults.innerHTML = '';
    }

    try {
      const result = await searchRAG(query);
      renderSearchResults(result);
    } catch (error) {
      console.error('Search failed:', error);
      if (searchResults) {
        searchResults.innerHTML = '<div class="error-message">Ошибка поиска. Попробуйте позже.</div>';
      }
    } finally {
      if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
      }
    }
  });
}

function renderSearchResults(data) {
  const resultsContainer = document.getElementById('search-results');
  if (!resultsContainer) return;

  if (!data || !data.found_text) {
    resultsContainer.innerHTML = '<div class="no-results">Ничего не найдено</div>';
    return;
  }

  const resultCard = document.createElement('div');
  resultCard.className = 'result-card';
  
  const title = document.createElement('h3');
  title.textContent = 'Найденный текст:';
  
  const content = document.createElement('p');
  content.textContent = data.found_text;
  
  const meta = document.createElement('small');
  meta.textContent = `Источник: ${data.source || 'База знаний'}`;
  
  resultCard.appendChild(title);
  resultCard.appendChild(content);
  resultCard.appendChild(meta);
  
  resultsContainer.innerHTML = '';
  resultsContainer.appendChild(resultCard);
}

// Инициализация тренажёра
let currentQuestion = null;

function initTrainer() {
  const questionContainer = document.getElementById('question-container');
  const answerForm = document.getElementById('answer-form');
  const answerInput = document.getElementById('answer-input');
  const nextQuestionBtn = document.getElementById('next-question-btn');
  const feedbackDiv = document.getElementById('feedback');
  const questionText = document.getElementById('question-text');

  if (!answerForm) return;

  async function loadNextQuestion() {
    if (questionContainer) {
      questionContainer.style.opacity = '0.5';
    }
    
    if (feedbackDiv) {
      feedbackDiv.innerHTML = '';
    }
    
    if (answerInput) {
      answerInput.value = '';
      answerInput.disabled = true;
    }

    try {
      currentQuestion = await getNextQuestion();
      
      if (currentQuestion && questionText) {
        questionText.textContent = currentQuestion.question_text || currentQuestion.text;
        
        if (answerInput) {
          answerInput.disabled = false;
          answerInput.focus();
        }
      }
    } catch (error) {
      console.error('Failed to load question:', error);
      if (questionText) {
        questionText.textContent = error.message === 'Нет карточек для повторения' 
          ? 'Поздравляем! Все карточки повторены.' 
          : 'Ошибка загрузки вопроса. Попробуйте позже.';
      }
      if (answerInput) {
        answerInput.disabled = true;
      }
      currentQuestion = null;
    } finally {
      if (questionContainer) {
        questionContainer.style.opacity = '1';
      }
    }
  }

  async function handleSubmitAnswer(event) {
    event.preventDefault();
    
    if (!currentQuestion) {
      alert('Нет активного вопроса. Загрузите следующий вопрос.');
      return;
    }
    
    const answer = answerInput ? answerInput.value.trim() : '';
    if (!answer) {
      alert('Пожалуйста, введите ответ');
      return;
    }
    
    const submitBtn = answerForm.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
    }
    
    try {
      const result = await submitAnswer(currentQuestion.id, answer);
      
      if (feedbackDiv) {
        const isCorrect = result.is_correct || result.correct;
        feedbackDiv.innerHTML = `
          <div class="feedback ${isCorrect ? 'correct' : 'incorrect'}">
            <strong>${isCorrect ? 'Верно!' : 'Неверно!'}</strong>
            <p>${result.message || (isCorrect ? 'Отличная работа!' : `Правильный ответ: ${result.correct_answer || 'не указан'}`)}</p>
          </div>
        `;
      }
      
      setTimeout(() => {
        loadNextQuestion();
      }, 2000);
      
    } catch (error) {
      console.error('Failed to submit answer:', error);
      if (feedbackDiv) {
        feedbackDiv.innerHTML = '<div class="error">Ошибка отправки ответа. Попробуйте еще раз.</div>';
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
      }
    }
  }

  answerForm.addEventListener('submit', handleSubmitAnswer);
  
  if (nextQuestionBtn) {
    nextQuestionBtn.addEventListener('click', loadNextQuestion);
  }
  
  loadNextQuestion();
}