"""
Servicio de gestión de cache para el Bot Asistente de Consultas
"""
import time
import threading
from typing import Dict, Any, Optional, Tuple
from collections import OrderedDict
import logging
from config.settings import config

logger = logging.getLogger(__name__)

class CacheService:
    """Servicio de cache thread-safe con TTL (Time To Live)"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = None):
        self.max_size = max_size
        self.default_ttl = default_ttl or config.CACHE_TTL
        self.cache: OrderedDict[str, Tuple[float, Any]] = OrderedDict()
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache"""
        with self.lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            timestamp, value = self.cache[key]
            
            # Verificar si ha expirado
            if time.time() - timestamp > self.default_ttl:
                del self.cache[key]
                self.stats['misses'] += 1
                self.stats['size'] = len(self.cache)
                logger.debug(f"Cache key '{key}' expired")
                return None
            
            # Mover al final (LRU)
            self.cache.move_to_end(key)
            self.stats['hits'] += 1
            logger.debug(f"Cache hit for key '{key}'")
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Establece un valor en el cache"""
        with self.lock:
            current_time = time.time()
            
            # Si la clave ya existe, actualizarla
            if key in self.cache:
                self.cache[key] = (current_time, value)
                self.cache.move_to_end(key)
                logger.debug(f"Cache updated for key '{key}'")
                return
            
            # Si el cache está lleno, eliminar el más antiguo
            while len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
                logger.debug(f"Cache evicted key '{oldest_key}'")
            
            # Agregar nueva entrada
            self.cache[key] = (current_time, value)
            self.stats['size'] = len(self.cache)
            logger.debug(f"Cache set for key '{key}'")
    
    def delete(self, key: str) -> bool:
        """Elimina una clave del cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.stats['size'] = len(self.cache)
                logger.debug(f"Cache deleted key '{key}'")
                return True
            return False
    
    def clear(self) -> None:
        """Limpia todo el cache"""
        with self.lock:
            self.cache.clear()
            self.stats['size'] = 0
            logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """Limpia entradas expiradas y retorna el número de entradas eliminadas"""
        with self.lock:
            current_time = time.time()
            expired_keys = []
            
            for key, (timestamp, _) in self.cache.items():
                if current_time - timestamp > self.default_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            self.stats['size'] = len(self.cache)
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.stats,
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests,
                'max_size': self.max_size
            }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Información detallada del cache para debugging"""
        with self.lock:
            current_time = time.time()
            entries_info = []
            
            for key, (timestamp, value) in list(self.cache.items())[:10]:  # Solo los primeros 10
                age = current_time - timestamp
                entries_info.append({
                    'key': key,
                    'age_seconds': round(age, 2),
                    'expired': age > self.default_ttl,
                    'value_type': type(value).__name__
                })
            
            return {
                'stats': self.get_stats(),
                'sample_entries': entries_info,
                'total_entries': len(self.cache)
            }

# Instancia global del cache
cache_service = CacheService()