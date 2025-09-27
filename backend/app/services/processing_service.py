"""
Servicio de control de procesamiento para el Bot Asistente de Consultas
"""
import time
import threading
from typing import Optional, Dict, Any
import logging
from config.settings import config

logger = logging.getLogger(__name__)

class ProcessingLockService:
    """Servicio para controlar el procesamiento simultáneo de consultas"""
    
    def __init__(self, max_processing_time: int = None):
        self.max_processing_time = max_processing_time or config.MAX_PROCESSING_TIME
        self.lock = threading.RLock()
        self.is_processing = False
        self.processing_start_time: Optional[float] = None
        self.current_query: Optional[str] = None
        self.processing_history = []
        self.stats = {
            'total_attempts': 0,
            'successful_processes': 0,
            'blocked_attempts': 0,
            'timeout_recoveries': 0
        }
    
    def is_bot_processing(self) -> bool:
        """Verifica si el bot está procesando una consulta actualmente"""
        with self.lock:
            # Verificar si hay un procesamiento colgado (timeout)
            if self.is_processing and self.processing_start_time:
                elapsed_time = time.time() - self.processing_start_time
                if elapsed_time > self.max_processing_time:
                    logger.warning(
                        f"Procesamiento colgado detectado después de {elapsed_time:.1f}s, "
                        f"liberando bloqueo para query: '{self.current_query}'"
                    )
                    self._force_release()
                    self.stats['timeout_recoveries'] += 1
            
            return self.is_processing
    
    def start_processing(self, query: str = "") -> bool:
        """
        Intenta iniciar el procesamiento. Retorna True si se pudo iniciar.
        
        Args:
            query: La consulta que se va a procesar (para logging)
        """
        with self.lock:
            self.stats['total_attempts'] += 1
            
            if self.is_processing:
                self.stats['blocked_attempts'] += 1
                logger.info(f"Procesamiento rechazado para query: '{query}' - Bot ocupado")
                return False
            
            self.is_processing = True
            self.processing_start_time = time.time()
            self.current_query = query
            
            logger.info(f"Procesamiento iniciado para query: '{query}'")
            return True
    
    def finish_processing(self) -> None:
        """Marca el procesamiento como finalizado"""
        with self.lock:
            if self.is_processing:
                elapsed_time = time.time() - (self.processing_start_time or 0)
                
                # Agregar al historial
                self.processing_history.append({
                    'query': self.current_query,
                    'start_time': self.processing_start_time,
                    'duration': elapsed_time,
                    'completed': True
                })
                
                # Mantener solo los últimos 10 registros
                if len(self.processing_history) > 10:
                    self.processing_history.pop(0)
                
                self.stats['successful_processes'] += 1
                logger.info(
                    f"Procesamiento completado en {elapsed_time:.1f}s para query: '{self.current_query}'"
                )
                
                self._release()
    
    def _force_release(self) -> None:
        """Libera el bloqueo por timeout"""
        if self.is_processing:
            elapsed_time = time.time() - (self.processing_start_time or 0)
            
            # Agregar al historial como timeout
            self.processing_history.append({
                'query': self.current_query,
                'start_time': self.processing_start_time,
                'duration': elapsed_time,
                'completed': False,
                'reason': 'timeout'
            })
            
            if len(self.processing_history) > 10:
                self.processing_history.pop(0)
        
        self._release()
    
    def _release(self) -> None:
        """Libera el bloqueo interno"""
        self.is_processing = False
        self.processing_start_time = None
        self.current_query = None
    
    def get_current_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del procesamiento"""
        with self.lock:
            if not self.is_processing:
                return {
                    'status': 'idle',
                    'is_processing': False,
                    'message': 'Bot disponible para nuevas consultas'
                }
            
            elapsed_time = time.time() - (self.processing_start_time or 0)
            remaining_time = max(0, self.max_processing_time - elapsed_time)
            
            return {
                'status': 'processing',
                'is_processing': True,
                'current_query': self.current_query,
                'elapsed_time': round(elapsed_time, 1),
                'remaining_time': round(remaining_time, 1),
                'progress_percentage': min(100, (elapsed_time / self.max_processing_time) * 100),
                'message': f'Procesando consulta: "{self.current_query[:50]}..."'
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del servicio de procesamiento"""
        with self.lock:
            success_rate = 0
            avg_duration = 0
            
            if self.stats['total_attempts'] > 0:
                success_rate = (self.stats['successful_processes'] / self.stats['total_attempts']) * 100
            
            completed_processes = [h for h in self.processing_history if h.get('completed', False)]
            if completed_processes:
                avg_duration = sum(h['duration'] for h in completed_processes) / len(completed_processes)
            
            return {
                **self.stats,
                'success_rate_percentage': round(success_rate, 2),
                'average_processing_time': round(avg_duration, 2),
                'max_processing_time': self.max_processing_time,
                'current_status': self.get_current_status()['status']
            }
    
    def get_processing_history(self) -> list:
        """Obtiene el historial de procesamiento reciente"""
        with self.lock:
            return list(self.processing_history)  # Copia para evitar modificaciones externas
    
    def reset_stats(self) -> None:
        """Reinicia las estadísticas"""
        with self.lock:
            self.stats = {
                'total_attempts': 0,
                'successful_processes': 0,
                'blocked_attempts': 0,
                'timeout_recoveries': 0
            }
            self.processing_history.clear()
            logger.info("Estadísticas de procesamiento reiniciadas")

# Instancia global del servicio de procesamiento
processing_lock_service = ProcessingLockService()