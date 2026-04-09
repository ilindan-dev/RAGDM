const API_BASE = '/api'; 

/**
 * Поиск RAG - отправляет запрос на поиск релевантного текста
 * @param {string} query - поисковый запрос пользователя
 * @returns {Promise<Object>} - ответ бэкенда с найденным текстом
 */
async function searchRAG(query) {
    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return data;
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
        const response = await fetch(`${API_BASE}/review/next`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Нет карточек для повторения');
            }
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Get next question error:', error);
        showError(error.message || 'Не удалось загрузить следующий вопрос');
        throw error;
    }
}

/**
 * Отправить ответ студента на проверку
 * @param {string|number} questionId - ID вопроса
 * @param {string} text - ответ пользователя
 * @returns {Promise<Object>} - результат проверки
 */
async function submitAnswer(questionId, text) {
    try {
        const response = await fetch(`${API_BASE}/review/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                question_id: questionId, 
                answer: text 
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return data;
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
    alert(message); // Простой alert, можно заменить на модальное окно
}

// Экспорт функций для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { searchRAG, getNextQuestion, submitAnswer };
}