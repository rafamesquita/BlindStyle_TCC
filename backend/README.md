# 🎨 Blind Style Model - MCN Outfit Compatibility

**Multi-Correlation Network for Fashion Outfit Compatibility Prediction**

---

## 🚀 Quick Start

### Phase 1: Data Generation ✅ (Complete)
Dataset of 7,936 outfit samples (balanced: 50% compatible, 50% incompatible)

### Phase 2: Model Training ✅ (Implementation Complete)

#### Test Training (Quick Validation - 5 epochs)
```bash
python scripts/train.py
```

#### Full Training (Production - 50 epochs)
```bash
# Option 1: Edit config/config.yaml line 48 → num_epochs: 50
python scripts/train.py

# Option 2: Override from command line
python scripts/train.py --epochs 50
```

#### Monitor Training
```bash
tensorboard --logdir=./logs
```

#### Evaluate Model
```bash
python scripts/evaluate.py
```

---

## 🔧 Where to Change Epochs

**File**: `config/config.yaml`  
**Line**: 48

```yaml
num_epochs: 5  # 🔧 CHANGE THIS FOR FULL TRAINING (recommended: 50-100)
```

---

## 📚 Documentation

- **Quick Reference**: [`TRAINING_GUIDE.md`](TRAINING_GUIDE.md) - One-page guide
- **Detailed Guide**: [`memory-bank/phase-2-implementation.md`](memory-bank/phase-2-implementation.md)
- **Phase 1 Report**: [`memory-bank/phase-1-completion-report.md`](memory-bank/phase-1-completion-report.md)
- **Phase 2 Summary**: [`memory-bank/phase-2-execution-summary.md`](memory-bank/phase-2-execution-summary.md)

---

## 📁 Project Structure

```
blindstylemodel/
├── config/
│   └── config.yaml              # 🔧 Configuration (epochs on line 48)
├── models/
│   ├── dataset.py               # PyTorch Dataset
│   ├── compat_model.py          # MCN Architecture
│   └── trainer.py               # Training Loop
├── scripts/
│   ├── train.py                 # Training script
│   └── evaluate.py              # Evaluation script
├── data/
│   └── processed/
│       ├── outfits_dataset.npz  # 7,936 samples
│       └── metadata.json        # Labels & metadata
├── checkpoints/                 # Saved models (created during training)
├── logs/                        # TensorBoard logs (created during training)
└── results/                     # Evaluation results (created after eval)
```

---

## 🏗️ Model Architecture

```
Input: Outfit embeddings (2-5 items × 96-D)
    ↓
Feature Projection (96 → 1000-D)
    ↓
Pairwise Comparisons (15 pairs with learnable masks)
    ↓
MLP Predictor
    ↓
Output: Compatibility score [0, 1]
```

**Parameters**: ~1.2M trainable  
**Hardware**: Auto-detects GPU, falls back to CPU

---

## ⏱️ Training Times

| Epochs | CPU | GPU | Purpose |
|--------|-----|-----|---------|
| 5 (test) | ~10 min | ~3 min | Validation |
| 50 (standard) | ~2 hrs | ~25 min | Production |
| 100 (extensive) | ~4 hrs | ~50 min | Best results |

---

## 📊 Expected Results

After 50 epochs of training:
- **AUC**: > 0.85
- **Accuracy**: > 0.80
- **F1-Score**: > 0.80

---

## 🛠️ Initial Setup

1. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows PowerShell
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install Pillow
pip install python-dotenv
pip install google-generativeai
pip install numpy
pip install chromadb
pip install torch torchvision
pip install scikit-learn
pip install matplotlib seaborn
pip install tensorboard
pip install pyyaml tqdm
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Future Updates

If you add new packages to the project, update requirements.txt using:
```bash
pip freeze > requirements.txt
```

## Note
Make sure you have Python 3.13+ installed on your system before proceeding with the setup.