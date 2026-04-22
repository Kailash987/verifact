"""
Training script for fake news detection model.
"""

import os
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    get_linear_schedule_with_warmup
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
import numpy as np
from tqdm import tqdm
import json
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

from preprocessing import TextPreprocessor, load_and_preprocess_dataset


class FakeNewsDataset(Dataset):
    """Custom dataset for fake news classification."""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


class FakeNewsTrainer:
    """Trainer class for fake news detection model."""
    
    def __init__(self, model_name: str = "distilbert-base-uncased", 
                 model_save_path: str = "ml/model"):
        self.model_name = model_name
        self.model_save_path = model_save_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Create model directory if it doesn't exist
        os.makedirs(model_save_path, exist_ok=True)
        
        # Initialize model and tokenizer
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, 
            num_labels=2  # Binary classification
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Move model to device
        self.model.to(self.device)
        
        # Training history
        self.train_history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': []
        }
    
    def prepare_data(self, texts: List[str], labels: List[int], 
                    test_size: float = 0.2, random_state: int = 42) -> Tuple[DataLoader, DataLoader]:
        """
        Prepare train and validation data loaders.
        
        Args:
            texts: List of input texts
            labels: List of corresponding labels
            test_size: Fraction of data for validation
            random_state: Random seed
            
        Returns:
            Tuple of (train_loader, val_loader)
        """
        # Split data
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=test_size, random_state=random_state, stratify=labels
        )
        
        # Create datasets
        train_dataset = FakeNewsDataset(train_texts, train_labels, self.tokenizer)
        val_dataset = FakeNewsDataset(val_texts, val_labels, self.tokenizer)
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False)
        
        return train_loader, val_loader
    
    def train_epoch(self, train_loader: DataLoader, optimizer, scheduler) -> Tuple[float, float]:
        """
        Train for one epoch.
        
        Args:
            train_loader: Training data loader
            optimizer: Optimizer
            scheduler: Learning rate scheduler
            
        Returns:
            Tuple of (average_loss, accuracy)
        """
        self.model.train()
        total_loss = 0
        predictions = []
        true_labels = []
        
        for batch in tqdm(train_loader, desc="Training"):
            # Move batch to device
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            # Clear gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            total_loss += loss.item()
            
            # Backward pass
            loss.backward()
            optimizer.step()
            scheduler.step()
            
            # Get predictions
            preds = torch.argmax(outputs.logits, dim=1)
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
        
        # Calculate metrics
        avg_loss = total_loss / len(train_loader)
        accuracy = accuracy_score(true_labels, predictions)
        
        return avg_loss, accuracy
    
    def validate(self, val_loader: DataLoader) -> Tuple[float, float, Dict]:
        """
        Validate the model.
        
        Args:
            val_loader: Validation data loader
            
        Returns:
            Tuple of (val_loss, accuracy, metrics_dict)
        """
        self.model.eval()
        total_loss = 0
        predictions = []
        true_labels = []
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validating"):
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                total_loss += loss.item()
                
                # Get predictions
                preds = torch.argmax(outputs.logits, dim=1)
                predictions.extend(preds.cpu().numpy())
                true_labels.extend(labels.cpu().numpy())
        
        # Calculate metrics
        avg_loss = total_loss / len(val_loader)
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_labels, predictions, average='binary'
        )
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
        
        return avg_loss, accuracy, metrics
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader,
              epochs: int = 3, learning_rate: float = 2e-5, 
              early_stopping_patience: int = 2) -> Dict:
        """
        Train the model.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of training epochs
            learning_rate: Learning rate
            early_stopping_patience: Patience for early stopping
            
        Returns:
            Training history and final metrics
        """
        # Setup optimizer and scheduler
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer, num_warmup_steps=0, num_training_steps=total_steps
        )
        
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            print(f"\nEpoch {epoch + 1}/{epochs}")
            print("-" * 50)
            
            # Train
            train_loss, train_acc = self.train_epoch(train_loader, optimizer, scheduler)
            
            # Validate
            val_loss, val_acc, val_metrics = self.validate(val_loader)
            
            # Update history
            self.train_history['train_loss'].append(train_loss)
            self.train_history['val_loss'].append(val_loss)
            self.train_history['train_acc'].append(train_acc)
            self.train_history['val_acc'].append(val_acc)
            
            # Print metrics
            print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            print(f"Val F1: {val_metrics['f1']:.4f}")
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                self.save_model("best_model")
            else:
                patience_counter += 1
                
            if patience_counter >= early_stopping_patience:
                print(f"Early stopping triggered after epoch {epoch + 1}")
                break
        
        # Save final model
        self.save_model("final_model")
        
        return {
            'history': self.train_history,
            'final_metrics': val_metrics
        }
    
    def save_model(self, model_name: str):
        """Save model and tokenizer."""
        model_path = os.path.join(self.model_save_path, model_name)
        os.makedirs(model_path, exist_ok=True)
        
        self.model.save_pretrained(model_path)
        self.tokenizer.save_pretrained(model_path)
        
        # Save training history
        history_path = os.path.join(model_path, 'training_history.json')
        with open(history_path, 'w') as f:
            json.dump(self.train_history, f, indent=2)
        
        print(f"Model saved to {model_path}")
    
    def plot_training_history(self):
        """Plot training history."""
        plt.figure(figsize=(12, 4))
        
        # Loss plot
        plt.subplot(1, 2, 1)
        plt.plot(self.train_history['train_loss'], label='Train Loss')
        plt.plot(self.train_history['val_loss'], label='Val Loss')
        plt.title('Training and Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        # Accuracy plot
        plt.subplot(1, 2, 2)
        plt.plot(self.train_history['train_acc'], label='Train Acc')
        plt.plot(self.train_history['val_acc'], label='Val Acc')
        plt.title('Training and Validation Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.model_save_path, 'training_history.png'))
        plt.show()


def main():
    """Main training function."""
    print("Starting Fake News Detection Model Training...")
    
    # Load data
    print("Loading and preprocessing data...")
    texts, labels = load_and_preprocess_dataset()
    print(f"Loaded {len(texts)} samples")
    
    # Initialize trainer
    trainer = FakeNewsTrainer()
    
    # Prepare data
    train_loader, val_loader = trainer.prepare_data(texts, labels)
    
    # Train model
    print("Starting training...")
    results = trainer.train(train_loader, val_loader, epochs=5)
    
    # Plot results
    trainer.plot_training_history()
    
    print("\nTraining completed!")
    print(f"Final metrics: {results['final_metrics']}")
    print(f"Model saved to: {trainer.model_save_path}")


if __name__ == "__main__":
    main()
