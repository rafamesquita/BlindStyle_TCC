"""
PyTorch Dataset for Outfit Compatibility Training

This module implements the Dataset class for loading and processing outfit embeddings
with variable numbers of items (2-5 pieces). Handles padding, masking, and train/val/test splits.
"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class OutfitCompatibilityDataset(Dataset):
    """Dataset for outfit compatibility training with padding and masking"""

    def __init__(
        self,
        data_path: str,
        max_items: int = 5,
        split: str = 'train',
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        seed: int = 42
    ):
        """
        Initialize dataset with train/val/test split
        
        Args:
            data_path: Path to data/processed/ containing NPZ and JSON files
            max_items: Maximum number of items per outfit (for padding)
            split: 'train', 'val', or 'test'
            train_ratio: Proportion of data for training (default: 0.7)
            val_ratio: Proportion of data for validation (default: 0.15)
            seed: Random seed for reproducibility
        """
        self.max_items = max_items
        self.data_path = Path(data_path)
        self.split = split

        # Load metadata
        metadata_path = self.data_path / 'metadata.json'
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")
        
        with open(metadata_path, 'r') as f:
            all_metadata = json.load(f)

        # Load embeddings
        embeddings_path = self.data_path / 'outfits_dataset.npz'
        if not embeddings_path.exists():
            raise FileNotFoundError(f"Dataset not found: {embeddings_path}")
        
        self.embeddings_data = np.load(embeddings_path, allow_pickle=True)

        # Split dataset deterministically
        np.random.seed(seed)
        total = len(all_metadata)
        indices = np.random.permutation(total)

        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)

        if split == 'train':
            self.indices = indices[:train_end]
        elif split == 'val':
            self.indices = indices[train_end:val_end]
        elif split == 'test':
            self.indices = indices[val_end:]
        else:
            raise ValueError(f"Invalid split: {split}. Must be 'train', 'val', or 'test'")

        # Filter metadata for this split
        self.metadata = [all_metadata[i] for i in self.indices]

        print(f"📦 Dataset [{split.upper()}]: {len(self.metadata)} outfits loaded")

    def __len__(self) -> int:
        """Return number of samples in this split"""
        return len(self.metadata)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a single outfit sample with padding and masking
        
        Returns:
            Dictionary containing:
                - embeddings: (max_items, 96) - padded embeddings
                - mask: (max_items,) - boolean mask (True for valid items)
                - num_items: scalar - actual number of items
                - label: scalar - compatibility label (1=compatible, 0=incompatible)
                - outfit_id: str - outfit identifier
        """
        metadata = self.metadata[idx]
        outfit_idx = self.indices[idx]

        # Load embeddings for this outfit
        embeddings = self.embeddings_data[f'outfit_{outfit_idx}']  # (num_items, 96)
        num_items = embeddings.shape[0]

        # Limit number of items if exceeds max
        if num_items > self.max_items:
            embeddings = embeddings[:self.max_items]
            num_items = self.max_items

        # Create padded embeddings (pad with zeros)
        padded_embeddings = np.zeros((self.max_items, embeddings.shape[1]), dtype=np.float32)
        padded_embeddings[:num_items] = embeddings

        # Create mask (True for valid items, False for padding)
        mask = np.zeros(self.max_items, dtype=bool)
        mask[:num_items] = True

        # Get label
        label = float(metadata['is_compatible'])

        return {
            'embeddings': torch.FloatTensor(padded_embeddings),
            'mask': torch.BoolTensor(mask),
            'num_items': torch.LongTensor([num_items]),
            'label': torch.FloatTensor([label]),
            'outfit_id': metadata['outfit_id']
        }

    def get_statistics(self) -> Dict:
        """
        Compute and return dataset statistics
        
        Returns:
            Dictionary with statistics about the dataset
        """
        num_items = [m['num_items'] for m in self.metadata]
        labels = [m['is_compatible'] for m in self.metadata]

        compatible = sum(1 for l in labels if l)
        incompatible = len(labels) - compatible

        stats = {
            'split': self.split,
            'total_outfits': len(self.metadata),
            'num_items': {
                'min': min(num_items),
                'max': max(num_items),
                'mean': float(np.mean(num_items)),
                'std': float(np.std(num_items))
            },
            'labels': {
                'compatible': compatible,
                'incompatible': incompatible,
                'ratio': compatible / len(labels) if len(labels) > 0 else 0
            }
        }

        return stats


def get_dataloaders(
    data_path: str,
    batch_size: int = 32,
    max_items: int = 5,
    num_workers: int = 0,  # Set to 0 for Windows compatibility
    seed: int = 42,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Create train, validation, and test dataloaders
    
    Args:
        data_path: Path to processed data directory
        batch_size: Batch size for training
        max_items: Maximum items per outfit
        num_workers: Number of worker processes (use 0 for Windows)
        seed: Random seed
        train_ratio: Training split ratio
        val_ratio: Validation split ratio
        
    Returns:
        Tuple of (train_loader, val_loader, test_loader)
    """
    # Create datasets
    train_dataset = OutfitCompatibilityDataset(
        data_path=data_path,
        max_items=max_items,
        split='train',
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        seed=seed
    )
    
    val_dataset = OutfitCompatibilityDataset(
        data_path=data_path,
        max_items=max_items,
        split='val',
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        seed=seed
    )
    
    test_dataset = OutfitCompatibilityDataset(
        data_path=data_path,
        max_items=max_items,
        split='test',
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        seed=seed
    )

    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )

    # Print statistics
    print("\n📊 Dataset Statistics:")
    for loader, dataset in [('Train', train_dataset), ('Val', val_dataset), ('Test', test_dataset)]:
        stats = dataset.get_statistics()
        print(f"\n  {loader}:")
        print(f"    Total: {stats['total_outfits']}")
        print(f"    Compatible: {stats['labels']['compatible']} ({stats['labels']['ratio']:.1%})")
        print(f"    Incompatible: {stats['labels']['incompatible']}")
        print(f"    Items per outfit: {stats['num_items']['mean']:.1f} ± {stats['num_items']['std']:.1f}")

    return train_loader, val_loader, test_loader


if __name__ == "__main__":
    """Test the dataset implementation"""
    print("🧪 Testing OutfitCompatibilityDataset...\n")
    
    # Test with actual data
    data_path = "./data/processed"
    
    try:
        # Create dataloaders
        train_loader, val_loader, test_loader = get_dataloaders(
            data_path=data_path,
            batch_size=4,
            max_items=5,
            num_workers=0,
            seed=42
        )
        
        # Test a batch from train loader
        print("\n🔍 Testing batch from train loader:")
        batch = next(iter(train_loader))
        
        print(f"  Embeddings shape: {batch['embeddings'].shape}")
        print(f"  Mask shape: {batch['mask'].shape}")
        print(f"  Labels shape: {batch['label'].shape}")
        print(f"  Num items: {batch['num_items'].squeeze().tolist()}")
        print(f"  Labels: {batch['label'].squeeze().tolist()}")
        print(f"  Outfit IDs: {batch['outfit_id']}")
        
        print("\n✅ Dataset test passed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
