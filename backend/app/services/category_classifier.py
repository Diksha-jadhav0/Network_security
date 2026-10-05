import os
import json
import torch

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "category_model")

class CategoryClassifierService:
    _model = None
    _tokenizer = None
    _id2label = None
    _is_loaded = False
    _load_failed = False

    @classmethod
    def load_model(cls) -> bool:
        if cls._is_loaded:
            return True
        if cls._load_failed:
            return False

        if not os.path.exists(MODEL_DIR) or not os.path.exists(os.path.join(MODEL_DIR, "config.json")):
            print(f"Category model not found at {MODEL_DIR}. Category classifier will return UNKNOWN.")
            cls._load_failed = True
            return False

        try:
            from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
            print(f"Loading DistilBERT Category Classifier from {MODEL_DIR}...")
            cls._tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
            cls._model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
            cls._model.eval()

            label_map_path = os.path.join(MODEL_DIR, "label_mapping.json")
            if os.path.exists(label_map_path):
                with open(label_map_path, "r") as f:
                    data = json.load(f)
                    cls._id2label = {int(k): v for k, v in data["id2label"].items()}
            elif hasattr(cls._model.config, "id2label"):
                cls._id2label = {int(k): v for k, v in cls._model.config.id2label.items()}
            else:
                cls._id2label = {}

            cls._is_loaded = True
            print("DistilBERT Category Classifier loaded successfully!")
            return True
        except Exception as e:
            print(f"Failed to load DistilBERT category classifier: {e}")
            cls._load_failed = True
            return False

    @classmethod
    def classify_category(cls, email_text: str) -> dict:
        if not cls.load_model():
            return {
                "category": "UNKNOWN",
                "confidence": 0.0
            }

        try:
            inputs = cls._tokenizer(
                email_text,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            )
            with torch.no_grad():
                outputs = cls._model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)[0]
                pred_idx = torch.argmax(probs).item()
                confidence = float(probs[pred_idx].item())

            category = cls._id2label.get(pred_idx, "UNKNOWN")
            return {
                "category": category,
                "confidence": round(confidence, 4)
            }
        except Exception as e:
            print(f"Inference error in category classifier: {e}")
            return {
                "category": "UNKNOWN",
                "confidence": 0.0
            }

def classify_category(email_text: str) -> dict:
    """Helper function to classify an email's fraud category."""
    return CategoryClassifierService.classify_category(email_text)
