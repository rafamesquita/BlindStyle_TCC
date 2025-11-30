"""
Script de Teste para Dataset Gerado
=====================================

Valida que o dataset foi gerado corretamente e pode ser carregado.
"""

import numpy as np
import json
from pathlib import Path


def test_dataset():
    """Testa dataset gerado"""
    
    print("🧪 TESTANDO DATASET")
    print("="*70)
    
    # Paths
    npz_path = "data/processed/outfits_dataset.npz"
    json_path = "data/processed/metadata.json"
    stats_path = "data/processed/dataset_statistics.json"
    
    # Verifica se arquivos existem
    print("\n1. Verificando arquivos...")
    for path in [npz_path, json_path, stats_path]:
        if not Path(path).exists():
            print(f"   ❌ Arquivo não encontrado: {path}")
            return False
        else:
            file_size = Path(path).stat().st_size / (1024 * 1024)
            print(f"   ✅ {path} ({file_size:.2f} MB)")
    
    # ────────────────────────────────────────────────────────────
    # 2. Carrega NPZ
    # ────────────────────────────────────────────────────────────
    print("\n2. Carregando NPZ...")
    data = np.load(npz_path)
    
    print(f"   Número de outfits: {len(data.files)}")
    print(f"   Primeiros 5 keys: {data.files[:5]}")
    
    # ────────────────────────────────────────────────────────────
    # 3. Carrega metadata
    # ────────────────────────────────────────────────────────────
    print("\n3. Carregando metadados...")
    with open(json_path, 'r') as f:
        metadata = json.load(f)
    
    print(f"   Número de metadados: {len(metadata)}")
    print(f"   Exemplo do primeiro sample:")
    example = metadata[0]
    print(f"      outfit_id: {example['outfit_id']}")
    print(f"      is_compatible: {example['is_compatible']}")
    print(f"      num_items: {example['num_items']}")
    print(f"      piece_ids: {example['piece_ids'][:2]}..." if len(example['piece_ids']) > 2 else f"      piece_ids: {example['piece_ids']}")
    print(f"      negative_type: {example.get('negative_type', 'N/A')}")
    
    # Valida que piece_ids existem
    if 'piece_ids' not in example:
        print(f"   ❌ Campo 'piece_ids' não encontrado nos metadados!")
        return False
    else:
        print(f"   ✅ Campo 'piece_ids' presente nos metadados")
    
    # ────────────────────────────────────────────────────────────
    # 4. Carrega estatísticas
    # ────────────────────────────────────────────────────────────
    print("\n4. Carregando estatísticas...")
    with open(stats_path, 'r') as f:
        stats = json.load(f)
    
    print(f"   Total samples: {stats['dataset_info']['total_samples']}")
    print(f"   Positivos: {stats['dataset_info']['total_positives']}")
    print(f"   Negativos: {stats['dataset_info']['total_negatives']}")
    print(f"   Seed: {stats['dataset_info']['seed']}")
    
    # ────────────────────────────────────────────────────────────
    # 5. Consistência
    # ────────────────────────────────────────────────────────────
    print("\n5. Verificando consistência...")
    
    if len(data.files) != len(metadata):
        print(f"   ❌ Inconsistência: {len(data.files)} arrays vs {len(metadata)} metadados")
        return False
    else:
        print(f"   ✅ Arrays e metadados consistentes: {len(data.files)} samples")
    
    # Verifica balanceamento
    pos_ratio = stats['dataset_info']['total_positives'] / stats['dataset_info']['total_samples']
    if abs(pos_ratio - 0.5) > 0.01:
        print(f"   ⚠️  Desbalanceamento: {pos_ratio*100:.1f}% positivos")
    else:
        print(f"   ✅ Dataset balanceado: {pos_ratio*100:.1f}% positivos")
    
    # ────────────────────────────────────────────────────────────
    # 6. Testa 10 samples aleatórios
    # ────────────────────────────────────────────────────────────
    print("\n6. Testando samples aleatórios...")
    test_indices = np.random.choice(len(data.files), size=min(10, len(data.files)), replace=False)
    
    all_tests_passed = True
    for i in test_indices:
        key = f'outfit_{i}'
        emb = data[key]
        meta = metadata[i]
        
        # Testes
        tests_passed = True
        errors = []
        
        # Shape
        if emb.ndim != 2:
            errors.append(f"ndim={emb.ndim} (esperado 2)")
            tests_passed = False
        
        if emb.shape[1] != 96:
            errors.append(f"dim={emb.shape[1]} (esperado 96)")
            tests_passed = False
        
        if emb.shape[0] != meta['num_items']:
            errors.append(f"num_items={emb.shape[0]} vs metadata={meta['num_items']}")
            tests_passed = False
        
        # Sem NaN/Inf
        if np.isnan(emb).any():
            errors.append("contém NaN")
            tests_passed = False
        
        if np.isinf(emb).any():
            errors.append("contém Inf")
            tests_passed = False
        
        # Relatório
        if tests_passed:
            print(f"   ✅ Sample {i}: {emb.shape} - {meta['outfit_id'][:30]}...")
        else:
            print(f"   ❌ Sample {i}: {', '.join(errors)}")
            all_tests_passed = False
    
    # ────────────────────────────────────────────────────────────
    # 7. Distribuições
    # ────────────────────────────────────────────────────────────
    print("\n7. Distribuições:")
    
    print("\n   Tamanhos:")
    for size, count in sorted(stats['size_distribution'].items()):
        percent = int(count) / stats['dataset_info']['total_samples'] * 100
        bar = '█' * int(percent / 2)
        print(f"      {size} itens: {count:5d} ({percent:5.2f}%) {bar}")
    
    if 'negative_type_distribution' in stats and stats['negative_type_distribution']:
        print("\n   Tipos de negativos:")
        for neg_type, count in stats['negative_type_distribution'].items():
            total_neg = stats['dataset_info']['total_negatives']
            percent = int(count) / total_neg * 100
            print(f"      {neg_type}: {count:5d} ({percent:5.2f}%)")
    
    # Valida piece_ids nos metadados
    print("\n8. Validando piece_ids nos metadados...")
    samples_with_pieces = sum(1 for m in metadata if m.get('piece_ids'))
    samples_without_pieces = len(metadata) - samples_with_pieces
    
    if samples_without_pieces > 0:
        print(f"   ⚠️  {samples_without_pieces} samples sem piece_ids!")
        all_tests_passed = False
    else:
        print(f"   ✅ Todos os {len(metadata)} samples têm piece_ids")
    
    # Valida consistência num_items vs len(piece_ids)
    inconsistent_count = 0
    for m in metadata[:100]:  # Sample de 100
        if m.get('piece_ids') and len(m['piece_ids']) != m['num_items']:
            inconsistent_count += 1
    
    if inconsistent_count > 0:
        print(f"   ❌ {inconsistent_count} samples com num_items ≠ len(piece_ids)")
        all_tests_passed = False
    else:
        print(f"   ✅ num_items consistente com len(piece_ids)")
    
    print("\n   Estatísticas de embeddings:")
    emb_stats = stats['embedding_stats']
    print(f"      Mean: {emb_stats['mean']:.4f}")
    print(f"      Std:  {emb_stats['std']:.4f}")
    print(f"      Min:  {emb_stats['min']:.4f}")
    print(f"      Max:  {emb_stats['max']:.4f}")
    
    # ────────────────────────────────────────────────────────────
    # RESULTADO FINAL
    # ────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    if all_tests_passed:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("="*70)
        print("\n🎉 Dataset validado e pronto para uso!")
        return True
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("="*70)
        print("\n⚠️  Verifique os erros acima antes de usar o dataset.")
        return False


if __name__ == "__main__":
    success = test_dataset()
    exit(0 if success else 1)
