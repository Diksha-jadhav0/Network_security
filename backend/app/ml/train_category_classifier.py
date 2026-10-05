import os
import sys
import json
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "phishing_categories.csv")
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "category_model")

LABEL_LIST = [
    "BANKING_FRAUD",
    "TRANSACTION_FRAUD",
    "LOTTERY_SCAM",
    "JOB_FRAUD",
    "ENTERTAINMENT_SCAM",
    "CRYPTO_INVESTMENT_SCAM",
    "ACCOUNT_VERIFICATION_SCAM"
]

LABEL2ID = {label: idx for idx, label in enumerate(LABEL_LIST)}
ID2LABEL = {idx: label for idx, label in enumerate(LABEL_LIST)}

def ensure_dataset():
    """Ensure dataset exists, if missing generate synthetic dataset."""
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at {DATASET_PATH}. Generating synthetic category dataset...")
        gen_script = os.path.join(BASE_DIR, "dataset", "generate_category_dataset.py")
        if os.path.exists(gen_script):
            import subprocess
            subprocess.run([sys.executable, gen_script], check=True)
        else:
            raise FileNotFoundError(f"Neither dataset {DATASET_PATH} nor generator {gen_script} was found.")

class CategoryDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.labels)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted', zero_division=0)
    acc = accuracy_score(labels, predictions)
    return {
        'accuracy': acc,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

def train():
    ensure_dataset()
    print(f"Loading category dataset from {DATASET_PATH}...")
    df = pd.read_csv(DATASET_PATH)
    
    # Filter rows with valid labels
    df = df[df['label'].isin(LABEL_LIST)].copy()
    print(f"Loaded {len(df)} samples across {len(LABEL_LIST)} categories.")
    
    df['label_id'] = df['label'].map(LABEL2ID)
    
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['text'].tolist(),
        df['label_id'].tolist(),
        test_size=0.2,
        random_state=42,
        stratify=df['label_id'].tolist()
    )

    print("Initializing DistilBertTokenizerFast...")
    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

    print("Tokenizing datasets (max_length=128)...")
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128)

    train_dataset = CategoryDataset(train_encodings, train_labels)
    val_dataset = CategoryDataset(val_encodings, val_labels)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Training device: {device}")

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=len(LABEL_LIST),
        id2label=ID2LABEL,
        label2id=LABEL2ID
    )

    training_args = TrainingArguments(
        output_dir=os.path.join(MODEL_DIR, "results"),
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=8,
        gradient_accumulation_steps=2,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_steps=10,
        learning_rate=3e-5,
        weight_decay=0.01,
        no_cuda=(device == "cpu"),
        use_mps_device=False,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics
    )

    print("Starting DistilBERT fine-tuning...")
    trainer.train()

    print("Evaluating model performance...")
    eval_results = trainer.evaluate()

    print("\n" + "="*40)
    print("DISTILBERT CATEGORY CLASSIFIER EVALUATION METRICS:")
    print(f"  Accuracy:  {eval_results.get('eval_accuracy', 0.0):.4f}")
    print(f"  Precision: {eval_results.get('eval_precision', 0.0):.4f}")
    print(f"  Recall:    {eval_results.get('eval_recall', 0.0):.4f}")
    print(f"  F1 Score:  {eval_results.get('eval_f1', 0.0):.4f}")
    print("="*40 + "\n")

    os.makedirs(MODEL_DIR, exist_ok=True)
    print(f"Saving fine-tuned DistilBERT model to {MODEL_DIR}...")
    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)

    # Save metadata mapping for service
    with open(os.path.join(MODEL_DIR, "label_mapping.json"), "w") as f:
        json.dump({
            "label2id": LABEL2ID,
            "id2label": {str(k): v for k, v in ID2LABEL.items()}
        }, f, indent=2)

    print("DistilBERT category model training completed successfully!")

if __name__ == "__main__":
    train()
