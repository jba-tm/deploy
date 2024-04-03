from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification

tokenizer = AutoTokenizer.from_pretrained("d4data/biomedical-ner-all")
model = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")

pipe = pipeline(
    "ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple"
)  # pass device=0 if using gpu
