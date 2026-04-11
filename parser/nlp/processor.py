import re
from typing import List, Dict, Any

def parse_theorems_and_terms(text: str, chapter_name: str, model) -> List[Dict[str, Any]]:
    cards = []
    # Убираем множественные пробелы
    text = re.sub(r'[ \t]+', ' ', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    state = "NORMAL"
    front_buf = []
    back_buf = []
    
    stop_markers = ("Теорема", "Лемма", "Следствие", "Пример", "Замечание", "Определение", "Алгоритм")

    for line in lines:
        is_theorem_start = any(line.startswith(m) for m in ("Теорема.", "Теорема ", "Лемма.", "Лемма ", "Следствие.", "Следствие "))
        
        if is_theorem_start:
            if state in ["THEOREM", "PROOF"] and front_buf and back_buf:
                cards.append({"front": " ".join(front_buf)[:250], "back": " ".join(back_buf), "type": "Теорема"})
            state = "THEOREM"
            front_buf, back_buf = [line], []
        elif line.startswith("Доказательство.") or line.startswith("Обоснование."):
            if state == "THEOREM": state = "PROOF"
            back_buf.append(line)
        elif state == "THEOREM":
            front_buf.append(line)
        elif state == "PROOF":
            back_buf.append(line)
            if any(end in line for end in ("□", "■")):
                cards.append({"front": " ".join(front_buf)[:250], "back": " ".join(back_buf), "type": "Теорема"})
                state = "NORMAL"
        else:
            if state == "PROOF" and any(line.startswith(m) for m in stop_markers):
                cards.append({"front": " ".join(front_buf)[:250], "back": " ".join(back_buf), "type": "Теорема"})
                state = "NORMAL"

    # --- Улучшенный поиск терминов ---
    full_text = " ".join(lines)
    # Разбиваем на предложения более аккуратно
    sentences = re.split(r'(?<=[.!?])\s+', full_text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        # Ищем: любой текст — [это] определение. Поддерживаем длинное и короткое тире.
        # Ограничиваем термин 100 символами, чтобы не захватить лишнего
        match = re.search(r'([^.!?—–-]{2,100})\s*[—–-]\s*(?:это\s+)?([^.!?]{10,})', sentence)
        
        if match:
            term = match.group(1).strip()
            # Очистка от мусора типа "Определение 1.2"
            term = re.sub(r'^(?:Определение|Понятие|Термин)\s*\d*\.?\s*', '', term, flags=re.IGNORECASE)
            
            if len(term) > 2:
                cards.append({
                    "front": f"Термин: {term}",
                    "back": sentence,
                    "type": "Термин"
                })

    print(f"Генерация векторов для {len(cards)} карточек...")
    for card in cards:
        # Важно: векторизуем только основной текст для более точного поиска
        text_to_embed = f"{card['front']} {card['back']}".lower()
        card["embedding"] = model.encode(text_to_embed).tolist()
        card["source_info"] = f"{chapter_name} | {card['type']}"

    return cards
