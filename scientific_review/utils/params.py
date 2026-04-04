# scientific_review/utils/load_params.py
# загрузка параметров из params.yaml


import yaml
from functools import lru_cache
from typing import Dict, Any

@lru_cache()
def get_params(path: str = "scientific_review/params.yaml") -> Dict[str, Any]:
    """
    Загружает params.yaml (кэшируется)

    Args:
        path: путь к yaml

    Returns:
        dict: параметры проекта
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
    
if __name__ == "__main__":
    params = get_params()
    print(params)
