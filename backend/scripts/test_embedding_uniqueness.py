"""
Script de Teste de Unicidade e Determinismo de Embeddings

Este script valida que:
1. Peças diferentes geram embeddings diferentes (unicidade)
2. Mesma peça sempre gera mesmo embedding (determinismo)

Casos de teste baseados em exemplos reais que apresentavam colisão antes da correção.
"""

import numpy as np
import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from modules import EmbeddingGenerator


def print_separator(title: str = "", char: str = "=", width: int = 70):
    """Imprime separador visual"""
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"\n{char * padding} {title} {char * padding}")
    else:
        print(f"\n{char * width}")


def test_embedding_uniqueness():
    """
    Valida que embeddings diferentes são gerados para peças diferentes
    
    Testa os 3 casos que apresentavam colisão antes da correção:
    - train1: blouse + peach + chiffon
    - 1.jpg: sleeveless blouse + beige + synthetic
    - 2.jpg: bikini top + peach + synthetic
    """
    print_separator("TESTE DE UNICIDADE", "=")
    
    # Casos de teste (JSONs reais que colidiam)
    test_cases = {
        "train1": {
            "category": "tops",
            "item_type": "blouse",
            "primary_color": "peach",
            "usage": "casual",
            "texture": "chiffon",
            "print_category": "solid"
        },
        "1.jpg": {
            "category": "tops",
            "item_type": "sleeveless blouse",
            "primary_color": "beige",
            "usage": "casual",
            "texture": "synthetic",
            "print_category": "solid"
        },
        "2.jpg": {
            "category": "tops",
            "item_type": "bikini top",
            "primary_color": "peach",
            "usage": "casual",
            "texture": "synthetic",
            "print_category": "solid"
        }
    }
    
    generator = EmbeddingGenerator()
    
    print("\n📦 Gerando embeddings para os 3 casos de teste...\n")
    
    embeddings = {}
    for name, piece_data in test_cases.items():
        emb = generator._generate_piece_embedding(piece_data)
        embeddings[name] = emb
        
        print(f"✅ {name}:")
        print(f"   Shape: {emb.shape}")
        print(f"   Tipo: {emb.dtype}")
        print(f"   Primeiros 5 valores: {emb[:5]}")
        print(f"   Últimos 5 valores: {emb[-5:]}")
        
        # Validar shape
        if emb.shape != (96,):
            print(f"   ❌ ERRO: Shape incorreto! Esperado (96,), obtido {emb.shape}")
            return False
        
        # Validar tipo
        if emb.dtype != np.float32:
            print(f"   ⚠️  AVISO: Tipo incorreto! Esperado float32, obtido {emb.dtype}")
        
        # Validar que não é zero
        if np.allclose(emb, 0):
            print(f"   ❌ ERRO: Embedding é zero!")
            return False
        
        # Validar que não tem NaN/Inf
        if np.isnan(emb).any() or np.isinf(emb).any():
            print(f"   ❌ ERRO: Embedding contém NaN ou Inf!")
            return False
    
    # Verificar unicidade
    print_separator("COMPARAÇÃO DE EMBEDDINGS")
    
    names = list(embeddings.keys())
    all_unique = True
    
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            name1, name2 = names[i], names[j]
            emb1, emb2 = embeddings[name1], embeddings[name2]
            
            # Similaridade cosine
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            
            # Distância euclidiana
            distance = np.linalg.norm(emb1 - emb2)
            
            print(f"\n🔍 {name1} vs {name2}:")
            print(f"   Similaridade cosine: {similarity:.6f}")
            print(f"   Distância euclidiana: {distance:.6f}")
            
            # Verificar que não são idênticos
            is_identical = np.allclose(emb1, emb2, atol=1e-6)
            
            if is_identical:
                print(f"   ❌ ERRO: Embeddings são IDÊNTICOS!")
                print(f"      Diff máxima: {np.max(np.abs(emb1 - emb2))}")
                all_unique = False
            else:
                print(f"   ✅ Embeddings são DIFERENTES (OK)")
    
    return all_unique


