from modules.pytorch_model import get_model_predictor
from modules import FeatureExtractor, JsonCleaner, OutfitFilter, EmbeddingGenerator, VectorDB, config
import json
import numpy as np

from modules.model_input import ModelInputBuilder
def main():
    # # Inicializa componentes
    # extractor = FeatureExtractor()
    # cleaner = JsonCleaner()
    # outfit_filter = OutfitFilter()
    
    # Inicializa banco vetorial
    vector_db = VectorDB()
    
    # # Cria coleções necessárias
    # vector_db.get_or_create_collection("pieces")
    
    # # Inicializa gerador de embeddings com banco existente
    # embedding_generator = EmbeddingGenerator(vector_db=vector_db)
    
    # # Extrai features de imagens
    # print("Extraindo features...")
    # extractor.process_all_folders()
    
    # # Limpa respostas com erro
    # print("\nLimpando respostas com erro...")
    # cleaner.clean_error_responses()
    
    # # Filtra outfits
    # print("\nFiltrando outfits...")
    # outfit_filter.process_responses()
    
    # # Gera e armazena embeddings
    # print("\nGerando embeddings...")
    # embedding_generator.process_and_store("pieces")
    
    # # Lista coleções existentes
    # print("\nColeções no banco:")
    # for collection in vector_db.list_collections():
    #     print(f"- {collection}")

    # # vector_db.delete_collection("user_1_pieces")
    
    # # Exemplo de uso:
    # id_para_buscar = "1"  # Substitua pelo ID que você quer buscar
    # resultado = vector_db.get_by_id("user_1_pieces", id_para_buscar)

    # if resultado:
    #     print(f"\nEmbedding encontrado para ID {id_para_buscar}:")
    #     print(f"Dimensões do embedding: {len(resultado['embedding'])}")
    #     print(f"Primeiros 5 valores: {resultado['embedding'][:5]}")
    #     print(f"Últimos 5 valores: {resultado['embedding'][-5:]}")
    # else:
    #     print(f"\nNenhum embedding encontrado para ID {id_para_buscar}")
    # file_name_test = "193875024.json"
    # path_test =  config.FILTERED_DIR / file_name_test
    # outfit_json = json.load(open(path_test, "r"))
    # emebdding_test, id_test = embedding_generator._process_outfit(outfit_json, file_name_test)
    # for i, emb in enumerate(emebdding_test):
    #     print(f"\nEmbedding {i + 1}:")
    #     print(f"ID: {id_test[i]}")
    #     print(f"Dimensões do embedding: {len(emb)}")
    #     print(f"Primeiros 5 valores: {emb[:5]}")  # Mostra apenas os primeiros 5 valores para não sobrecarregar o output
    #     vector_db.add_item(
    #       collection_name="pieces",
    #       embedding=emb,
    #       id=id_test[i]
    #     )
        
    # id_para_buscar = "193875024/5.jpg"  # Substitua pelo ID que você quer buscar
    # resultado = vector_db.get_by_id("pieces", id_para_buscar)
    
    # if resultado:
    #     print(f"\nEmbedding encontrado para ID {id_para_buscar}:")
    #     print(f"Dimensões do embedding: {len(resultado['embedding'])}")
    #     print(f"Primeiros 5 valores: {resultado['embedding'][:5]}")
    #     print(f"Últimos 5 valores: {resultado['embedding'][-5:]}")
    # else:
    #     print(f"\nNenhum embedding encontrado para ID {id_para_buscar}")

    
    resultado1 =  vector_db.get_by_id("user_1_pieces", "3")
    if resultado1:
        print(f"\nEmbedding encontrado para 3 ID em pieces:")
        print(f"Dimensões do embedding: {len(resultado1['embedding'])}")
        print(f"Primeiros 5 valores: {resultado1['embedding'][:5]}")
        print(f"Últimos 5 valores: {resultado1['embedding'][-5:]}")

    embedding = resultado1["embedding"]

    similars = vector_db.search_similar(
        collection_name="pieces",
        query_embedding=embedding,
        n_results=10
    )
    
    print(f"\nResultados da busca similar ({len(similars['ids'][0])} encontrados):")
    for i, result in enumerate(similars['ids'][0]):
        distance = similars['distances'][0][i] if 'distances' in similars else 'N/A'
        print(f"ID {result}: distance = {distance}")

    similar_ids = similars['ids'][0]
    
    unique_outfits = set()
    for sid in similar_ids:
        outfit_id = sid.split('/')[0]
        unique_outfits.add(outfit_id)
    
    outfits_dict = {}
    for outfit_id in unique_outfits:
        pieces = vector_db.get_pieces_by_outfit("pieces", outfit_id)
        outfits_dict[outfit_id] = pieces
    
    similar_piece_ids = set(similar_ids)
    
    for outfit_id in outfits_dict.keys():
        original_pieces = outfits_dict[outfit_id]
        filtered_pieces = [
            piece for piece in original_pieces 
            if piece['piece_id'] not in similar_piece_ids
        ]
        outfits_dict[outfit_id] = filtered_pieces
    
    model_input_builder = ModelInputBuilder(max_items=5, embedding_dim=96)
    
    batch_inputs = model_input_builder.build_batch_inputs(
        new_piece_embedding=embedding,
        outfits_dict=outfits_dict
    )


    model_predictor = get_model_predictor(checkpoint_path="../checkpoints/best_model.pth")


    all_scores = model_predictor.predict_batch(batch_inputs)
    print(all_scores)

if __name__ == "__main__":
    main()