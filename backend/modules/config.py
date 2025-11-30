import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Diretórios
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMAGES_DIR = BASE_DIR / "archive" / "images"
RESPONSES_DIR = BASE_DIR / "responses"
FILTERED_DIR = BASE_DIR / "filtered_outfits"
VECTOR_DB_DIR = BASE_DIR / "chroma_db"

# Configurações de Embedding
ATTRIBUTES = ["category", "item_type", "primary_color", "usage", "texture", "print_category"]
ATTR_DIM = 16
PIECE_DIM = len(ATTRIBUTES) * ATTR_DIM

# Configurações de Filtragem
MAX_ITEMS_PER_OUTFIT = 5

# ============================================================================
# SISTEMA DE VALIDAÇÃO DE ATRIBUTOS
# ============================================================================

# Categorias válidas (ÚNICA RESTRIÇÃO MANTIDA)
# Apenas "category" é restrito a estes valores exatos
VALID_CATEGORIES = ["tops", "bottoms", "shoes", "others"]

# ATENÇÃO: Listas abaixo são APENAS REFERÊNCIA HISTÓRICA
# Valores LIVRES são aceitos na prática para estes atributos:
# - usage, texture, print_category: podem ter qualquer valor textual
# - item_type, primary_color: sempre foram valores livres

# Lista de referência para "usage" (valores livres aceitos)
VALID_USAGE = ["casual", "formal", "business", "sportswear", "sleepwear", "outerwear", "party", "workwear"]

# Lista de referência para "texture" (valores livres aceitos)
VALID_TEXTURE = ["cotton", "denim", "leather", "polyester", "wool", "silk", "linen", "knit", "suede", "nylon", "fleece", "velvet", "mesh", "others"]

# Lista de referência para "print_category" (valores livres aceitos)
VALID_PRINT = ["striped", "animal", "floral", "plaid", "plain", "abstract", "logo", "graphic"]

# Prompt para extração de features
FEATURE_EXTRACTION_PROMPT = """
Context:
From a given set of images, information about compatible outfit compositions is to be extracted. Each valid image represents a single clothing item that makes up these outfits. The goal is to generate objective descriptions for each piece, based on predefined characteristics, in order to facilitate future combination and analysis of these clothes from a structured dataset.

Each image will be preceded by a line containing its filename (e.g., "image1.jpg"). Use this filename as the key in the resulting JSON.

Task:
Classify each image into one of the following categories:

tops
bottoms
shoes
others (if the image contains multiple items or a single item cannot be clearly identified)

For images classified as tops, bottoms, or shoes, identify and describe the following characteristics using the specified values below:

item_type: type of the piece (free text, be specific but avoid outliers - e.g., "blouse", "sleeveless blouse", "bikini top")
primary_color: predominant color (free text, use common color names - e.g., "peach", "beige", "dark blue")
usage: intended use (free text, can reference: casual, formal, business, sportswear, sleepwear, outerwear, party, workwear)
texture: type of fabric or material (free text, can reference: cotton, denim, leather, polyester, wool, silk, linen, knit, suede, nylon, fleece, velvet, mesh)
print_category: main pattern or print (free text, can reference: striped, animal, floral, plaid, plain, abstract, logo, graphic)

Return the results in JSON format, where the key is the filename of the image and the value is an object with the classification and attributes.

Output example:
{{
  "1.jpg": {{
    "category": "tops",
    "item_type": "tshirt",
    "primary_color": "blue",
    "usage": "casual",
    "texture": "cotton",
    "print_category": "graphic"
  }}
}}

Images and Filenames to proccess:
"""

# Chave da API Gemini (deve ser movida para variável de ambiente posteriormente)
GEMINI_API_KEY = os.getenv('GEMINI_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente. Crie um arquivo .env com a chave.")

LLM_MODEL = "gemini-2.5-pro"

IMAGES_DIR = BASE_DIR / "archive" / "images"