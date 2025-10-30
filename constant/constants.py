"""Constants and default configurations"""
from transformers import TrainingArguments

default_training_args = TrainingArguments(
<<<<<<< HEAD
    output_dir="./models_saved_checkpoints",
    eval_strategy="steps",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=5e-5,
    logging_steps=100,
    save_steps=500,
    save_total_limit=2,
    fp16=True,
    save_strategy="no",
=======
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
    save_strategy="epoch",
    load_best_model_at_end=True,
    logging_dir="./logs",
    logging_steps=10,
    save_total_limit=2,
>>>>>>> d26a4cb (update crawl)
)

