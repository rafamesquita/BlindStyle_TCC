"""
Pipeline de Geração de Dataset para Treinamento MCN
====================================================

Este script extrai outfits do ChromaDB e gera um dataset balanceado
com samples positivos e negativos para treinar o modelo MCN.

Autor: Blind Style Model Team
Data: 2025-10-15
"""

import chromadb
import numpy as np
import json
from pathlib import Path
from collections import defaultdict, Counter
from tqdm import tqdm
from datetime import datetime
from typing import Dict, List, Tuple


class ChromaDBExtractor:
    """Extrai e organiza dados do ChromaDB"""
    
    def __init__(self, chromadb_path: str):
        """
        Inicializa extrator do ChromaDB
        
        Args:
            chromadb_path: Caminho para o diretório do ChromaDB
        """
        self.chromadb_path = chromadb_path
        self.client = chromadb.PersistentClient(path=chromadb_path)
        self.collection = self.client.get_collection("pieces")
        self.pieces_by_outfit = {}
        
    def extract_pieces(self) -> Dict:
        """
        Extrai todas as peças do ChromaDB organizadas por outfit
        
        Returns:
            dict: {
                '1013': [
                    {
                        'piece_id': '1013/1.jpg',
                        'piece_name': '1.jpg',
                        'embedding': np.array(96,),
                        'outfit_id': '1013'
                    },
                    ...
                ],
                ...
            }
        """
        print("🔍 [EXTRAÇÃO] Consultando ChromaDB collection 'pieces'...")
        
        # 1. Busca TODOS os documentos
        results = self.collection.get(
            include=['embeddings']
        )
        
        total_pieces = len(results['ids'])
        print(f"   Encontradas {total_pieces} peças no total")
        
        # 2. Agrupa por outfit_id
        pieces_by_outfit = defaultdict(list)
        invalid_count = 0
        
        for doc_id, embedding in tqdm(zip(results['ids'], results['embeddings']), 
                                       total=total_pieces,
                                       desc="Agrupando por outfit"):
            # Parse: "1013/1.jpg" → outfit_id="1013", piece_name="1.jpg"
            parts = doc_id.split('/')
            
            if len(parts) != 2:
                print(f"   ⚠️  ID inválido ignorado: {doc_id}")
                invalid_count += 1
                continue
                
            outfit_id, piece_name = parts
            
            pieces_by_outfit[outfit_id].append({
                'piece_id': doc_id,
                'piece_name': piece_name,
                'embedding': np.array(embedding, dtype=np.float32),
                'outfit_id': outfit_id
            })
        
        # 3. Validações
        num_outfits = len(pieces_by_outfit)
        print(f"\n✅ [EXTRAÇÃO COMPLETA]")
        print(f"   Total de outfits: {num_outfits}")
        print(f"   Peças válidas: {total_pieces - invalid_count}")
        print(f"   Peças inválidas: {invalid_count}")
        
        # Estatísticas
        pieces_per_outfit = [len(pieces) for pieces in pieces_by_outfit.values()]
        print(f"\n📊 [ESTATÍSTICAS]")
        print(f"   Peças por outfit: min={min(pieces_per_outfit)}, "
              f"max={max(pieces_per_outfit)}, "
              f"média={np.mean(pieces_per_outfit):.2f}")
        
        # Histograma de distribuição
        distribution = Counter(pieces_per_outfit)
        print(f"\n   Distribuição:")
        for num_pieces in sorted(distribution.keys()):
            count = distribution[num_pieces]
            bar = '█' * (count // 50)  # Escala visual
            print(f"      {num_pieces} peças: {count:4d} outfits {bar}")
        
        self.pieces_by_outfit = dict(pieces_by_outfit)
        return self.pieces_by_outfit
    
    def validate_extraction(self):
        """Valida extração do ChromaDB"""
        
        print("\n🔍 [VALIDAÇÃO] Verificando qualidade dos dados...")
        
        errors = []
        warnings = []
        
        # 1. Número mínimo de outfits
        num_outfits = len(self.pieces_by_outfit)
        if num_outfits < 3000:
            errors.append(f"Muito poucos outfits: {num_outfits} < 3000")
        
        # 2. Verificar embeddings
        for outfit_id, pieces in self.pieces_by_outfit.items():
            # Mínimo 2 peças
            if len(pieces) < 2:
                errors.append(f"Outfit {outfit_id} tem apenas {len(pieces)} peça(s)")
            
            # Máximo 5 peças
            if len(pieces) > 5:
                warnings.append(f"Outfit {outfit_id} tem {len(pieces)} peças (>5)")
            
            # Embeddings válidos
            for piece in pieces:
                emb = piece['embedding']
                
                # Shape correto
                if emb.shape != (96,):
                    errors.append(f"Embedding com shape errado: {emb.shape} (esperado: (96,))")
                
                # Sem NaN/Inf
                if np.isnan(emb).any() or np.isinf(emb).any():
                    errors.append(f"Embedding com NaN/Inf: {piece['piece_id']}")
                
                # Não é zero
                if np.allclose(emb, 0):
                    warnings.append(f"Embedding zero: {piece['piece_id']}")
        
        # Relatório
        if errors:
            print(f"\n❌ [ERROS CRÍTICOS] {len(errors)} problema(s) encontrado(s):")
            for err in errors[:10]:  # Mostra primeiros 10
                print(f"   - {err}")
            raise ValueError("Extração inválida! Verifique os erros acima.")
        
        if warnings:
            print(f"\n⚠️  [AVISOS] {len(warnings)} aviso(s):")
            for warn in warnings[:10]:
                print(f"   - {warn}")
        
        print(f"\n✅ [VALIDAÇÃO COMPLETA] Dados OK para processamento!")


class DatasetGenerator:
    """Gera dataset de treino com positivos e negativos"""
    
    def __init__(self, pieces_by_outfit: Dict, seed: int = 42):
        """
        Inicializa gerador de dataset
        
        Args:
            pieces_by_outfit: Dicionário com peças organizadas por outfit
            seed: Seed para reprodutibilidade
        """
        self.pieces_by_outfit = pieces_by_outfit
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
    def create_positive_samples(self) -> List[Dict]:
        """
        Gera samples positivos (originais apenas, SEM shuffling)
        
        Para cada outfit:
          - Adiciona original como está (label=1)
          - SEM shuffling de ordem
          - SEM data augmentation
        
        Returns:
            list[dict]: Lista de samples positivos
        """
        print("\n✅ [POSITIVOS] Gerando samples positivos (apenas originais)...")
        
        positive_samples = []
        
        for outfit_id, pieces in tqdm(self.pieces_by_outfit.items(), 
                                       desc="Criando positivos"):
            # Embeddings das peças (num_items, 96)
            embeddings = np.array([p['embedding'] for p in pieces], dtype=np.float32)
            num_items = len(pieces)
            piece_ids = [p['piece_id'] for p in pieces]
            
            # Adiciona apenas ORIGINAL (sem shuffling)
            positive_samples.append({
                'outfit_id': f"{outfit_id}_positive",
                'embeddings': embeddings.copy(),
                'num_items': num_items,
                'piece_ids': piece_ids.copy(),
                'is_compatible': True,
                'source_outfit': outfit_id
            })
        
        # Estatísticas
        num_positives = len(positive_samples)
        
        print(f"\n✅ [POSITIVOS COMPLETOS]")
        print(f"   Originais: {num_positives}")
        print(f"   TOTAL: {num_positives}")
        print(f"   (SEM shuffling - dataset menor mas mais limpo)")
        
        return positive_samples
    
    def create_negative_samples(self, num_positives: int) -> List[Dict]:
        """
        Gera samples negativos estratificados
        
        - 80% médios (trocar ~50% das peças)
        - 20% fáceis (trocar 1 peça muito diferente)
        
        Args:
            num_positives: Número de positivos (para balancear 1:1)
        
        Returns:
            list[dict]: Lista de samples negativos
        """
        print(f"\n❌ [NEGATIVOS] Gerando {num_positives} samples negativos...")
        
        # Distribuição: 80% medium, 20% easy
        num_medium = int(num_positives * 0.80)
        num_easy = num_positives - num_medium
        
        print(f"   Médios (80%): {num_medium}")
        print(f"   Fáceis (20%): {num_easy}")
        
        negative_samples = []
        
        # Lista de outfit_ids
        outfit_ids_list = list(self.pieces_by_outfit.keys())
        
        # ────────────────────────────────────────────────────────────
        # A) NEGATIVOS MÉDIOS (trocar ~50% das peças)
        # ────────────────────────────────────────────────────────────
        print("\n   Gerando negativos MÉDIOS...")
        for neg_idx in tqdm(range(num_medium), desc="Medium negatives"):
            # Escolhe outfit base aleatório
            base_outfit_id = self.rng.choice(outfit_ids_list)
            base_pieces = self.pieces_by_outfit[base_outfit_id]
            num_items = len(base_pieces)
            
            # Quantas peças trocar? ~50% (mínimo 1, máximo num_items-1)
            num_to_replace = max(1, min(num_items - 1, num_items // 2))
            
            # Escolhe índices para substituir
            replace_indices = self.rng.choice(num_items, 
                                             size=num_to_replace, 
                                             replace=False)
            
            # Cria nova lista de embeddings
            new_embeddings = [p['embedding'].copy() for p in base_pieces]
            replaced_pieces = []
            
            for idx in replace_indices:
                # Escolhe outro outfit aleatório (diferente do base)
                other_outfit_id = self.rng.choice(
                    [oid for oid in outfit_ids_list if oid != base_outfit_id]
                )
                other_pieces = self.pieces_by_outfit[other_outfit_id]
                
                # Escolhe peça aleatória desse outfit
                random_piece = self.rng.choice(other_pieces)
                
                # Substitui
                new_embeddings[idx] = random_piece['embedding'].copy()
                replaced_pieces.append({
                    'index': int(idx),
                    'original': base_pieces[idx]['piece_id'],
                    'replaced_with': random_piece['piece_id']
                })
            
            # Cria lista de piece_ids do outfit negativo
            negative_piece_ids = [p['piece_id'] for p in base_pieces]
            for replace_info in replaced_pieces:
                negative_piece_ids[replace_info['index']] = replace_info['replaced_with']
            
            negative_samples.append({
                'outfit_id': f"{base_outfit_id}_negative_medium_{neg_idx}",
                'embeddings': np.array(new_embeddings, dtype=np.float32),
                'num_items': num_items,
                'piece_ids': negative_piece_ids,
                'is_compatible': False,
                'negative_type': 'medium',
                'num_replaced': num_to_replace,
                'source_outfit': base_outfit_id,
                'replaced_pieces': replaced_pieces
            })
        
        # ────────────────────────────────────────────────────────────
        # B) NEGATIVOS FÁCEIS (trocar 1 peça, outfit muito diferente)
        # ────────────────────────────────────────────────────────────
        print("\n   Gerando negativos FÁCEIS...")
        for neg_idx in tqdm(range(num_easy), desc="Easy negatives"):
            # Escolhe outfit base
            base_outfit_id = self.rng.choice(outfit_ids_list)
            base_pieces = self.pieces_by_outfit[base_outfit_id]
            num_items = len(base_pieces)
            
            # Escolhe 1 índice para substituir
            replace_idx = self.rng.choice(num_items)
            
            # Busca outfit "muito diferente"
            # (simplificação: escolhe aleatório com tamanho diferente se possível)
            candidates = [
                oid for oid in outfit_ids_list 
                if oid != base_outfit_id and 
                abs(len(self.pieces_by_outfit[oid]) - num_items) >= 1
            ]
            
            if not candidates:
                # Fallback: qualquer outro outfit
                candidates = [oid for oid in outfit_ids_list if oid != base_outfit_id]
            
            other_outfit_id = self.rng.choice(candidates)
            other_pieces = self.pieces_by_outfit[other_outfit_id]
            random_piece = self.rng.choice(other_pieces)
            
            # Cria nova lista
            new_embeddings = [p['embedding'].copy() for p in base_pieces]
            new_embeddings[replace_idx] = random_piece['embedding'].copy()
            
            # Cria lista de piece_ids do outfit negativo
            negative_piece_ids = [p['piece_id'] for p in base_pieces]
            negative_piece_ids[replace_idx] = random_piece['piece_id']
            
            replaced_pieces = [{
                'index': int(replace_idx),
                'original': base_pieces[replace_idx]['piece_id'],
                'replaced_with': random_piece['piece_id']
            }]
            
            negative_samples.append({
                'outfit_id': f"{base_outfit_id}_negative_easy_{neg_idx}",
                'embeddings': np.array(new_embeddings, dtype=np.float32),
                'num_items': num_items,
                'piece_ids': negative_piece_ids,
                'is_compatible': False,
                'negative_type': 'easy',
                'num_replaced': 1,
                'source_outfit': base_outfit_id,
                'replaced_pieces': replaced_pieces
            })
        
        print(f"\n❌ [NEGATIVOS COMPLETOS]")
        print(f"   Médios: {num_medium}")
        print(f"   Fáceis: {num_easy}")
        print(f"   TOTAL: {len(negative_samples)}")
        
        return negative_samples
    
    def balance_and_shuffle(self, positives: List[Dict], negatives: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Balanceia e embaralha dataset final
        
        Args:
            positives: Lista de samples positivos
            negatives: Lista de samples negativos
        
        Returns:
            tuple: (samples_combined, metadata_combined)
        """
        print("\n🔀 [BALANCEAMENTO] Combinando e embaralhando dataset...")
        
        # 1. Verificar balanceamento
        num_pos = len(positives)
        num_neg = len(negatives)
        
        print(f"   Positivos: {num_pos}")
        print(f"   Negativos: {num_neg}")
        
        if abs(num_pos - num_neg) > 10:
            print(f"   ⚠️  AVISO: Desbalanceamento detectado!")
            print(f"      Diferença: {abs(num_pos - num_neg)} samples")
        
        # 2. Combina listas
        all_samples = positives + negatives
        
        print(f"\n   Dataset total: {len(all_samples)} samples")
        print(f"   Ratio pos:neg = {num_pos}:{num_neg} ({num_pos/len(all_samples)*100:.1f}% positivos)")
        
        # 3. Embaralha com seed fixa
        print(f"\n   Embaralhando com seed={self.seed}...")
        indices = np.arange(len(all_samples))
        self.rng.shuffle(indices)
        
        shuffled_samples = [all_samples[i] for i in indices]
        
        # 4. Cria metadados separados
        metadata = []
        for idx, sample in enumerate(shuffled_samples):
            metadata.append({
                'index': idx,
                'outfit_id': sample['outfit_id'],
                'is_compatible': sample['is_compatible'],
                'num_items': sample['num_items'],
                'piece_ids': sample.get('piece_ids', []),
                'negative_type': sample.get('negative_type', None),
                'num_replaced': sample.get('num_replaced', None),
                'replaced_pieces': sample.get('replaced_pieces', []),
                'source_outfit': sample.get('source_outfit', None)
            })
        
        print(f"\n✅ [BALANCEAMENTO COMPLETO]")
        print(f"   Dataset embaralhado: {len(shuffled_samples)} samples")
        print(f"   Metadados criados: {len(metadata)} entradas")
        
        return shuffled_samples, metadata
    
    def validate_dataset(self, samples: List[Dict], metadata: List[Dict]):
        """
        Valida dataset final antes de persistir
        
        Verificações:
        1. Número de samples consistente
        2. Embeddings válidos (shape, dtype, valores)
        3. Labels balanceados
        4. Sem duplicatas
        5. Distribuição de tamanhos
        """
        print("\n🔍 [VALIDAÇÃO FINAL] Verificando dataset...")
        
        errors = []
        warnings = []
        
        # ────────────────────────────────────────────────────────────
        # 1. Consistência samples vs metadata
        # ────────────────────────────────────────────────────────────
        if len(samples) != len(metadata):
            errors.append(f"Inconsistência: {len(samples)} samples vs {len(metadata)} metadados")
        
        # ────────────────────────────────────────────────────────────
        # 2. Validar cada sample
        # ────────────────────────────────────────────────────────────
        num_pos = 0
        num_neg = 0
        size_distribution = defaultdict(int)
        
        for i, sample in enumerate(tqdm(samples, desc="Validando samples")):
            # Embeddings
            emb = sample['embeddings']
            
            # Shape (num_items, 96)
            if emb.ndim != 2 or emb.shape[1] != 96:
                errors.append(f"Sample {i}: shape inválida {emb.shape}")
            
            # Dtype float32
            if emb.dtype != np.float32:
                warnings.append(f"Sample {i}: dtype {emb.dtype} (esperado float32)")
            
            # Sem NaN/Inf
            if np.isnan(emb).any() or np.isinf(emb).any():
                errors.append(f"Sample {i}: contém NaN/Inf")
            
            # num_items consistente
            if emb.shape[0] != sample['num_items']:
                errors.append(f"Sample {i}: shape[0]={emb.shape[0]} != num_items={sample['num_items']}")
            
            # Contadores
            if sample['is_compatible']:
                num_pos += 1
            else:
                num_neg += 1
            
            size_distribution[sample['num_items']] += 1
        
        # ────────────────────────────────────────────────────────────
        # 3. Balanceamento de labels
        # ────────────────────────────────────────────────────────────
        total = len(samples)
        pos_ratio = num_pos / total
        
        print(f"\n📊 [DISTRIBUIÇÃO DE LABELS]")
        print(f"   Positivos: {num_pos} ({pos_ratio*100:.2f}%)")
        print(f"   Negativos: {num_neg} ({(1-pos_ratio)*100:.2f}%)")
        
        if abs(pos_ratio - 0.5) > 0.01:  # Tolerância 1%
            warnings.append(f"Desbalanceamento: {pos_ratio*100:.1f}% positivos (esperado ~50%)")
        
        # ────────────────────────────────────────────────────────────
        # 4. Distribuição de tamanhos
        # ────────────────────────────────────────────────────────────
        print(f"\n📊 [DISTRIBUIÇÃO DE TAMANHOS]")
        for size in sorted(size_distribution.keys()):
            count = size_distribution[size]
            percent = count / total * 100
            bar = '█' * int(percent / 2)
            print(f"   {size} itens: {count:5d} ({percent:5.2f}%) {bar}")
        
        # ────────────────────────────────────────────────────────────
        # 5. Verificar duplicatas (sample de IDs)
        # ────────────────────────────────────────────────────────────
        outfit_ids = [s['outfit_id'] for s in samples]
        unique_ids = set(outfit_ids)
        
        if len(outfit_ids) != len(unique_ids):
            num_duplicates = len(outfit_ids) - len(unique_ids)
            errors.append(f"{num_duplicates} IDs duplicados detectados!")
        
        # ────────────────────────────────────────────────────────────
        # RELATÓRIO FINAL
        # ────────────────────────────────────────────────────────────
        if errors:
            print(f"\n❌ [ERROS CRÍTICOS] {len(errors)} problema(s):")
            for err in errors:
                print(f"   - {err}")
            raise ValueError("Dataset inválido! Corrija os erros.")
        
        if warnings:
            print(f"\n⚠️  [AVISOS] {len(warnings)} aviso(s):")
            for warn in warnings:
                print(f"   - {warn}")
        
        print(f"\n✅ [VALIDAÇÃO COMPLETA] Dataset OK!")


class DatasetPersister:
    """Persiste dataset em formato otimizado"""
    
    def save_to_npz(self, samples: List[Dict], output_path: str):
        """
        Salva embeddings em formato NPZ
        
        Estrutura:
            outfit_0: np.array(num_items, 96) float32
            outfit_1: np.array(num_items, 96) float32
            ...
            outfit_N: np.array(num_items, 96) float32
        
        Não padded! Padding será feito durante loading no Dataset
        """
        print(f"\n💾 [SALVANDO NPZ] {output_path}")
        
        # Cria dicionário para npz
        arrays_dict = {}
        
        for i, sample in enumerate(tqdm(samples, desc="Preparando arrays")):
            arrays_dict[f'outfit_{i}'] = sample['embeddings']
        
        # Salva
        np.savez_compressed(output_path, **arrays_dict)
        
        # Verifica tamanho do arquivo
        file_size_mb = Path(output_path).stat().st_size / (1024 * 1024)
        print(f"   Arquivo salvo: {file_size_mb:.2f} MB")
        
        print(f"✅ NPZ salvo com sucesso!")
    
    def save_metadata(self, metadata: List[Dict], output_path: str):
        """
        Salva metadados em JSON
        
        Estrutura:
            [
                {
                    "index": 0,
                    "outfit_id": "1013_positive",
                    "is_compatible": true,
                    "num_items": 3,
                    "augmentation": "original",
                    "negative_type": null,
                    ...
                },
                ...
            ]
        """
        print(f"\n💾 [SALVANDO JSON] {output_path}")
        
        # Serializa
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Verifica tamanho
        file_size_mb = Path(output_path).stat().st_size / (1024 * 1024)
        print(f"   Arquivo salvo: {file_size_mb:.2f} MB")
        
        print(f"✅ Metadados salvos com sucesso!")
    
    def compute_statistics(self, samples: List[Dict], metadata: List[Dict], seed: int) -> Dict:
        """
        Calcula estatísticas abrangentes do dataset
        
        Returns:
            dict com estatísticas completas
        """
        print("\n📊 [ESTATÍSTICAS] Computando...")
        
        stats = {
            'dataset_info': {
                'total_samples': len(samples),
                'total_positives': sum(1 for m in metadata if m['is_compatible']),
                'total_negatives': sum(1 for m in metadata if not m['is_compatible']),
                'creation_date': datetime.now().isoformat(),
                'seed': seed
            },
            'size_distribution': {},
            'augmentation_distribution': {},
            'negative_type_distribution': {},
            'embedding_stats': {}
        }
        
        # Distribuição de tamanhos
        sizes = [m['num_items'] for m in metadata]
        stats['size_distribution'] = dict(Counter(sizes))
        
        # Contagem de positivos e negativos
        num_positives = sum(1 for m in metadata if m['is_compatible'])
        num_negatives = sum(1 for m in metadata if not m['is_compatible'])
        stats['dataset_info']['positives'] = num_positives
        stats['dataset_info']['negatives'] = num_negatives
        
        # Distribuição de tipos de negativos
        neg_types = [m['negative_type'] for m in metadata if m['negative_type']]
        stats['negative_type_distribution'] = dict(Counter(neg_types))
        
        # Estatísticas de embeddings (sample de 100 para performance)
        sample_size = min(100, len(samples))
        all_embeddings = np.concatenate([s['embeddings'] for s in samples[:sample_size]], axis=0)
        stats['embedding_stats'] = {
            'mean': float(np.mean(all_embeddings)),
            'std': float(np.std(all_embeddings)),
            'min': float(np.min(all_embeddings)),
            'max': float(np.max(all_embeddings)),
            'sample_size': sample_size
        }
        
        return stats


def main():
    """Pipeline principal de geração de dataset"""
    
    print("="*70)
    print("🚀 PIPELINE DE GERAÇÃO DE DATASET MCN")
    print("="*70)
    
    # ────────────────────────────────────────────────────────────
    # CONFIGURAÇÕES
    # ────────────────────────────────────────────────────────────
    CHROMADB_PATH = "chroma_db"
    OUTPUT_DIR = "data/processed"
    SEED = 42
    
    # Cria diretórios
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # ────────────────────────────────────────────────────────────
    # FASE 1: EXTRAÇÃO
    # ────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("FASE 1: EXTRAÇÃO DO CHROMADB")
    print("="*70)
    
    extractor = ChromaDBExtractor(CHROMADB_PATH)
    pieces_by_outfit = extractor.extract_pieces()
    extractor.validate_extraction()
    
    # ────────────────────────────────────────────────────────────
    # FASE 2: GERAÇÃO DE SAMPLES
    # ────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("FASE 2: GERAÇÃO DE SAMPLES")
    print("="*70)
    
    generator = DatasetGenerator(pieces_by_outfit, seed=SEED)
    
    # Positivos
    positives = generator.create_positive_samples()
    
    # Negativos
    negatives = generator.create_negative_samples(num_positives=len(positives))
    
    # Balanceia e embaralha
    samples, metadata = generator.balance_and_shuffle(positives, negatives)
    
    # ────────────────────────────────────────────────────────────
    # FASE 3: VALIDAÇÃO
    # ────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("FASE 3: VALIDAÇÃO")
    print("="*70)
    
    generator.validate_dataset(samples, metadata)
    
    # ────────────────────────────────────────────────────────────
    # FASE 4: PERSISTÊNCIA
    # ────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("FASE 4: PERSISTÊNCIA")
    print("="*70)
    
    persister = DatasetPersister()
    
    # Salva NPZ
    npz_path = Path(OUTPUT_DIR) / "outfits_dataset.npz"
    persister.save_to_npz(samples, str(npz_path))
    
    # Salva metadados
    json_path = Path(OUTPUT_DIR) / "metadata.json"
    persister.save_metadata(metadata, str(json_path))
    
    # Salva estatísticas
    stats = persister.compute_statistics(samples, metadata, SEED)
    stats_path = Path(OUTPUT_DIR) / "dataset_statistics.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # ────────────────────────────────────────────────────────────
    # RELATÓRIO FINAL
    # ────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETO!")
    print("="*70)
    
    print(f"\n📁 Arquivos gerados:")
    print(f"   - {npz_path}")
    print(f"   - {json_path}")
    print(f"   - {stats_path}")
    
    print(f"\n📊 Resumo do dataset:")
    print(f"   Total de samples: {stats['dataset_info']['total_samples']}")
    print(f"   Positivos: {stats['dataset_info']['total_positives']}")
    print(f"   Negativos: {stats['dataset_info']['total_negatives']}")
    print(f"   Seed usado: {stats['dataset_info']['seed']}")
    
    print(f"\n🎉 Dataset pronto para treinamento!")
    print("="*70)


if __name__ == "__main__":
    main()
