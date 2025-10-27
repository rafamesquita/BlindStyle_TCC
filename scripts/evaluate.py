"""
Evaluation Script for MCN Outfit Compatibility Model

This script evaluates a trained model on the test set and generates:
- Metrics (Accuracy, AUC, Precision, Recall, F1)
- Confusion matrix
- Probability distribution plots
- Classification report

Usage:
    python scripts/evaluate.py
    
    # Or with custom checkpoint:
    python scripts/evaluate.py --checkpoint checkpoints/my_model.pth
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import numpy as np
import yaml
import argparse
from datetime import datetime

from models.compat_model import create_model
from models.dataset import get_dataloaders
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
    roc_curve
)

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Evaluate MCN Outfit Compatibility Model'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--checkpoint',
        type=str,
        default='checkpoints/best_model.pth',
        help='Path to model checkpoint'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='results',
        help='Output directory for results and plots'
    )
    
    return parser.parse_args()


def load_checkpoint(model, checkpoint_path: str, device: str):
    """Load model from checkpoint"""
    if not Path(checkpoint_path).exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    
    print(f"✅ Model loaded from: {checkpoint_path}")
    print(f"  Epoch: {checkpoint.get('epoch', 'N/A')}")
    print(f"  Best validation AUC: {checkpoint.get('best_val_auc', 'N/A'):.4f}")
    
    return model


def evaluate_model(model, test_loader, device: str):
    """Evaluate model on test set"""
    model.eval()
    model.to(device)
    
    all_preds = []
    all_probs = []
    all_labels = []
    all_outfit_ids = []
    all_num_items = []
    
    # Collect samples by category for detailed analysis
    samples_by_category = {
        'tp': [],  # True Positives
        'tn': [],  # True Negatives
        'fp': [],  # False Positives
        'fn': []   # False Negatives
    }
    
    print("\n🧪 Evaluating model on test set...")
    
    with torch.no_grad():
        for batch in test_loader:
            embeddings = batch['embeddings'].to(device)
            mask = batch['mask'].to(device)
            labels = batch['label'].to(device).squeeze()
            num_items = batch['num_items'].cpu().squeeze()
            
            # Forward pass
            outputs = model(embeddings, mask)
            
            # Collect results
            batch_probs = outputs.cpu().numpy()
            batch_preds = (outputs > 0.5).cpu().numpy()
            batch_labels = labels.cpu().numpy()
            batch_outfit_ids = batch['outfit_id']
            batch_num_items = num_items.numpy()
            
            all_probs.extend(batch_probs)
            all_preds.extend(batch_preds)
            all_labels.extend(batch_labels)
            all_outfit_ids.extend(batch_outfit_ids)
            all_num_items.extend(batch_num_items)
            
            # Categorize predictions for sample analysis
            for i in range(len(batch_labels)):
                pred = int(batch_preds[i])
                label = int(batch_labels[i])
                prob = float(batch_probs[i])
                
                sample_info = {
                    'outfit_id': batch_outfit_ids[i],
                    'probability': prob,
                    'predicted': pred,
                    'actual': label,
                    'num_items': int(batch_num_items[i])
                }
                
                # Categorize sample
                if pred == 1 and label == 1:
                    samples_by_category['tp'].append(sample_info)
                elif pred == 0 and label == 0:
                    samples_by_category['tn'].append(sample_info)
                elif pred == 1 and label == 0:
                    samples_by_category['fp'].append(sample_info)
                else:  # pred == 0 and label == 1
                    samples_by_category['fn'].append(sample_info)
    
    # Convert to arrays
    all_preds = np.array(all_preds)
    all_probs = np.array(all_probs)
    all_labels = np.array(all_labels)
    
    # Compute metrics
    accuracy = accuracy_score(all_labels, all_preds)
    auc = roc_auc_score(all_labels, all_probs)
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_preds, average='binary', zero_division=0
    )
    
    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds)
    
    # Print results
    print("\n" + "="*70)
    print("📊 EVALUATION RESULTS")
    print("="*70)
    print(f"\n  Overall Metrics:")
    print(f"    Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"    AUC:       {auc:.4f}")
    print(f"    Precision: {precision:.4f}")
    print(f"    Recall:    {recall:.4f}")
    print(f"    F1-Score:  {f1:.4f}")
    
    print(f"\n  Confusion Matrix:")
    print(f"                   Predicted")
    print(f"                   Incomp.  Compat.")
    print(f"    Actual Incomp.  {cm[0,0]:6d}  {cm[0,1]:6d}")
    print(f"           Compat.  {cm[1,0]:6d}  {cm[1,1]:6d}")
    
    print(f"\n  Detailed Breakdown:")
    print(f"    True Negatives:  {cm[0,0]:6d}")
    print(f"    False Positives: {cm[0,1]:6d}")
    print(f"    False Negatives: {cm[1,0]:6d}")
    print(f"    True Positives:  {cm[1,1]:6d}")
    
    # Classification report
    print(f"\n  Classification Report:")
    print(classification_report(
        all_labels,
        all_preds,
        target_names=['Incompatible', 'Compatible'],
        digits=4
    ))
    
    print("="*70 + "\n")
    
    return {
        'accuracy': accuracy,
        'auc': auc,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm,
        'predictions': all_preds,
        'probabilities': all_probs,
        'labels': all_labels,
        'outfit_ids': all_outfit_ids,
        'samples_by_category': samples_by_category
    }


def display_sample_predictions(samples_by_category: dict, num_samples: int = 5):
    """
    Display sample predictions for each category
    
    Args:
        samples_by_category: Dict with keys 'tp', 'tn', 'fp', 'fn'
        num_samples: Number of samples to show per category
    """
    print("\n" + "="*70)
    print("📸 SAMPLE PREDICTIONS BY CATEGORY")
    print("="*70)
    
    categories = [
        ('tp', '✅ TRUE POSITIVES', 'Correctly Predicted Compatible', True),
        ('tn', '✅ TRUE NEGATIVES', 'Correctly Predicted Incompatible', True),
        ('fp', '❌ FALSE POSITIVES', 'Wrongly Predicted Compatible', False),
        ('fn', '❌ FALSE NEGATIVES', 'Wrongly Predicted Incompatible', False)
    ]
    
    for cat_key, cat_title, cat_desc, is_correct in categories:
        samples = samples_by_category[cat_key]
        
        print(f"\n{cat_title} ({cat_desc})")
        print("-" * 70)
        print(f"Total: {len(samples)} samples")
        
        if len(samples) == 0:
            print("  No samples in this category.")
            continue
        
        # Sort by confidence (probability)
        # For correct predictions: show highest confidence first
        # For incorrect predictions: show highest confidence first (most confident mistakes)
        sorted_samples = sorted(samples, key=lambda x: x['probability'], reverse=True)
        
        # Show top N samples
        display_count = min(num_samples, len(sorted_samples))
        print(f"Showing top {display_count} by confidence:\n")
        
        for i, sample in enumerate(sorted_samples[:display_count], 1):
            actual_label = "Compatible" if sample['actual'] == 1 else "Incompatible"
            pred_label = "Compatible" if sample['predicted'] == 1 else "Incompatible"
            confidence = sample['probability'] if sample['predicted'] == 1 else (1 - sample['probability'])
            
            print(f"  Sample {i}: {sample['outfit_id']}")
            print(f"    Prediction: {pred_label} (confidence: {confidence:.4f})")
            print(f"    Actual: {actual_label}")
            print(f"    Probability: {sample['probability']:.4f}")
            print(f"    Items: {sample['num_items']} pieces")
            
            if not is_correct:
                # Add insight for errors
                if cat_key == 'fp':
                    print(f"    ⚠️  Model was overconfident - predicted compatible but was incompatible")
                else:  # fn
                    print(f"    ⚠️  Model missed this compatible outfit")
            
            print()
    
    print("="*70)


def save_sample_predictions(samples_by_category: dict, output_dir: Path, num_samples: int = 10):
    """
    Save sample predictions to JSON file
    
    Args:
        samples_by_category: Dict with keys 'tp', 'tn', 'fp', 'fn'
        output_dir: Directory to save the file
        num_samples: Number of samples to save per category
    """
    output_path = output_dir / 'sample_predictions.json'
    
    # Prepare data for JSON
    json_data = {
        'metadata': {
            'description': 'Sample predictions categorized by prediction outcome',
            'categories': {
                'tp': 'True Positives - Correctly predicted compatible',
                'tn': 'True Negatives - Correctly predicted incompatible',
                'fp': 'False Positives - Wrongly predicted compatible',
                'fn': 'False Negatives - Wrongly predicted incompatible'
            },
            'num_samples_per_category': num_samples
        },
        'samples': {}
    }
    
    # Add samples for each category
    for cat_key, samples in samples_by_category.items():
        # Sort by confidence
        sorted_samples = sorted(samples, key=lambda x: x['probability'], reverse=True)
        
        # Take top N
        top_samples = sorted_samples[:num_samples]
        
        json_data['samples'][cat_key] = {
            'total_count': len(samples),
            'top_samples': top_samples
        }
    
    # Save to JSON
    import json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"  💾 Sample predictions saved: {output_path}")


def plot_sample_predictions(samples_by_category: dict, output_dir: Path):
    """
    Create visualization showing confidence distribution for each category
    
    Args:
        samples_by_category: Dict with keys 'tp', 'tn', 'fp', 'fn'
        output_dir: Directory to save the plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Prediction Confidence Distribution by Category', fontsize=16, fontweight='bold')
    
    categories = [
        ('tp', '✅ True Positives\n(Correct Compatible)', 0, 0, 'green'),
        ('tn', '✅ True Negatives\n(Correct Incompatible)', 0, 1, 'blue'),
        ('fp', '❌ False Positives\n(Wrong Compatible)', 1, 0, 'red'),
        ('fn', '❌ False Negatives\n(Wrong Incompatible)', 1, 1, 'orange')
    ]
    
    for cat_key, cat_title, row, col, color in categories:
        ax = axes[row, col]
        samples = samples_by_category[cat_key]
        
        if len(samples) == 0:
            ax.text(0.5, 0.5, 'No samples', ha='center', va='center', fontsize=14)
            ax.set_title(f"{cat_title}\n(0 samples)", fontweight='bold')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            continue
        
        # Extract probabilities
        probs = [s['probability'] for s in samples]
        
        # Create histogram
        ax.hist(probs, bins=20, color=color, alpha=0.7, edgecolor='black')
        
        # Add threshold line
        ax.axvline(x=0.5, color='black', linestyle='--', linewidth=2, label='Threshold (0.5)')
        
        # Add statistics
        mean_prob = np.mean(probs)
        ax.axvline(x=mean_prob, color='darkred', linestyle='-', linewidth=2, label=f'Mean: {mean_prob:.3f}')
        
        ax.set_title(f"{cat_title}\n({len(samples)} samples)", fontweight='bold')
        ax.set_xlabel('Predicted Probability', fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
    
    plt.tight_layout()
    
    output_path = output_dir / 'sample_predictions.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  💾 Sample visualization saved: {output_path}")


def plot_confusion_matrix(cm, output_dir: Path):
    """Plot and save confusion matrix"""
    plt.figure(figsize=(8, 6))
    
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=['Incompatible', 'Compatible'],
        yticklabels=['Incompatible', 'Compatible'],
        cbar_kws={'label': 'Count'}
    )
    
    plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    
    output_path = output_dir / 'confusion_matrix.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  💾 Confusion matrix saved: {output_path}")


