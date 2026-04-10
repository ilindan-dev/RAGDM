import re
from typing import List, Dict, Any

def parse_theorems_and_terms(text: str, chapter_name: str, model) -> List[Dict[str, Any]]:
    cards = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # --- ШАГ 1: Поиск теорем, лемм и доказательств (State Machine) ---
    state = "NORMAL"
    front_buf = []
    back_buf = []
    
    stop_markers = ("Теорема", "Лемма", "Следствие", "Пример", "Замечание", "Определение", "Алгоритм", "1.", "2.")

    for line in lines:
        is_theorem_start = any(line.startswith(m) for m in ("Теорема.", "Теорема ", "Лемма.", "Лемма ", "Следствие.", "Следствие "))
        
        if is_theorem_start:
            if state in ["THEOREM", "PROOF"] and front_buf and back_buf:
                cards.append({"front": " ".join(front_buf), "back": "\n".join(back_buf), "type": "Теорема/Доказательство"})
            
            state = "THEOREM"
            front_buf = [line]
            back_buf = []
            
        elif line.startswith("Доказательство.") or line.startswith("Обоснование."):
            if state == "THEOREM":
                state = "PROOF"
            back_buf.append(line)
            
        elif state == "THEOREM":
            front_buf.append(line)
            
        elif state == "PROOF":
            back_buf.append(line)
            # Конец доказательства
            if line.endswith("□") or line.endswith("■"):
                cards.append({"front": " ".join(front_buf), "back": "\n".join(back_buf), "type": "Теорема/Доказательство"})
                state = "NORMAL"
                front_buf, back_buf = []
        else:
            if state == "PROOF" and any(line.startswith(m) for m in stop_markers):
                cards.append({"front": " ".join(front_buf), "back": "\n".join(back_buf), "type": "Теорема/Доказательство"})
                state = "NORMAL"
                front_buf, back_buf = []

    if state in ["THEOREM", "PROOF"] and front_buf and back_buf:
         cards.append({"front": " ".join(front_buf), "back": "\n".join(back_buf), "type": "Теорема/Доказательство"})

    # --- ШАГ 2: Поиск Терминов (Regex) ---
    full_text = " ".join(lines)
    sentences = re.split(r'(?<=[.!?])\s+', full_text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 15 or sentence.startswith("Теорема") or sentence.startswith("Лемма"): 
            continue

        match_eto = re.search(r'^(.{2,60}?)\s*—\s*это\s+(.+)$', sentence)
        if match_eto:
            term = match_eto.group(1).strip()
            cards.append({"front": f"Термин: {term}", "back": sentence, "type": "Термин"})
            continue

        match_naz = re.search(r'(.+?)\s+называ(?:ет)?ся\s+([^.]+)', sentence)
        if match_naz:
            term = match_naz.group(2).strip()
            cards.append({"front": f"Термин: {term}", "back": sentence, "type": "Термин"})

    # --- ШАГ 3: Генерация Эмбеддингов ---
    print(f"Генерация векторов для {len(cards)} карточек...")
    for card in cards:
        text_to_embed = f"{card['front']} {card['back']}"
        card["embedding"] = model.encode(text_to_embed).tolist()
        card["source_info"] = f"{chapter_name} | {card['type']}"

    return cards
