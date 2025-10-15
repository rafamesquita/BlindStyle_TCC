from modules import FeatureExtractor, JsonCleaner, OutfitFilter, EmbeddingGenerator, VectorDB, config
import json
def main():
    # Inicializa componentes
    extractor = FeatureExtractor()
    cleaner = JsonCleaner()
    outfit_filter = OutfitFilter()
    
    # Inicializa banco vetorial
    vector_db = VectorDB()
    
    # Cria coleções necessárias
    vector_db.get_or_create_collection("pieces")
    
    # Inicializa gerador de embeddings com banco existente
    embedding_generator = EmbeddingGenerator(vector_db=vector_db)
    
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
    
    # # Exemplo de uso:
    # id_para_buscar = "158304930/1.jpg"  # Substitua pelo ID que você quer buscar
    # resultado = vector_db.get_by_id("pieces", id_para_buscar)

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

if __name__ == "__main__":
    main()