"""
Módulo para recuperar outfits usados em treino e teste

Este módulo implementa a lógica para recuperar outfits específicos
baseados na divisão de dados usada no treinamento do modelo.

"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import numpy as np
from typing import List, Dict, Tuple

from modules.config import BASE_DIR


class OutfitRetriever:
    """Classe para recuperar outfits de treino e teste"""

    def __init__(self, data_path: str = None):
        """
        Inicializa o recuperador de outfits

        Args:
            data_path: Caminho para data/processed/ (padrão: BASE_DIR/data/processed)
        """
        if data_path is None:
            data_path = BASE_DIR / "data" / "processed"
        self.data_path = Path(data_path)

        # Carrega metadata
        metadata_path = self.data_path / 'metadata.json'
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata não encontrado: {metadata_path}")

        with open(metadata_path, 'r') as f:
            self.all_metadata = json.load(f)

        print(f"📦 Carregado metadata com {len(self.all_metadata)} outfits")

    def get_split_indices(self, split: str, train_ratio: float = 0.7,
                         val_ratio: float = 0.15, seed: int = 42) -> np.ndarray:
        """
        Retorna os índices para um split específico

        Args:
            split: 'train', 'val', ou 'test'
            train_ratio: Proporção para treino
            val_ratio: Proporção para validação
            seed: Seed para reprodutibilidade

        Returns:
            Array com índices do split
        """
        np.random.seed(seed)
        total = len(self.all_metadata)
        indices = np.random.permutation(total)

        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)

        if split == 'train':
            return indices[:train_end]
        elif split == 'val':
            return indices[train_end:val_end]
        elif split == 'test':
            return indices[val_end:]
        else:
            raise ValueError(f"Split inválido: {split}")

    def get_outfit_ids(self, split: str, num_samples: int = 5) -> List[str]:
        """
        Retorna IDs dos primeiros outfits de um split

        Args:
            split: 'train' ou 'test'
            num_samples: Número de outfits a retornar

        Returns:
            Lista de outfit_ids
        """
        indices = self.get_split_indices(split)
        selected_indices = indices[:num_samples]

        outfit_ids = []
        for idx in selected_indices:
            outfit_id = self.all_metadata[idx]['outfit_id']
            # Remove sufixos como _positive, _negative_medium_1234
            base_id = outfit_id.split('_')[0]
            outfit_ids.append(base_id)

        return outfit_ids

    def load_outfit_details(self, outfit_id: str) -> Dict:
        """
        Carrega detalhes de um outfit do filtered_outfits

        Args:
            outfit_id: ID do outfit (ex: '100002074')

        Returns:
            Dict com detalhes do outfit
        """
        from modules.config import FILTERED_DIR

        outfit_file = FILTERED_DIR / f"{outfit_id}.json"
        if not outfit_file.exists():
            raise FileNotFoundError(f"Arquivo de outfit não encontrado: {outfit_file}")

        with open(outfit_file, 'r') as f:
            return json.load(f)

    def retrieve_sample_outfits(self, num_train: int = 5, num_test: int = 5) -> Dict[str, List[Dict]]:
        """
        Recupera amostras de outfits de treino e teste

        Args:
            num_train: Número de outfits de treino
            num_test: Número de outfits de teste

        Returns:
            Dict com 'train' e 'test', cada um contendo lista de dicts com detalhes dos outfits
        """
        result = {'train': [], 'test': []}

        # Recupera IDs
        train_ids = self.get_outfit_ids('train', num_train)
        test_ids = self.get_outfit_ids('test', num_test)

        print(f"🔍 Recuperando {len(train_ids)} outfits de treino e {len(test_ids)} de teste")

        # Carrega detalhes
        for outfit_id in train_ids:
            try:
                details = self.load_outfit_details(outfit_id)
                result['train'].append({
                    'outfit_id': outfit_id,
                    'details': details
                })
            except FileNotFoundError as e:
                print(f"Aviso: {e}")

        for outfit_id in test_ids:
            try:
                details = self.load_outfit_details(outfit_id)
                result['test'].append({
                    'outfit_id': outfit_id,
                    'details': details
                })
            except FileNotFoundError as e:
                print(f"Aviso: {e}")

        print(f"✅ Recuperados {len(result['train'])} outfits de treino e {len(result['test'])} de teste")

        return result


def main():
    """Função principal para teste"""
    retriever = OutfitRetriever()
    outfits = retriever.retrieve_sample_outfits()

    print("\n🎯 OUTFITS DE TREINO:")
    for outfit in outfits['train']:
        print(f"  - ID: {outfit['outfit_id']}")
        print(f"    Itens: {len(outfit['details'])}")

    print("\n🎯 OUTFITS DE TESTE:")
    for outfit in outfits['test']:
        print(f"  - ID: {outfit['outfit_id']}")
        print(f"    Itens: {len(outfit['details'])}")


if __name__ == "__main__":
    main()