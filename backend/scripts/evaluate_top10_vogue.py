"""
Script para avaliar outfits do arquivo top10outfit2025voguebr.json

Este script:
1. Carrega os outfits do JSON
2. Gera embeddings para cada peça usando o sistema de hash determinístico
3. Avalia cada outfit completo usando o modelo MCN treinado
4. Gera gráficos de distribuição dos scores
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.embeddings import EmbeddingGenerator
from modules.pytorch_model import ModelPredictor
from modules.model_input import ModelInputBuilder


class VogueOutfitEvaluator:
    """Avaliador de outfits da Vogue usando o modelo MCN"""
    
    @staticmethod
    def get_threshold_color(score: float) -> str:
        """
        Retorna cor baseada em thresholds do modelo:
        - Vermelho: score < 0.5 (muito baixa qualidade)
        - Cinza: 0.5 <= score < 0.8 (baixa qualidade)
        - Amarelo: 0.8 <= score < 0.96 (qualidade média)
        - Verde: score >= 0.96 (alta qualidade)
        
        Args:
            score: Score de compatibilidade
            
        Returns:
            String com código de cor hexadecimal
        """
        if score < 0.5:
            return '#FF4444'  # Vermelho
        elif score < 0.8:
            return '#9E9E9E'  # Cinza
        elif score < 0.96:
            return '#FFBB33'  # Amarelo
        else:
            return '#00C851'  # Verde
    
    def __init__(self, checkpoint_path: str = "checkpoints/best_model.pth"):
        """
        Inicializa o avaliador
        
        Args:
            checkpoint_path: Caminho para o checkpoint do modelo
        """
        self.embedding_generator = EmbeddingGenerator()
        self.model_predictor = ModelPredictor(
            checkpoint_path=f"../{checkpoint_path}",
            device='cpu'  # Usa CPU por padrão
        )
        self.max_items = 5
        self.embedding_dim = 96
        
    def load_outfits(self, json_path: str) -> Dict[str, List[Dict]]:
        """
        Carrega outfits do arquivo JSON
        
        Args:
            json_path: Caminho para o arquivo JSON
            
        Returns:
            Dict com {tendencia: [pieces]}
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Converte lista de outfits para dicionário {tendencia: [pieces]}
        outfits_dict = {}
        for outfit in data:
            tendencia = outfit.get('tendencia', 'unknown')
            pecas_dict = outfit.get('peças', {})
            
            # Converte dict de peças para lista de dicts com atributos
            pieces_list = list(pecas_dict.values())
            outfits_dict[tendencia] = pieces_list
        
        print(f"✅ Carregados {len(outfits_dict)} outfits do arquivo")
        return outfits_dict
    
    def generate_outfit_embeddings(
        self, 
        pieces: List[Dict]
    ) -> Tuple[np.ndarray, np.ndarray, int]:
        """
        Gera embeddings para todas as peças de um outfit
        
        Args:
            pieces: Lista de dicionários com atributos das peças
            
        Returns:
            Tuple (embeddings, mask, num_items)
        """
        num_items = len(pieces)
        
        if num_items > self.max_items:
            print(f"⚠️ Outfit com {num_items} peças excede máximo de {self.max_items}. Truncando.")
            pieces = pieces[:self.max_items]
            num_items = self.max_items
        
        # Gera embeddings para cada peça
        embeddings = np.zeros((self.max_items, self.embedding_dim), dtype=np.float32)
        mask = np.zeros(self.max_items, dtype=bool)
        
        for i, piece in enumerate(pieces):
            # Usa o mesmo método do EmbeddingGenerator
            piece_embedding = self.embedding_generator._generate_piece_embedding(piece)
            embeddings[i] = piece_embedding
            mask[i] = True
        
        return embeddings, mask, num_items
    
    def evaluate_all_outfits(
        self, 
        outfits_dict: Dict[str, List[Dict]]
    ) -> Dict[str, Dict]:
        """
        Avalia todos os outfits e retorna scores
        
        Args:
            outfits_dict: Dict com {image_name: [pieces]}
            
        Returns:
            Dict com {image_name: {'score': float, 'num_items': int, 'pieces': list}}
        """
        results = {}
        
        print("\n🔄 Avaliando outfits...")
        print("=" * 60)
        
        for image_name, pieces in outfits_dict.items():
            if not pieces:
                print(f"⚠️ {image_name}: Sem peças, atribuindo score 0")
                results[image_name] = {
                    'score': 0.0,
                    'num_items': 0,
                    'pieces': [],
                    'usage': 'N/A'
                }
                continue
            
            try:
                # Gera embeddings
                embeddings, mask, num_items = self.generate_outfit_embeddings(pieces)
                
                # Prediz score de compatibilidade
                score = self.model_predictor.predict_single(embeddings, mask)
                
                # Monta descrição das peças
                piece_descriptions = []
                for piece in pieces:
                    desc = f"{piece.get('primary_color', '')} {piece.get('item_type', 'item')}"
                    piece_descriptions.append(desc.strip())
                
                results[image_name] = {
                    'score': score,
                    'num_items': num_items,
                    'pieces': piece_descriptions,
                    'usage': pieces[0].get('usage', 'N/A') if pieces else 'N/A'
                }
                
                print(f"✅ {image_name}: Score = {score:.4f} ({num_items} peças)")
                
            except Exception as e:
                import traceback
                print(f"❌ Erro ao avaliar '{image_name}': {e}")
                print(f"   Traceback: {traceback.format_exc()}")
                print(f"   Peças: {len(pieces)} items")
                continue
        
        print("=" * 60)
        print(f"✅ Avaliação concluída: {len(results)} outfits processados\n")
        
        return results
    
    def plot_score_distribution(
        self, 
        results: Dict[str, Dict],
        save_dir: str = "results/vogue_analysis"
    ):
        """
        Gera gráficos individuais de distribuição dos scores
        
        Args:
            results: Resultados da avaliação
            save_dir: Diretório para salvar os gráficos
        """
        # Cria diretório
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Extrai scores
        scores = [r['score'] for r in results.values()]
        image_names = list(results.keys())
        
        # Configura estilo
        sns.set_style("whitegrid")
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.size'] = 10
        
        print(f"\n📊 Gerando gráficos individuais em: {save_path}")
        print("=" * 60)
        
        # 1. Histograma com KDE
        plt.figure(figsize=(10, 6))
        plt.hist(scores, bins=15, alpha=0.6, color='#E91E63', edgecolor='black', density=True)
        
        # KDE overlay
        from scipy.stats import gaussian_kde
        if len(scores) > 1:
            kde = gaussian_kde(scores)
            x_range = np.linspace(min(scores), max(scores), 100)
            plt.plot(x_range, kde(x_range), 'k-', linewidth=2, label='KDE')
        
        plt.axvline(np.mean(scores), color='red', linestyle='--', linewidth=2, label=f'Média: {np.mean(scores):.3f}')
        plt.axvline(np.median(scores), color='blue', linestyle='--', linewidth=2, label=f'Mediana: {np.median(scores):.3f}')
        
        # Adiciona linhas de threshold
        plt.axvline(0.8, color='#FF4444', linestyle=':', linewidth=2, alpha=0.7, label='Threshold 0.8')
        plt.axvline(0.96, color='#00C851', linestyle=':', linewidth=2, alpha=0.7, label='Threshold 0.96')
        
        plt.xlabel('Score de Compatibilidade', fontweight='bold')
        plt.ylabel('Densidade', fontweight='bold')
        plt.title('Distribuição dos Scores (Histograma + KDE)', fontweight='bold', pad=10)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path / '01_histogram_kde.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✅ 1/4 - Histograma com KDE salvo")
        
        # 2. Boxplot
        plt.figure(figsize=(10, 6))
        bp = plt.boxplot([scores], vert=True, patch_artist=True, widths=0.5,
                         medianprops=dict(color='red', linewidth=2),
                         boxprops=dict(facecolor='#E91E63', alpha=0.6),
                         whiskerprops=dict(linewidth=1.5),
                         capprops=dict(linewidth=1.5))
        
        # Adiciona pontos individuais com cores baseadas em thresholds
        point_colors = [self.get_threshold_color(s) for s in scores]
        plt.scatter([1]*len(scores), scores, alpha=0.7, s=100, c=point_colors, edgecolors='black', zorder=3)
        
        plt.ylabel('Score de Compatibilidade', fontweight='bold')
        plt.title('Boxplot com Outliers', fontweight='bold', pad=10)
        plt.xticks([1], ['Todos os Outfits'])
        plt.grid(True, alpha=0.3, axis='y')
        
        # Adiciona estatísticas ao lado do boxplot
        stats_text = f"Min: {np.min(scores):.3f}\n"
        stats_text += f"Q1: {np.percentile(scores, 25):.3f}\n"
        stats_text += f"Mediana: {np.median(scores):.3f}\n"
        stats_text += f"Q3: {np.percentile(scores, 75):.3f}\n"
        stats_text += f"Max: {np.max(scores):.3f}\n"
        stats_text += f"Std: {np.std(scores):.3f}"
        plt.text(1.35, np.median(scores), stats_text, fontsize=9, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        plt.tight_layout()
        plt.savefig(save_path / '02_boxplot.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✅ 2/4 - Boxplot salvo")
        
        # 3. Barplot horizontal dos scores individuais (top 10)
        plt.figure(figsize=(12, 8))
        sorted_results = sorted(results.items(), key=lambda x: x[1]['score'], reverse=True)[:10]
        sorted_names = [name for name, _ in sorted_results]
        sorted_scores = [data['score'] for _, data in sorted_results]
        
        # Aplica cores baseadas em thresholds
        colors = [self.get_threshold_color(s) for s in sorted_scores]
        bars = plt.barh(range(len(sorted_names)), sorted_scores, color=colors, edgecolor='black', alpha=0.8)
        plt.yticks(range(len(sorted_names)), sorted_names, fontsize=9)
        plt.xlabel('Score de Compatibilidade', fontweight='bold')
        plt.title('Top 10 Outfits por Score', fontweight='bold', pad=10)
        plt.grid(True, alpha=0.3, axis='x')
        plt.gca().invert_yaxis()
        
        # Adiciona valores nas barras
        for i, (bar, score) in enumerate(zip(bars, sorted_scores)):
            plt.text(score + 0.005, i, f'{score:.3f}', va='center', fontweight='bold', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(save_path / '03_top10_ranking.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✅ 3/4 - Ranking Top 10 salvo")
        
        # 4. Análise por número de peças
        plt.figure(figsize=(10, 6))
        num_items_scores = {}
        for data in results.values():
            num = data['num_items']
            if num not in num_items_scores:
                num_items_scores[num] = []
            num_items_scores[num].append(data['score'])
        
        # Prepara dados para violin plot
        num_items_list = sorted(num_items_scores.keys())
        scores_by_items = [num_items_scores[n] for n in num_items_list]
        
        parts = plt.violinplot(scores_by_items, positions=num_items_list, 
                               showmeans=True, showmedians=True, widths=0.6)
        
        # Colorir violins
        for pc in parts['bodies']:
            pc.set_facecolor('#E91E63')
            pc.set_alpha(0.6)
            pc.set_edgecolor('black')
        
        # Adiciona pontos individuais com cores baseadas em thresholds
        for i, (num, scores_list) in enumerate(zip(num_items_list, scores_by_items)):
            x = np.random.normal(num, 0.04, size=len(scores_list))
            point_colors = [self.get_threshold_color(s) for s in scores_list]
            plt.scatter(x, scores_list, alpha=0.7, s=50, c=point_colors, edgecolors='black', zorder=3)
        
        plt.xlabel('Número de Peças no Outfit', fontweight='bold')
        plt.ylabel('Score de Compatibilidade', fontweight='bold')
        plt.title('Distribuição de Scores por Número de Peças', fontweight='bold', pad=10)
        plt.xticks(num_items_list)
        plt.grid(True, alpha=0.3, axis='y')
        
        # Adiciona contagem em cada posição
        for num, scores_list in zip(num_items_list, scores_by_items):
            plt.text(num, min(scores_list) - 0.02, f'n={len(scores_list)}', 
                    ha='center', fontsize=8, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path / '04_scores_by_items.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✅ 4/4 - Análise por número de peças salvo")
        
        print("=" * 60)
        print(f"✅ Todos os gráficos salvos em: {save_path.absolute()}\n")
    
    def print_summary_report(self, results: Dict[str, Dict]):
        """
        Imprime relatório resumido da avaliação
        
        Args:
            results: Resultados da avaliação
        """
        scores = [r['score'] for r in results.values()]
        
        print("\n" + "="*70)
        print("📊 RELATÓRIO DE AVALIAÇÃO - TOP 10 OUTFITS VOGUE BRASIL 2025")
        print("="*70)
        
        print(f"\n📈 ESTATÍSTICAS GERAIS:")
        print(f"  • Total de outfits avaliados: {len(results)}")
        print(f"  • Score médio: {np.mean(scores):.4f}")
        print(f"  • Score mediano: {np.median(scores):.4f}")
        print(f"  • Desvio padrão: {np.std(scores):.4f}")
        print(f"  • Score mínimo: {np.min(scores):.4f}")
        print(f"  • Score máximo: {np.max(scores):.4f}")
        
        # Top 3 outfits
        print(f"\n🏆 TOP 3 OUTFITS:")
        sorted_results = sorted(results.items(), key=lambda x: x[1]['score'], reverse=True)
        for i, (name, data) in enumerate(sorted_results[:3], 1):
            print(f"\n  {i}. {name}")
            print(f"     Score: {data['score']:.4f}")
            print(f"     Peças ({data['num_items']}): {', '.join(data['pieces'])}")
            print(f"     Uso: {data['usage']}")
        
        # Análise por número de peças
        print(f"\n📦 ANÁLISE POR NÚMERO DE PEÇAS:")
        num_items_analysis = {}
        for data in results.values():
            num = data['num_items']
            if num not in num_items_analysis:
                num_items_analysis[num] = []
            num_items_analysis[num].append(data['score'])
        
        for num in sorted(num_items_analysis.keys()):
            scores_list = num_items_analysis[num]
            print(f"  • {num} peças: {len(scores_list)} outfits | Score médio: {np.mean(scores_list):.4f}")
        
        print("\n" + "="*70 + "\n")


def main():
    """Função principal"""
    
    # Configuração
    base_dir = Path(__file__).parent.parent
    json_path = base_dir / "top10outfit2025voguebr.json"
    checkpoint_path = "checkpoints/best_model.pth"
    
    print("\n" + "="*70)
    print("🎨 AVALIADOR DE OUTFITS VOGUE BRASIL 2025")
    print("="*70 + "\n")
    
    # Inicializa avaliador
    print("🔧 Inicializando avaliador...")
    evaluator = VogueOutfitEvaluator(checkpoint_path)
    
    # Carrega outfits
    print(f"📂 Carregando outfits de: {json_path.name}")
    outfits = evaluator.load_outfits(json_path)
    
    # Avalia todos os outfits
    results = evaluator.evaluate_all_outfits(outfits)
    
    # Gera relatório
    evaluator.print_summary_report(results)
    
    # Gera gráficos
    print("📊 Gerando visualizações...")
    evaluator.plot_score_distribution(results)
    
    print("\n✨ Avaliação completa!")


if __name__ == "__main__":
    main()
