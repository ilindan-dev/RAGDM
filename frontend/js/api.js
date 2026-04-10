// API Base URL (relative path for container compatibility)
const API_BASE = 'api/v1';

// Helper function for API calls with error handling
async function apiCall(url, options = {}) {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * Поиск RAG - отправляет запрос на поиск релевантного текста
 * @param {string} query - поисковый запрос пользователя
 * @returns {Promise<Object>} - ответ бэкенда с найденным текстом
 */
async function searchRAG(query) {
  try {
    const url = `${API_BASE}/cards/search?phrase=${encodeURIComponent(query)}&limit=5`;
    const similarCards = await apiCall(url);
    
    // Преобразуем массив SimilarCard в нужный фронтенду формат
    // Бэкенд возвращает массив объектов с полями: ID, FrontText, BackText, SourceInfo, Similarity
    if (Array.isArray(similarCards)) {
      return {
        terms: similarCards.map(card => ({
          front_text: card.FrontText || card.front_text,
          back_text: card.BackText || card.back_text,
          source_info: card.SourceInfo || card.source_info,
          similarity: card.Similarity || card.similarity || 0,
          id: card.ID || card.id
        }))
      };
    }
    
    return { terms: [] };
  } catch (error) {
    console.error('Search RAG error:', error);
    showError('Не удалось выполнить поиск. Проверьте соединение с сервером.');
    throw error;
  }
}

/**
 * Получить следующую карточку для повторения
 * @returns {Promise<Object>} - карточка с вопросом
 */
async function getNextQuestion() {
  try {
    // Используем правильный эндпоинт из бэкенда
    const url = `${API_BASE}/cards/review/next`;
    const reviewCard = await apiCall(url);
    
    // Бэкенд возвращает ReviewCard с полями: CardID, FrontText, BackText, SourceInfo, и т.д.
    if (reviewCard && (reviewCard.CardID || reviewCard.card_id)) {
      return {
        card_id: reviewCard.CardID || reviewCard.card_id,
        front_text: reviewCard.FrontText || reviewCard.front_text,
        back_text: reviewCard.BackText || reviewCard.back_text,
        source_info: reviewCard.SourceInfo || reviewCard.source_info,
        interval: reviewCard.Interval || reviewCard.interval,
        easiness: reviewCard.Easiness || reviewCard.easiness,
        repetitions: reviewCard.Repetitions || reviewCard.repetitions,
        next_review_at: reviewCard.NextReviewAt || reviewCard.next_review_at
      };
    }
    return null;
  } catch (error) {
    console.error('Get next question error:', error);
    if (error.message.includes('404') || error.message.includes('Нет карточек')) {
      throw new Error('Нет карточек для повторения');
    }
    showError(error.message || 'Не удалось загрузить следующий вопрос');
    throw error;
  }
}

/**
 * Отправить ответ студента на проверку
 * @param {string|number} questionId - ID вопроса (UUID)
 * @param {string} text - ответ пользователя
 * @returns {Promise<Object>} - результат проверки
 */
async function submitAnswer(questionId, text) {
  try {
    const url = `${API_BASE}/cards/${questionId}/answer`;
    const result = await apiCall(url, {
      method: 'POST',
      body: JSON.stringify({ answer: text }),
    });
    
    // Бэкенд возвращает ReviewResult с полями: Quality, NextInterval, NewEasiness, Repetitions
    // Конвертируем Quality (0-5) в similarity (0-1)
    let similarity = 0;
    const quality = result.Quality || result.quality || 0;
    
    if (quality >= 4) {
      similarity = 0.9;  // Отлично
    } else if (quality >= 3) {
      similarity = 0.7;  // Хорошо
    } else if (quality >= 2) {
      similarity = 0.5;  // Удовлетворительно
    } else if (quality >= 1) {
      similarity = 0.3;  // Плохо
    } else {
      similarity = 0.1;  // Очень плохо
    }
    
    return {
      similarity: similarity,
      quality: quality,
      next_interval: result.NextInterval || result.next_interval,
      new_easiness: result.NewEasiness || result.new_easiness,
      repetitions: result.Repetitions || result.repetitions
    };
  } catch (error) {
    console.error('Submit answer error:', error);
    showError('Не удалось отправить ответ. Проверьте соединение с сервером.');
    throw error;
  }
}

/**
 * Показать ошибку пользователю
 * @param {string} message - сообщение об ошибке
 */
function showError(message) {
  alert(message);
}

// Экспорт функций для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { searchRAG, getNextQuestion, submitAnswer };
}

// Export functions for use in main.js
window.RAGAPI = {
  searchRAG,
  getNextQuestion,
  submitAnswer,
};