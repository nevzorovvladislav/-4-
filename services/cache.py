import json
import os
import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CacheManager:
    """Простой менеджер кэша, сохраняющий данные в файл с ограничением по времени (TTL)."""
    def __init__(self, cache_file="cache.json", ttl=3600):
        self.cache_file = cache_file
        self.ttl = ttl  # Time To Live в секундах

    def get(self, key: str) -> Any:
        """Получает значение из кэша."""
        cache = self._load_cache()
        if key in cache:
            item = cache[key]
            if time.time() - item.get('timestamp', 0) < self.ttl:
                return item.get('data')
        return None

    def set(self, key: str, data: Any):
        """Сохраняет значение в кэш."""
        cache = self._load_cache()
        cache[key] = {
            'timestamp': time.time(),
            'data': data
        }
        self._save_cache(cache)

    def _load_cache(self) -> Dict:
        """Загружает весь кэш из файла."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка загрузки кэша: {e}")
        return {}

    def _save_cache(self, cache: Dict):
        """Сохраняет кэш в файл."""
        try:
            # Убедимся, что директория существует
            os.makedirs(os.path.dirname(self.cache_file) or '.', exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения кэша: {e}")


# Создаем глобальный экземпляр кэша (если он нужен)
# cache_manager = CacheManager(cache_file=os.path.join(os.getcwd(), 'data', 'api_cache.json'))