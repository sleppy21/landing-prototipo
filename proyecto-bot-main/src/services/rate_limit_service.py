"""
Servicio de Rate Limiting para el Bot Asistente de Consultas
"""
import time
import threading
from typing import Dict, Tuple
from collections import defaultdict, deque
import logging
from config.settings import config

logger = logging.getLogger(__name__)

class RateLimitService:
    """Servicio de rate limiting con ventana deslizante"""
    
    def __init__(self, requests_per_minute: int = None):
        self.requests_per_minute = requests_per_minute or config.REQUESTS_PER_MINUTE
        self.requests_log: Dict[str, deque] = defaultdict(lambda: deque())
        self.lock = threading.RLock()
        self.stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'unique_clients': 0
        }
    
    def is_allowed(self, client_id: str) -> Tuple[bool, Dict[str, any]]:
        """
        Verifica si una solicitud está permitida
        
        Returns:
            Tuple[bool, Dict]: (permitido, info_adicional)
        """
        with self.lock:
            now = time.time()
            client_requests = self.requests_log[client_id]
            
            # Limpiar solicitudes antiguas (más de 60 segundos)
            while client_requests and now - client_requests[0] > 60:
                client_requests.popleft()
            
            current_count = len(client_requests)
            remaining = max(0, self.requests_per_minute - current_count)
            
            # Actualizar estadísticas
            self.stats['total_requests'] += 1
            self.stats['unique_clients'] = len(self.requests_log)
            
            if current_count >= self.requests_per_minute:
                self.stats['blocked_requests'] += 1
                
                # Calcular tiempo hasta la próxima solicitud permitida
                oldest_request = client_requests[0]
                reset_time = oldest_request + 60
                wait_time = max(0, reset_time - now)
                
                logger.warning(f"Rate limit exceeded for client {client_id}")
                
                return False, {
                    'reason': 'rate_limit_exceeded',
                    'current_count': current_count,
                    'limit': self.requests_per_minute,
                    'remaining': 0,
                    'reset_in_seconds': int(wait_time),
                    'retry_after': int(wait_time)
                }
            
            # Agregar la solicitud actual
            client_requests.append(now)
            
            # Calcular tiempo hasta el reset
            if current_count > 0:
                oldest_request = client_requests[0]
                reset_time = oldest_request + 60
            else:
                reset_time = now + 60
            
            logger.debug(f"Request allowed for client {client_id}. Remaining: {remaining - 1}")
            
            return True, {
                'current_count': current_count + 1,
                'limit': self.requests_per_minute,
                'remaining': remaining - 1,
                'reset_in_seconds': int(reset_time - now)
            }
    
    def get_client_info(self, client_id: str) -> Dict[str, any]:
        """Obtiene información detallada de un cliente"""
        with self.lock:
            now = time.time()
            client_requests = self.requests_log.get(client_id, deque())
            
            # Limpiar solicitudes antiguas
            while client_requests and now - client_requests[0] > 60:
                client_requests.popleft()
            
            current_count = len(client_requests)
            remaining = max(0, self.requests_per_minute - current_count)
            
            # Calcular estadísticas del cliente
            if client_requests:
                first_request = client_requests[0]
                last_request = client_requests[-1]
                avg_interval = (last_request - first_request) / max(1, len(client_requests) - 1)
            else:
                first_request = last_request = avg_interval = 0
            
            return {
                'client_id': client_id,
                'current_count': current_count,
                'limit': self.requests_per_minute,
                'remaining': remaining,
                'first_request_time': first_request,
                'last_request_time': last_request,
                'average_interval_seconds': round(avg_interval, 2),
                'is_at_limit': current_count >= self.requests_per_minute
            }
    
    def get_stats(self) -> Dict[str, any]:
        """Obtiene estadísticas globales del rate limiting"""
        with self.lock:
            now = time.time()
            active_clients = 0
            total_active_requests = 0
            
            # Limpiar y contar clientes activos
            for client_id in list(self.requests_log.keys()):
                client_requests = self.requests_log[client_id]
                
                # Limpiar solicitudes antiguas
                while client_requests and now - client_requests[0] > 60:
                    client_requests.popleft()
                
                if client_requests:
                    active_clients += 1
                    total_active_requests += len(client_requests)
                else:
                    # Eliminar clientes sin solicitudes recientes
                    del self.requests_log[client_id]
            
            block_rate = (self.stats['blocked_requests'] / max(1, self.stats['total_requests'])) * 100
            
            return {
                'total_requests': self.stats['total_requests'],
                'blocked_requests': self.stats['blocked_requests'],
                'block_rate_percentage': round(block_rate, 2),
                'active_clients': active_clients,
                'total_active_requests': total_active_requests,
                'requests_per_minute_limit': self.requests_per_minute,
                'average_requests_per_client': round(total_active_requests / max(1, active_clients), 2)
            }
    
    def reset_client(self, client_id: str) -> bool:
        """Resetea el contador de un cliente específico"""
        with self.lock:
            if client_id in self.requests_log:
                del self.requests_log[client_id]
                logger.info(f"Rate limit reset for client {client_id}")
                return True
            return False
    
    def cleanup_old_entries(self) -> int:
        """Limpia entradas antiguas y retorna el número de clientes limpiados"""
        with self.lock:
            now = time.time()
            cleaned_clients = 0
            
            for client_id in list(self.requests_log.keys()):
                client_requests = self.requests_log[client_id]
                
                # Limpiar solicitudes antiguas
                initial_count = len(client_requests)
                while client_requests and now - client_requests[0] > 60:
                    client_requests.popleft()
                
                # Si no quedan solicitudes, eliminar el cliente
                if not client_requests:
                    del self.requests_log[client_id]
                    cleaned_clients += 1
                elif len(client_requests) < initial_count:
                    logger.debug(f"Cleaned {initial_count - len(client_requests)} old requests for client {client_id}")
            
            if cleaned_clients > 0:
                logger.info(f"Cleaned up {cleaned_clients} inactive clients")
            
            return cleaned_clients

# Instancia global del rate limiter
rate_limit_service = RateLimitService()