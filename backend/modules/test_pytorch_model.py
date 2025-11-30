"""
Script de teste para validar o módulo pytorch_model.py

Execute: python backend/modules/test_pytorch_model.py
"""

import numpy as np
import sys
from pathlib import Path

# Adiciona backend ao path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from modules.pytorch_model import ModelPredictor, get_model_predictor


def test_model_loading():
    """
    Testa se o modelo carrega corretamente
    """
    print("🧪 Testando carregamento do modelo...\n")
    
    try:
        # Tenta carregar o modelo (path relativo)
        predictor = get_model_predictor(checkpoint_path="../checkpoints/best_model.pth")
        
        print(f"✅ Modelo carregado com sucesso!")
        print(f"  Parâmetros totais: {predictor.model.get_num_parameters():,}")
        print(f"  Parâmetros treináveis: {predictor.model.get_trainable_parameters():,}")
        
        return predictor
        
    except FileNotFoundError as e:
        print(f"❌ ERRO: {e}")
        print(f"\n⚠️  Certifique-se de que o checkpoint está em: backend/checkpoints/best_model.pth")
        sys.exit(1)


def test_single_prediction(predictor):
    """
    Testa predição única
    """
    print("\n🧪 Testando predição única...\n")
    
    # Simula embedding de nova peça e 3 peças de outfit
    embeddings = np.random.randn(5, 96).astype(np.float32)
    mask = np.array([True, True, True, True, False], dtype=bool)
    
    score = predictor.predict_single(embeddings, mask)
    
    print(f"✅ Predição executada com sucesso!")
    print(f"  Score: {score:.4f}")
    print(f"  Range esperado: [0.0, 1.0]")
    
    assert 0.0 <= score <= 1.0, f"Score fora do range: {score}"


def test_batch_prediction(predictor):
    """
    Testa predição em batch
    """
    print("\n🧪 Testando predição em batch...\n")
    
    # Simula 3 outfits
    batch_inputs = {
        "outfit_1": (
            np.random.randn(5, 96).astype(np.float32),
            np.array([True, True, True, False, False], dtype=bool),
            3
        ),
        "outfit_2": (
            np.random.randn(5, 96).astype(np.float32),
            np.array([True, True, True, True, False], dtype=bool),
            4
        ),
        "outfit_3": (
            np.random.randn(5, 96).astype(np.float32),
            np.array([True, True, True, True, True], dtype=bool),
            5
        ),
    }
    
    scores = predictor.predict_batch(batch_inputs)
    
    print(f"✅ Predição em batch executada com sucesso!")
    print(f"  Outfits avaliados: {len(scores)}")
    
    for outfit_id, score in scores.items():
        print(f"    {outfit_id}: {score:.4f}")
        assert 0.0 <= score <= 1.0, f"Score fora do range: {score}"


def test_top_k_filtering(predictor):
    """
    Testa filtragem de top-k outfits
    """
    print("\n🧪 Testando filtragem top-k...\n")
    
    # Simula scores variados
    scores = {
        "outfit_low": 0.45,
        "outfit_medium": 0.75,
        "outfit_high_1": 0.92,
        "outfit_high_2": 0.87,
        "outfit_high_3": 0.95,
        "outfit_high_4": 0.82,
    }
    
    top_3 = predictor.get_top_k_outfits(scores, k=3, min_threshold=0.8)
    
    print(f"✅ Filtragem executada com sucesso!")
    print(f"  Top 3 acima de 0.8:")
    
    for outfit_id, score in top_3.items():
        print(f"    {outfit_id}: {score:.4f}")
    
    # Validações
    assert len(top_3) <= 3, "Deveria retornar no máximo 3"
    assert all(score >= 0.8 for score in top_3.values()), "Todos devem estar acima de 0.8"
    
    # Verifica ordenação decrescente
    scores_list = list(top_3.values())
    assert scores_list == sorted(scores_list, reverse=True), "Deve estar ordenado"
    
    print(f"\n  Validações:")
    print(f"    ✓ Máximo 3 resultados")
    print(f"    ✓ Todos acima do limiar 0.8")
    print(f"    ✓ Ordenado por score decrescente")


def test_singleton_cache():
    """
    Testa se o singleton está funcionando
    """
    print("\n🧪 Testando cache singleton...\n")
    
    predictor1 = get_model_predictor()
    predictor2 = get_model_predictor()
    
    assert predictor1 is predictor2, "Deveria retornar a mesma instância"
    
    print(f"✅ Singleton funcionando corretamente!")
    print(f"  Mesma instância retornada em chamadas subsequentes")


if __name__ == "__main__":
    print("="*60)
    print("TESTES DO MÓDULO PYTORCH_MODEL")
    print("="*60)
    
    predictor = test_model_loading()
    test_single_prediction(predictor)
    test_batch_prediction(predictor)
    test_top_k_filtering(predictor)
    test_singleton_cache()
    
    print("\n" + "="*60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("="*60)