def test_determinism():
    """
    Valida que o mesmo JSON sempre gera o mesmo embedding
    
    Testa que 3 gerações consecutivas produzem embeddings idênticos.
    """
    print_separator("TESTE DE DETERMINISMO", "=")
    
    piece_data = {
        "category": "tops",
        "item_type": "blouse",
        "primary_color": "peach",
        "usage": "casual",
        "texture": "chiffon",
        "print_category": "solid"
    }
    
    generator = EmbeddingGenerator()
    
    print("\n🔄 Gerando mesmo embedding 3 vezes...\n")
    
    # Gerar embedding 3 vezes
    emb1 = generator._generate_piece_embedding(piece_data)
    emb2 = generator._generate_piece_embedding(piece_data)
    emb3 = generator._generate_piece_embedding(piece_data)
    
    print(f"Embedding 1: shape={emb1.shape}, dtype={emb1.dtype}")
    print(f"Embedding 2: shape={emb2.shape}, dtype={emb2.dtype}")
    print(f"Embedding 3: shape={emb3.shape}, dtype={emb3.dtype}")
    
    # Verificar identidade
    is_identical_12 = np.allclose(emb1, emb2, atol=1e-9)
    is_identical_23 = np.allclose(emb2, emb3, atol=1e-9)
    is_identical_13 = np.allclose(emb1, emb3, atol=1e-9)
    
    print(f"\n🔍 Comparando embeddings:")
    print(f"   Emb1 == Emb2? {'✅ SIM' if is_identical_12 else '❌ NÃO'}")
    print(f"   Emb2 == Emb3? {'✅ SIM' if is_identical_23 else '❌ NÃO'}")
    print(f"   Emb1 == Emb3? {'✅ SIM' if is_identical_13 else '❌ NÃO'}")
    
    if is_identical_12 and is_identical_23 and is_identical_13:
        print(f"\n✅ DETERMINISMO GARANTIDO!")
        return True
    else:
        print(f"\n❌ FALHA NO DETERMINISMO!")
        print(f"   Max diff 1-2: {np.max(np.abs(emb1 - emb2))}")
        print(f"   Max diff 2-3: {np.max(np.abs(emb2 - emb3))}")
        print(f"   Max diff 1-3: {np.max(np.abs(emb1 - emb3))}")
        return False


def test_attribute_contribution():
    """
    Valida que cada atributo contribui para o embedding final
    
    Testa que mudanças em cada atributo individual resultam em embeddings diferentes.
    """
    print_separator("TESTE DE CONTRIBUIÇÃO DE ATRIBUTOS", "=")
    
    base_piece = {
        "category": "tops",
        "item_type": "blouse",
        "primary_color": "peach",
        "usage": "casual",
        "texture": "chiffon",
        "print_category": "solid"
    }
    
    generator = EmbeddingGenerator()
    base_emb = generator._generate_piece_embedding(base_piece)
    
    print("\n🧪 Testando contribuição de cada atributo...\n")
    
    attributes_to_test = [
        ("category", "bottoms"),
        ("item_type", "t-shirt"),
        ("primary_color", "blue"),
        ("usage", "formal"),
        ("texture", "cotton"),
        ("print_category", "striped")
    ]
    
    all_different = True
    
    for attr, new_value in attributes_to_test:
        # Cria cópia modificada
        modified_piece = base_piece.copy()
        modified_piece[attr] = new_value
        
        # Gera embedding modificado
        modified_emb = generator._generate_piece_embedding(modified_piece)
        
        # Calcula diferença
        is_different = not np.allclose(base_emb, modified_emb, atol=1e-6)
        distance = np.linalg.norm(base_emb - modified_emb)
        
        status = "✅ DIFERENTE" if is_different else "❌ IDÊNTICO"
        print(f"{attr:15s} = '{new_value:15s}' → {status} (distância: {distance:.4f})")
        
        if not is_different:
            all_different = False
            print(f"   ❌ ERRO: Mudança em '{attr}' não afetou o embedding!")
    
    return all_different


def main():
    """Executa todos os testes"""
    print_separator("TESTES DE VALIDAÇÃO DE EMBEDDINGS", "█")
    print("\nValidando correção do bug de embeddings colidindo")
    print("Casos: train1, 1.jpg, 2.jpg")
    
    # Executar testes
    test1_pass = test_embedding_uniqueness()
    test2_pass = test_determinism()
    test3_pass = test_attribute_contribution()
    
    # Resultado final
    print_separator("RESULTADO FINAL", "█")
    
    print(f"\n{'✅' if test1_pass else '❌'} Teste de Unicidade: {'PASSOU' if test1_pass else 'FALHOU'}")
    print(f"{'✅' if test2_pass else '❌'} Teste de Determinismo: {'PASSOU' if test2_pass else 'FALHOU'}")
    print(f"{'✅' if test3_pass else '❌'} Teste de Contribuição: {'PASSOU' if test3_pass else 'FALHOU'}")
    
    if test1_pass and test2_pass and test3_pass:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Bug de embeddings colidindo foi corrigido com sucesso!")
        print("\n📝 Próximos passos:")
        print("   1. Limpar ChromaDB (deletar coleção 'pieces')")
        print("   2. Executar main.py para regenerar embeddings")
        print("   3. Seguir guia em memory-bank/pipeline-execution-guide.md")
        return 0
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
        print("⚠️  Verifique as correções em:")
        print("   - modules/embeddings.py")
        print("   - modules/config.py")
        print("   - modules/vector_db.py")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
