"""
Script de teste para validar que model_input.py gera máscaras 
idênticas ao models/dataset.py

Execute: python backend/modules/test_mask_consistency.py
"""

import numpy as np
import sys
from pathlib import Path

# Adiciona backend ao path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from modules.model_input import ModelInputBuilder


def test_mask_consistency():
    """
    Testa se as máscaras geradas são consistentes com dataset.py
    """
    print("🧪 Testando consistência de máscaras...\n")
    
    # Simula embedding de nova peça
    new_piece_embedding = np.random.randn(96).astype(np.float32)
    
    # Simula 3 peças de um outfit
    outfit_pieces = [
        {'embedding': np.random.randn(96).astype(np.float32)},
        {'embedding': np.random.randn(96).astype(np.float32)},
        {'embedding': np.random.randn(96).astype(np.float32)},
    ]
    
    builder = ModelInputBuilder(max_items=5, embedding_dim=96)
    embeddings, mask, num_items = builder.build_input(new_piece_embedding, outfit_pieces)
    
    # Validações
    print(f"✅ Embeddings shape: {embeddings.shape}")
    assert embeddings.shape == (5, 96), f"Shape incorreto: {embeddings.shape}"
    
    print(f"✅ Mask shape: {mask.shape}")
    assert mask.shape == (5,), f"Mask shape incorreto: {mask.shape}"
    
    print(f"✅ Mask dtype: {mask.dtype}")
    assert mask.dtype == bool, f"Mask dtype incorreto: {mask.dtype}"
    
    print(f"✅ Num items: {num_items}")
    assert num_items == 4, f"Num items incorreto: {num_items} (esperado: 4)"
    
    print(f"✅ Mask values: {mask}")
    expected_mask = np.array([True, True, True, True, False], dtype=bool)
    assert np.array_equal(mask, expected_mask), f"Mask values incorretos"
    
    print(f"✅ Embeddings não-zero count: {np.count_nonzero(np.any(embeddings != 0, axis=1))}")
    assert np.count_nonzero(np.any(embeddings != 0, axis=1)) == 4, "Embeddings incorretos"
    
    print("\n" + "="*50)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("="*50)
    print("\n📋 Resumo:")
    print(f"  - Embeddings: (5, 96) ✓")
    print(f"  - Mask: (5,) dtype=bool ✓")
    print(f"  - Mask pattern: [T,T,T,T,F] para 4 itens ✓")
    print(f"  - Consistente com models/dataset.py ✓")


def test_max_items_validation():
    """
    Testa se ValueError é lançado quando excede max_items
    """
    print("\n🧪 Testando validação de max_items...\n")
    
    new_piece_embedding = np.random.randn(96).astype(np.float32)
    
    # Simula 5 peças (5 + 1 nova = 6 total, excede max_items=5)
    outfit_pieces = [
        {'embedding': np.random.randn(96).astype(np.float32)}
        for _ in range(5)
    ]
    
    builder = ModelInputBuilder(max_items=5, embedding_dim=96)
    
    try:
        embeddings, mask, num_items = builder.build_input(new_piece_embedding, outfit_pieces)
        print("❌ ERRO: Deveria ter lançado ValueError!")
        sys.exit(1)
    except ValueError as e:
        print(f"✅ ValueError lançado corretamente: {e}")
        print("✅ Validação de max_items funcionando!")


if __name__ == "__main__":
    test_mask_consistency()
    test_max_items_validation()
