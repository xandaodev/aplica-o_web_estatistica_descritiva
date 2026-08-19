"""
Configurações centrais do projeto.

Mantém paths e constantes num único lugar para evitar "magic strings"
espalhadas pelo código (app.py, testes, notebooks etc.).
"""

from pathlib import Path

# Raiz do projeto (dois níveis acima deste arquivo: src/config.py -> raiz/)
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATASET_PATH = DATA_DIR / "dataset.csv"

PAGE_TITLE = "Credit Risk Analytics"
PAGE_ICON = "📊"

# Nome da coluna que, embora rotulada como "Status_of_existing_checking_account"
# no dataset original, contém na prática os valores 'good'/'bad' — ou seja,
# funciona como a variável de risco (target). Ver docs/METODOLOGIA.md para
# a discussão completa sobre essa inconsistência de nomenclatura.
TARGET_COLUMN = "Status_of_existing_checking_account"

DEFAULT_SUMMARY_METRICS = ["mean", "median", "std", "count"]
