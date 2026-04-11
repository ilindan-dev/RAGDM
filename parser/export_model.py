from sentence_transformers import SentenceTransformer
import torch
import os

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
target_dir = "../models"
os.makedirs(target_dir, exist_ok=True)

# 1. Сохраняем токенизатор
model.tokenizer.save_pretrained(target_dir)
if os.path.exists(os.path.join(target_dir, "tokenizer.json")):
    print("✅ tokenizer.json готов")

# 2. Экспортируем в ONNX
dummy_input = model.tokenizer("привет", return_tensors="pt")
torch.onnx.export(
    model[0].auto_model, 
    (dummy_input['input_ids'], dummy_input['attention_mask']),
    os.path.join(target_dir, "model.onnx"),
    input_names=['input_ids', 'attention_mask'],
    output_names=['last_hidden_state'],
    dynamic_axes={'input_ids': {0: 'batch_size', 1: 'sequence_length'}, 
                 'attention_mask': {0: 'batch_size', 1: 'sequence_length'}},
    opset_version=14
)
print("✅ model.onnx готов")
