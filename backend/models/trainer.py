"""
Training Loop for Outfit Compatibility Model

This module implements the trainer class with:
- Training and validation loops
- Metrics computation (AUC, Accuracy, Precision, Recall, F1)
- Checkpointing and early stopping
- TensorBoard logging
"""

import torch
import torch.nn as nn
from torch.utils.tensorboard import SummaryWriter
from pathlib import Path
from tqdm import tqdm
import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix
)
from typing import Dict, Optional
import time


class CompatibilityTrainer:
    """Trainer for outfit compatibility model"""

    def __init__(
        self,
        model: nn.Module,
        train_loader,
        val_loader,
        optimizer,
        scheduler,
        device: str = 'cuda',
        checkpoint_dir: str = './checkpoints',
        log_dir: str = './logs',
        early_stopping_patience: int = 20
    ):
        """
        Initialize trainer
        
        Args:
            model: PyTorch model to train
            train_loader: Training data loader
            val_loader: Validation data loader
            optimizer: Optimizer
            scheduler: Learning rate scheduler
            device: Device to train on ('cuda' or 'cpu')
            checkpoint_dir: Directory to save checkpoints
            log_dir: Directory for TensorBoard logs
            early_stopping_patience: Epochs to wait before early stopping
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device

        # Directories
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # TensorBoard writer
        self.writer = SummaryWriter(log_dir)

        # Loss function (Binary Cross Entropy)
        self.criterion = nn.BCELoss()

        # Tracking
        self.best_val_auc = 0.0
        self.best_val_acc = 0.0
        self.current_epoch = 0
        self.early_stopping_patience = early_stopping_patience
        self.epochs_without_improvement = 0

        print(f"\n🎯 Trainer initialized:")
        print(f"  Device: {self.device}")
        print(f"  Train batches: {len(self.train_loader)}")
        print(f"  Val batches: {len(self.val_loader)}")
        print(f"  Early stopping patience: {self.early_stopping_patience}")

    def train_epoch(self) -> Dict[str, float]:
        """
        Train for one epoch
        
        Returns:
            Dictionary with training metrics
        """
        self.model.train()

        total_loss = 0.0
        all_preds = []
        all_labels = []

        pbar = tqdm(
            self.train_loader,
            desc=f"Epoch {self.current_epoch+1} [TRAIN]",
            leave=False
        )

        for batch in pbar:
            # Move data to device
            embeddings = batch['embeddings'].to(self.device)
            mask = batch['mask'].to(self.device)
            labels = batch['label'].to(self.device).squeeze()

            # Forward pass
            outputs = self.model(embeddings, mask)
            loss = self.criterion(outputs, labels)

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()

            # Gradient clipping to prevent exploding gradients
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

            self.optimizer.step()

            # Track metrics
            total_loss += loss.item()
            all_preds.extend(outputs.detach().cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

            # Update progress bar
            pbar.set_postfix({'loss': f"{loss.item():.4f}"})

        # Compute epoch metrics
        avg_loss = total_loss / len(self.train_loader)
        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)

        # Binary predictions (threshold = 0.5)
        pred_binary = (all_preds > 0.5).astype(int)
        accuracy = accuracy_score(all_labels, pred_binary)

        # AUC score
        try:
            auc = roc_auc_score(all_labels, all_preds)
        except ValueError:
            auc = 0.0

        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'auc': auc
        }

    def validate(self) -> Dict[str, float]:
        """
        Validate the model
        
        Returns:
            Dictionary with validation metrics
        """
        self.model.eval()

        total_loss = 0.0
        all_preds = []
        all_labels = []

        with torch.no_grad():
            pbar = tqdm(
                self.val_loader,
                desc=f"Epoch {self.current_epoch+1} [VAL]",
                leave=False
            )

            for batch in pbar:
                # Move data to device
                embeddings = batch['embeddings'].to(self.device)
                mask = batch['mask'].to(self.device)
                labels = batch['label'].to(self.device).squeeze()

                # Forward pass
                outputs = self.model(embeddings, mask)
                loss = self.criterion(outputs, labels)

                # Track metrics
                total_loss += loss.item()
                all_preds.extend(outputs.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())

                # Update progress bar
                pbar.set_postfix({'loss': f"{loss.item():.4f}"})

        # Compute metrics
        avg_loss = total_loss / len(self.val_loader)
        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)

        pred_binary = (all_preds > 0.5).astype(int)
        accuracy = accuracy_score(all_labels, pred_binary)

        try:
            auc = roc_auc_score(all_labels, all_preds)
        except ValueError:
            auc = 0.0

        # Precision, Recall, F1
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_labels, pred_binary, average='binary', zero_division=0
        )

        # Confusion matrix
        cm = confusion_matrix(all_labels, pred_binary)

        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'auc': auc,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'confusion_matrix': cm
        }

    def train(self, num_epochs: int, start_epoch: Optional[int] = None):
        """
        Complete training loop
        
        Args:
            num_epochs: Number of epochs to train
        """
        print(f"\n🚀 Starting training for {num_epochs} epochs...")
        print(f"=" * 70)

        start_time = time.time()

        for epoch in range(start_epoch, num_epochs):
            self.current_epoch = epoch
            epoch_start = time.time()

            # Train
            train_metrics = self.train_epoch()

            # Validate
            val_metrics = self.validate()

            # Learning rate scheduling
            if self.scheduler is not None:
                self.scheduler.step()
                current_lr = self.scheduler.get_last_lr()[0]
            else:
                current_lr = self.optimizer.param_groups[0]['lr']

            # Log metrics to TensorBoard
            self._log_metrics(train_metrics, val_metrics, current_lr)

            # Calculate epoch time
            epoch_time = time.time() - epoch_start

            # Print progress
            print(f"\n{'='*70}")
            print(f"Epoch {epoch+1}/{num_epochs} (Time: {epoch_time:.1f}s, LR: {current_lr:.6f})")
            print(f"  TRAIN - Loss: {train_metrics['loss']:.4f}, "
                  f"Acc: {train_metrics['accuracy']:.4f}, "
                  f"AUC: {train_metrics['auc']:.4f}")
            print(f"  VAL   - Loss: {val_metrics['loss']:.4f}, "
                  f"Acc: {val_metrics['accuracy']:.4f}, "
                  f"AUC: {val_metrics['auc']:.4f}, "
                  f"F1: {val_metrics['f1']:.4f}")

            # Save best model
            if (epoch >= 19) and (val_metrics['auc'] > self.best_val_auc) :
                self.best_val_auc = val_metrics['auc']
                self.best_val_acc = val_metrics['accuracy']
                self.epochs_without_improvement = 0
                self._save_checkpoint('best_model.pth', val_metrics)
                print(f"  💾 New best model saved! (AUC: {self.best_val_auc:.4f})")
            else:
                self.epochs_without_improvement += 1

            # Save checkpoint every 10 epochs
            if (epoch + 1) % 10 == 0:
                self._save_checkpoint(f'checkpoint_epoch_{epoch+1}.pth', val_metrics)

            # Early stopping check
            if self.epochs_without_improvement >= self.early_stopping_patience:
                print(f"\n⏹️  Early stopping triggered after {self.early_stopping_patience} epochs without improvement")
                break

        # Training complete
        total_time = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"✅ Training completed!")
        print(f"  Total time: {total_time/60:.1f} minutes")
        print(f"  Best validation AUC: {self.best_val_auc:.4f}")
        print(f"  Best validation Accuracy: {self.best_val_acc:.4f}")
        print(f"{'='*70}\n")

        self.writer.close()

    def _log_metrics(
        self,
        train_metrics: Dict[str, float],
        val_metrics: Dict[str, float],
        learning_rate: float
    ):
        """Log metrics to TensorBoard"""
        epoch = self.current_epoch

        # Training metrics
        self.writer.add_scalar('Loss/train', train_metrics['loss'], epoch)
        self.writer.add_scalar('Accuracy/train', train_metrics['accuracy'], epoch)
        self.writer.add_scalar('AUC/train', train_metrics['auc'], epoch)

        # Validation metrics
        self.writer.add_scalar('Loss/val', val_metrics['loss'], epoch)
        self.writer.add_scalar('Accuracy/val', val_metrics['accuracy'], epoch)
        self.writer.add_scalar('AUC/val', val_metrics['auc'], epoch)
        self.writer.add_scalar('Precision/val', val_metrics['precision'], epoch)
        self.writer.add_scalar('Recall/val', val_metrics['recall'], epoch)
        self.writer.add_scalar('F1/val', val_metrics['f1'], epoch)

        # Learning rate
        self.writer.add_scalar('Learning_Rate', learning_rate, epoch)

    def _save_checkpoint(self, filename: str, metrics: Dict):
        """Save model checkpoint"""
        checkpoint_path = self.checkpoint_dir / filename

        checkpoint = {
            'epoch': self.current_epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'best_val_auc': self.best_val_auc,
            'best_val_acc': self.best_val_acc,
            'metrics': metrics
        }

        torch.save(checkpoint, checkpoint_path)

    def load_checkpoint(self, checkpoint_path: str):
        """
        Load a checkpoint
        
        Args:
            checkpoint_path: Path to checkpoint file
        """
        checkpoint = torch.load(checkpoint_path, map_location=self.device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        if self.scheduler and checkpoint['scheduler_state_dict']:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        self.current_epoch = checkpoint['epoch']
        self.best_val_auc = checkpoint['best_val_auc']
        self.best_val_acc = checkpoint['best_val_acc']

        print(f"✅ Checkpoint loaded from: {checkpoint_path}")
        print(f"  Epoch: {self.current_epoch}")
        print(f"  Best AUC: {self.best_val_auc:.4f}")


if __name__ == "__main__":
    """Test trainer with dummy data"""
    print("🧪 Testing CompatibilityTrainer...\n")
    print("Note: This requires actual model and dataloaders")
    print("Run scripts/train.py for full training pipeline")
