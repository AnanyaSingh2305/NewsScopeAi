import os
import torch
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments

def preprocess_function(examples, tokenizer):
    return tokenizer(examples['statement'], padding="max_length", truncation=True, max_length=128)

def map_labels(example):
    fake_labels = [0, 1, 2]
    example['label'] = 0 if example['label'] in fake_labels else 1
    return example

def main():
    print("Loading LIAR dataset...")
    try:
        dataset = load_dataset("liar")
    except Exception as e:
        print(f"Error loading dataset: {e}. Are you offline?")
        return
    
    print("Mapping labels to binary REAL/FAKE...")
    dataset = dataset.map(map_labels)
    
    model_name = "roberta-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    print("Tokenizing dataset...")
    tokenized_datasets = dataset.map(lambda x: preprocess_function(x, tokenizer), batched=True)
    
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    
    training_args = TrainingArguments(
        output_dir="./models/fake_news_model",
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=3,
        weight_decay=0.01,
        save_strategy="epoch",
        load_best_model_at_end=True,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
    )
    
    print("Starting training on CPU/GPU depending on environment...")
    trainer.train()
    
    print("Saving model to ./models/fake_news_model...")
    model.save_pretrained("./models/fake_news_model")
    tokenizer.save_pretrained("./models/fake_news_model")
    print("Training complete! Model saved successfully.")

if __name__ == "__main__":
    main()