def plot_probability_distribution(probs, labels, output_dir: Path):
    """Plot distribution of predicted probabilities"""
    plt.figure(figsize=(10, 6))
    
    # Plot histograms
    plt.hist(
        probs[labels == 0],
        bins=50,
        alpha=0.6,
        label='Incompatible (True)',
        color='red',
        edgecolor='black'
    )
    plt.hist(
        probs[labels == 1],
        bins=50,
        alpha=0.6,
        label='Compatible (True)',
        color='green',
        edgecolor='black'
    )
    
    # Add vertical line at threshold
    plt.axvline(x=0.5, color='black', linestyle='--', linewidth=2, label='Threshold (0.5)')
    
    plt.xlabel('Predicted Probability', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Distribution of Predicted Probabilities', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_path = output_dir / 'probability_distribution.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  💾 Probability distribution saved: {output_path}")


def plot_roc_curve(labels, probs, auc_score, output_dir: Path):
    """Plot ROC curve"""
    fpr, tpr, thresholds = roc_curve(labels, probs)
    
    plt.figure(figsize=(8, 8))
    
    # Plot ROC curve
    plt.plot(fpr, tpr, linewidth=2, label=f'ROC Curve (AUC = {auc_score:.4f})')
    
    # Plot diagonal line (random classifier)
    plt.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random Classifier')
    
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curve', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_path = output_dir / 'roc_curve.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  💾 ROC curve saved: {output_path}")


def save_metrics_to_file(results: dict, output_dir: Path):
    """Save metrics to text file"""
    output_path = output_dir / 'metrics.txt'
    
    with open(output_path, 'w') as f:
        f.write("MCN OUTFIT COMPATIBILITY MODEL - EVALUATION RESULTS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("Overall Metrics:\n")
        f.write(f"  Accuracy:  {results['accuracy']:.4f}\n")
        f.write(f"  AUC:       {results['auc']:.4f}\n")
        f.write(f"  Precision: {results['precision']:.4f}\n")
        f.write(f"  Recall:    {results['recall']:.4f}\n")
        f.write(f"  F1-Score:  {results['f1']:.4f}\n\n")
        
        cm = results['confusion_matrix']
        f.write("Confusion Matrix:\n")
        f.write(f"  True Negatives:  {cm[0,0]}\n")
        f.write(f"  False Positives: {cm[0,1]}\n")
        f.write(f"  False Negatives: {cm[1,0]}\n")
        f.write(f"  True Positives:  {cm[1,1]}\n")
    
    print(f"  💾 Metrics saved: {output_path}")


def main():
    """Main evaluation function"""
    args = parse_args()
    
    # Print header
    print("\n" + "📊"*35)
    print("MCN OUTFIT COMPATIBILITY MODEL - EVALUATION")
    print("📊"*35 + "\n")
    
    # Load configuration
    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Determine device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"💻 Using device: {device.upper()}")
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")
    
    # Load test data
    print(f"\n📦 Loading test dataset...")
    _, _, test_loader = get_dataloaders(
        data_path=config['data_path'],
        batch_size=config.get('eval_batch_size', 64),
        max_items=config['max_items'],
        num_workers=config.get('num_workers', 0),
        seed=config['seed']
    )
    
    # Create and load model
    print(f"\n🏗️  Creating model...")
    model = create_model(config)
    model = load_checkpoint(model, args.checkpoint, device)
    
    # Evaluate
    results = evaluate_model(model, test_loader, device)
    
    # Display sample predictions
    display_sample_predictions(
        results['samples_by_category'],
        num_samples=5
    )
    
    # Generate plots
    print(f"\n📈 Generating visualizations...")
    plot_confusion_matrix(results['confusion_matrix'], output_dir)
    plot_probability_distribution(
        results['probabilities'],
        results['labels'],
        output_dir
    )
    plot_roc_curve(
        results['labels'],
        results['probabilities'],
        results['auc'],
        output_dir
    )
    
    # Save sample predictions
    save_sample_predictions(
        results['samples_by_category'],
        output_dir,
        num_samples=10
    )
    
    # Plot sample predictions distribution
    plot_sample_predictions(
        results['samples_by_category'],
        output_dir
    )
    
    # Save metrics
    save_metrics_to_file(results, output_dir)
    
    # Summary
    print(f"\n" + "✅"*35)
    print("EVALUATION COMPLETED!")
    print("✅"*35)
    print(f"\n📊 Results summary:")
    print(f"  Accuracy: {results['accuracy']:.4f}")
    print(f"  AUC:      {results['auc']:.4f}")
    print(f"  F1-Score: {results['f1']:.4f}")
    print(f"\n📁 All results saved to: {output_dir}/")
    print(f"  - metrics.txt")
    print(f"  - confusion_matrix.png")
    print(f"  - probability_distribution.png")
    print(f"  - roc_curve.png")
    print(f"  - sample_predictions.json")
    print(f"  - sample_predictions.png")
    print()


if __name__ == "__main__":
    main()
