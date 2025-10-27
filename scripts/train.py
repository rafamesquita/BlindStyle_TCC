"""
Main Training Script for MCN Outfit Compatibility Model

This script:
1. Loads configuration from config/config.yaml
2. Creates datasets and dataloaders
3. Initializes the MCN model
4. Trains the model with validation
5. Saves checkpoints and best model

🔧 TO TRAIN WITH MORE EPOCHS:
   Edit config/config.yaml and change 'num_epochs' parameter
   Current default: 5 (for testing)
   Recommended for full training: 50-100 epochs

Usage:
    python scripts/train.py
    
    # Or with custom config:
    python scripts/train.py --config path/to/config.yaml
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import yaml
import argparse
from datetime import datetime

from models.dataset import get_dataloaders
from models.compat_model import create_model
from models.trainer import CompatibilityTrainer


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Train MCN Outfit Compatibility Model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train with default config
  python scripts/train.py
  
  # Train with custom config
  python scripts/train.py --config my_config.yaml
  
  # Resume from checkpoint
  python scripts/train.py --resume checkpoints/checkpoint_epoch_10.pth
  
  # Override epochs from command line
  python scripts/train.py --epochs 100
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '--resume',
        type=str,
        default=None,
        help='Path to checkpoint to resume training from'
    )
    
    parser.add_argument(
        '--epochs',
        type=int,
        default=None,
        help='Override number of epochs from config'
    )
    
    parser.add_argument(
        '--device',
        type=str,
        default=None,
        choices=['cuda', 'cpu', 'auto'],
        help='Override device from config'
    )
    
    return parser.parse_args()


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print(f"✅ Configuration loaded from: {config_path}")
    return config


def get_device(config: dict) -> str:
    """Determine device to use for training"""
    device_config = config.get('device', 'auto')
    
    if device_config == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        device = device_config
    
    # Validate CUDA availability
    if device == 'cuda' and not torch.cuda.is_available():
        print("⚠️  CUDA requested but not available. Falling back to CPU.")
        device = 'cpu'
    
    return device


def print_config_summary(config: dict, device: str):
    """Print training configuration summary"""
    print("\n" + "="*70)
    print("TRAINING CONFIGURATION")
    print("="*70)
    print(f"📁 Data path: {config['data_path']}")
    print(f"💾 Checkpoint dir: {config['checkpoint_dir']}")
    print(f"📊 Log dir: {config['log_dir']}")
    print(f"\n🎯 Training Settings:")
    print(f"  Epochs: {config['num_epochs']} 🔧 (Change in config.yaml for full training)")
    print(f"  Batch size: {config['batch_size']}")
    print(f"  Learning rate: {config['learning_rate']}")
    print(f"  Early stopping patience: {config['early_stopping_patience']}")
    print(f"\n🏗️  Model Architecture:")
    print(f"  Input dimension: {config['embed_input_size']}")
    print(f"  Projection dimension: {config['embed_proj_size']}")
    print(f"  Max items: {config['max_items']}")
    print(f"  Dropout: {config['dropout']}")
    print(f"\n💻 Hardware:")
    print(f"  Device: {device.upper()}")
    if device == 'cuda':
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
    print("="*70 + "\n")


def main():
    """Main training function"""
    # Parse arguments
    args = parse_args()
    
    # Print header
    print("\n" + "🎨"*35)
    print("MCN OUTFIT COMPATIBILITY MODEL - TRAINING")
    print("🎨"*35)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.epochs is not None:
        print(f"⚠️  Overriding epochs: {config['num_epochs']} → {args.epochs}")
        config['num_epochs'] = args.epochs
    
    if args.device is not None:
        config['device'] = args.device
    
    # Determine device
    device = get_device(config)
    
    # Print configuration
    print_config_summary(config, device)
    
    # Create dataloaders
    print("📦 Loading datasets...")
    train_loader, val_loader, test_loader = get_dataloaders(
        data_path=config['data_path'],
        batch_size=config['batch_size'],
        max_items=config['max_items'],
        num_workers=config.get('num_workers', 0),
        seed=config['seed'],
        train_ratio=config['train_ratio'],
        val_ratio=config['val_ratio']
    )
    
    # Create model
    print("\n🏗️  Building model...")
    model = create_model(config)
    
    # Create optimizer
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config['learning_rate'],
        weight_decay=config['weight_decay']
    )
    
    # Create learning rate scheduler
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer,
        step_size=config['lr_step_size'],
        gamma=config['lr_gamma']
    )
    
    # Create trainer
    print("\n🏃 Initializing trainer...")
    trainer = CompatibilityTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer,
        scheduler=scheduler,
        device=device,
        checkpoint_dir=config['checkpoint_dir'],
        log_dir=config['log_dir']
    )
    
    # Resume from checkpoint if specified
    start_epoch = 0
    if args.resume:
        print(f"\n♻️  Resuming from checkpoint: {args.resume}")
        checkpoint = torch.load(args.resume, map_location=device, weights_only=False)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        if scheduler and 'scheduler_state_dict' in checkpoint:
            scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        start_epoch = checkpoint['epoch']
        print(f"✅ Resumed from epoch {start_epoch}")
    
    # Train
    print("\n" + "🚀"*35)
    print("STARTING TRAINING")
    print("🚀"*35 + "\n")
    
    try:
        trainer.train(num_epochs=config['num_epochs'])
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        print("Saving current state...")
        trainer._save_checkpoint('interrupted.pth', {})
        print("✅ State saved to checkpoints/interrupted.pth")
    except Exception as e:
        print(f"\n\n❌ Training failed with error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Training complete
    print("\n" + "✅"*35)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("✅"*35)
    
    print(f"\n📊 Final Results:")
    print(f"  Best validation AUC: {trainer.best_val_auc:.4f}")
    print(f"  Best validation Accuracy: {trainer.best_val_acc:.4f}")
    print(f"\n💾 Best model saved to: {Path(config['checkpoint_dir']) / 'best_model.pth'}")
    print(f"📈 View training progress: tensorboard --logdir={config['log_dir']}")
    print(f"\n🎯 Next steps:")
    print(f"  1. Run evaluation: python scripts/evaluate.py")
    print(f"  2. View TensorBoard: tensorboard --logdir={config['log_dir']}")
    print(f"  3. For full training, edit config/config.yaml and set num_epochs to 50-100")
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


if __name__ == "__main__":
    main()
