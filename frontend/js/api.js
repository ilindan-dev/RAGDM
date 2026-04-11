// API Base URL (relative path for container compatibility)
const API_BASE = '/api/v1';

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
    const response = await apiCall(url); // Тут получаем весь объект {message: "...", terms: [...]}
    
    // ПРОВЕРКА: смотрим именно в поле terms
    if (response && Array.isArray(response.terms)) {
      return {
        terms: response.terms.map(card => ({
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
    throw error;
  }
}
/**
 * Получить следующую карточку для повторения
 * @returns {Promise<Object>} - карточка с вопросом
 */
async function getNextQuestion() {
  try {
    const url = `${API_BASE}/cards/review?limit=1`;
    const response = await apiCall(url);
    
    console.log('Backend response:', response); // Для отладки в консоли браузера

    // Проверяем: если бэкенд вернул объект с полем cards
    if (response && Array.isArray(response.cards) && response.cards.length > 0) {
      const reviewCard = response.cards[0];
      return {
        card_id: reviewCard.CardID || reviewCard.card_id,
        front_text: reviewCard.FrontText || reviewCard.front_text,
        back_text: reviewCard.BackText || reviewCard.back_text,
        source_info: reviewCard.SourceInfo || reviewCard.source_info
      };
    } 
    // Если бэкенд вернул просто массив (на всякий случай)
    else if (Array.isArray(response) && response.length > 0) {
        const reviewCard = response[0];
        return {
          card_id: reviewCard.CardID || reviewCard.card_id,
          front_text: reviewCard.FrontText || reviewCard.front_text,
          back_text: reviewCard.BackText || reviewCard.back_text,
          source_info: reviewCard.SourceInfo || reviewCard.source_info
        };
    }
    
    return null;
  } catch (error) {
    console.error('Get next question error:', error);
    throw new Error('Нет карточек для повторения');
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
    
    console.log('Answer result:', result);

    // 1. Пытаемся взять similarity напрямую (0.88 -> 0.88)
    let similarity = result.similarity || result.Similarity;

    // 2. Если бэкенд прислал только Quality (0-5), конвертируем его
    if (similarity === undefined) {
      const quality = result.quality || result.Quality || 0;
      if (quality >= 4) similarity = 0.9;
      else if (quality >= 3) similarity = 0.7;
      else if (quality >= 2) similarity = 0.5;
      else if (quality >= 1) similarity = 0.3;
      else similarity = 0.1;
    }
    
    return {
      similarity: similarity,
      quality: result.quality || result.Quality || 0,
      next_interval: result.next_interval || result.NextInterval,
      new_easiness: result.new_easiness || result.NewEasiness,
      repetitions: result.repetitions || result.Repetitions
    };
  } catch (error) {
    console.error('Submit answer error:', error);
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