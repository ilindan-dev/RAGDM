import re
import fitz  # Это библиотека PyMuPDF
from tqdm import tqdm

def extract_text_from_pdf(pdf_path: str) -> str:
    """Извлекает текст через PyMuPDF, который лучше обрабатывает мат. символы (cid)."""
    full_text = []
    
    # Открываем документ
    doc = fitz.open(pdf_path)
    
    for page in tqdm(doc, desc=f"Чтение {pdf_path.name}"):
        # get_text("text") в PyMuPDF автоматически пытается разрешить (cid:) ссылки
        # параметр sort=True важен для сохранения порядка формул и текста
        text = page.get_text("text", sort=True)
        
        if not text:
            continue
            
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            # 1. Пропускаем номера страниц
            if re.match(r'^\s*\d+\s*/\s*\d+\s*$', line):
                continue
            
            # 2. Убираем остаточные (cid:...) если библиотека не смогла их разрешить
            # Мы заменяем их на пустую строку, чтобы не засорять поиск
            line = re.sub(r'\(cid:\d+\)', '', line)
            
            # 3. Исправляем слипание слов (русский язык)
            # Разрываем "слово.Слово" или "слово.Множество"
            line = re.sub(r'([а-яё])([А-ЯЁ])', r'\1 \2', line)
            
            # 4. Добавляем пробелы вокруг математических знаков, если они слиплись
            line = re.sub(r'([а-яёА-ЯЁ])([=+<>])', r'\1 \2', line)
            line = re.sub(r'([=+<>])([а-яёА-ЯЁ])', r'\1 \2', line)

            clean_lines.append(line)
            
        full_text.append('\n'.join(clean_lines))
    
    doc.close()
    return '\n'.join(full_text)
