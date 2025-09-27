"""
Motor de chat principal que integra todos los componentes del Bot Asistente de Consultas
"""
import json
import logging
import random
from typing import Dict, Any, List, Optional
from pathlib import Path

from config.settings import config
from src.models.schemas import ChatResponse, Product, FAQ, Offer
from src.core.intent_processor import IntentProcessor
from src.services.cache_service import cache_service
from src.utils.text_utils import normalize_text, calculate_text_similarity

logger = logging.getLogger(__name__)

class ChatEngine:
    """Motor principal del chat que coordina todos los componentes"""
    
    def __init__(self):
        """Inicializa el motor de chat"""
        self.intent_processor = IntentProcessor()
        self.data = self._load_data()
        self.suggestions = self._load_suggestions()
        
        # Estadísticas del motor
        self.stats = {
            'total_questions': 0,
            'cache_hits': 0,
            'successful_responses': 0,
            'fallback_responses': 0
        }
        
        logger.info("ChatEngine initialized successfully")
    
    def _load_data(self) -> Dict[str, Any]:
        """Carga los datos del catálogo"""
        try:
            data_path = Path(config.DATA_FILE)
            if not data_path.exists():
                logger.error(f"Data file not found: {data_path}")
                return {}
            
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded data: {len(data.get('productos', []))} productos, "
                       f"{len(data.get('faq', []))} FAQs, "
                       f"{len(data.get('ofertas_actuales', []))} ofertas")
            
            return data
            
        except Exception as e:
            logger.exception(f"Error loading data: {e}")
            return {}
    
    def _load_suggestions(self) -> List[Dict[str, str]]:
        """Carga las sugerencias predeterminadas"""
        return [
            {"text": "Ver ofertas del día", "category": "ofertas", "icon": "tag"},
            {"text": "Política de devoluciones", "category": "politicas", "icon": "exchange-alt"},
            {"text": "Métodos de pago", "category": "pagos", "icon": "credit-card"},
            {"text": "Guía de tallas", "category": "productos", "icon": "ruler"},
            {"text": "Ubicación de tienda", "category": "tiendas", "icon": "map-marker-alt"},
            {"text": "Horario de atención", "category": "tiendas", "icon": "clock"},
            {"text": "Últimas novedades", "category": "productos", "icon": "sparkles"},
            {"text": "Ropa formal", "category": "productos", "icon": "user-tie"},
            {"text": "Casacas de temporada", "category": "productos", "icon": "tshirt"},
            {"text": "Jeans disponibles", "category": "productos", "icon": "jeans"}
        ]
    
    def process_question(self, question: str, client_id: str = "unknown") -> Dict[str, Any]:
        """
        Procesa una pregunta del usuario y retorna la respuesta
        
        Args:
            question: Pregunta del usuario
            client_id: ID del cliente (para logging y cache)
            
        Returns:
            Dict con la respuesta del chat
        """
        try:
            self.stats['total_questions'] += 1
            question_normalized = normalize_text(question)
            
            # Verificar cache
            cache_key = f"q:{question_normalized}"
            cached_response = cache_service.get(cache_key)
            if cached_response:
                self.stats['cache_hits'] += 1
                logger.debug(f"Cache hit for question: {question[:50]}...")
                return cached_response
            
            # Usar el nuevo procesador de intenciones limpio
            result = self.intent_processor.procesar_mensaje(question)
            
            # Si el procesador encontró una intención específica, usar su respuesta
            if result['confidence'] >= 0.8:
                response = result
            else:
                # Búsqueda contextual para consultas más complejas
                response = self._search_contextual_response(question, result.get('intent'))
            
            # Cachear la respuesta
            cache_service.set(cache_key, response)
            
            self.stats['successful_responses'] += 1
            logger.info(f"Question processed successfully: {question[:50]}...")
            
            return response
            
        except Exception as e:
            logger.exception(f"Error processing question: {question[:50]}...")
            self.stats['fallback_responses'] += 1
            
            return {
                "answer": "Disculpa, estoy teniendo problemas técnicos. ¿Podrías reformular tu pregunta?",
                "confidence": 0.1,
                "error": str(e) if config.DEBUG else None
            }
    

    
    def _search_contextual_response(self, question: str, intent = None) -> Dict[str, Any]:
        """Busca una respuesta contextual basada en la pregunta"""
        question_lower = question.lower()
        
        # Búsqueda de ofertas
        if any(word in question_lower for word in ['oferta', 'ofertas', 'descuento', 'promocion']):
            return self._handle_offers_query(question_lower)
        
        # Búsqueda de productos por precio
        if any(word in question_lower for word in ['precio', 'costo', 'valor', 'cuanto']):
            return self._handle_price_query(question_lower)
        
        # Búsqueda de tallas
        if any(word in question_lower for word in ['talla', 'tallas', 'medida', 'size']):
            return self._handle_size_query(question_lower)
        
        # Búsqueda de ubicación/horarios
        if any(word in question_lower for word in ['ubicacion', 'direccion', 'donde', 'tienda']):
            return self._handle_location_query()
        
        if any(word in question_lower for word in ['horario', 'horarios', 'abierto', 'cerrado']):
            return self._handle_schedule_query()
        
        # Búsqueda de devoluciones
        if any(word in question_lower for word in ['devolucion', 'devoluciones', 'cambio', 'reembolso']):
            return self._handle_returns_query()
        
        # Búsqueda en FAQs
        faq_response = self._search_faqs(question_lower)
        if faq_response:
            return faq_response
        
        # Búsqueda general de productos
        product_response = self._search_products(question_lower)
        if product_response:
            return product_response
        
        # Respuesta de fallback
        return self._generate_fallback_response(question)
    
    def _handle_offers_query(self, question: str) -> Dict[str, Any]:
        """Maneja consultas sobre ofertas"""
        ofertas = self.data.get('ofertas_actuales', [])
        
        if not ofertas:
            return {
                "answer": "En este momento no tenemos ofertas especiales, pero puedes consultar nuestros productos con los mejores precios siempre. 🛍️ ¿Te interesa alguna categoría en particular?",
                "confidence": 0.8
            }
        
        response = "**🎉 Nuestras ofertas actuales:**\n\n"
        for oferta in ofertas:
            response += f"• **{oferta['titulo']}**\n"
            response += f"  {oferta['descripcion']}\n"
            response += f"  Válido: {oferta.get('validez', 'Consultar términos')}\n\n"
        
        response += "¿Te interesa alguna oferta en particular? ¡Puedo darte más detalles! 😊"
        
        return {
            "answer": response.strip(),
            "confidence": 0.9,
            "category": "ofertas"
        }
    
    def _handle_price_query(self, question: str) -> Dict[str, Any]:
        """Maneja consultas sobre precios"""
        productos = self.data.get('productos', [])
        
        # Buscar productos mencionados en la pregunta
        mentioned_products = []
        for producto in productos:
            if any(word in question for word in producto['nombre'].lower().split()):
                mentioned_products.append(producto)
        
        if mentioned_products:
            producto = mentioned_products[0]  # Tomar el primero
            response = f"**{producto['nombre']}**\n\n"
            response += f"Precio: **S/{producto['precio']:.2f}**\n"
            response += f"Tallas disponibles: {', '.join(producto['tallas'])}\n"
            response += f"Colores: {', '.join(producto['colores'])}\n\n"
            response += "¿Te gustaría conocer más detalles o ver otros productos similares?"
            
            return {
                "answer": response,
                "confidence": 0.9,
                "category": "productos",
                "product_id": producto['id']
            }
        
        # Respuesta general sobre precios
        return {
            "answer": "Nuestros precios van desde S/39.90 hasta S/259.90 dependiendo del producto. ¿Sobre qué producto específico te gustaría conocer el precio? Puedo ayudarte con camisetas, pantalones, casacas y más.",
            "confidence": 0.7,
            "category": "productos"
        }
    
    def _handle_size_query(self, question: str) -> Dict[str, Any]:
        """Maneja consultas sobre tallas"""
        return {
            "answer": "**Guía de Tallas:**\n\n**Prendas superiores:** S, M, L, XL\n**Pantalones:** 28, 30, 32, 34, 36\n\nPara ayudarte mejor, ¿podrías decirme qué tipo de prenda te interesa? Tengo información detallada sobre medidas específicas para cada producto. También ofrecemos servicio de ajustes sin costo adicional.",
            "confidence": 0.8,
            "category": "productos"
        }
    
    def _handle_location_query(self) -> Dict[str, Any]:
        """Maneja consultas sobre ubicación"""
        return {
            "answer": "**📍 Nuestras tiendas:**\n\n**Tienda Principal**\nAv. Las Flores 123, Centro Comercial Plaza Mayor, Local 45, Lima\n\nFacilidades:\n• 🚗 Estacionamiento gratuito\n• ♿ Acceso para silla de ruedas\n• 👔 Probadores amplios\n• 📶 Wi-Fi gratuito\n\n¿Necesitas indicaciones específicas para llegar? 🗺️",
            "confidence": 0.9,
            "category": "tiendas"
        }
    
    def _handle_schedule_query(self) -> Dict[str, Any]:
        """Maneja consultas sobre horarios"""
        return {
            "answer": "**Horarios de atención:**\n\n**Lunes a Sábado:** 10:00 AM - 9:00 PM\n**Domingos:** 11:00 AM - 8:00 PM\n\n**Horario preferencial** (adultos mayores y personas con discapacidad):\n10:00 AM - 11:00 AM todos los días\n\n¿Hay algún servicio específico por el que consultas? Algunos servicios como sastrería tienen horarios especiales.",
            "confidence": 0.9,
            "category": "tiendas"
        }
    
    def _handle_returns_query(self) -> Dict[str, Any]:
        """Maneja consultas sobre devoluciones"""
        return {
            "answer": "**Política de Devoluciones:**\n\n**Plazos:**\n• Tienda física: 15 días\n• Compras online: 30 días\n\n**Requisitos:**\n• Ticket de compra\n• Prenda sin usar y con etiquetas\n• DNI del comprador\n\n**Reembolso:** En la misma forma de pago original\n**Proceso express:** Máximo 20 minutos en tienda\n\n¿Necesitas hacer una devolución específica? ¡Puedo guiarte paso a paso!",
            "confidence": 0.9,
            "category": "politicas"
        }
    
    def _search_faqs(self, question: str) -> Optional[Dict[str, Any]]:
        """Busca en las preguntas frecuentes"""
        faqs = self.data.get('faq', [])
        
        best_match = None
        best_score = 0
        
        for faq in faqs:
            # Calcular similitud con la pregunta
            score = calculate_text_similarity(question, faq['pregunta'].lower())
            
            # También buscar en palabras clave si existen
            if 'palabras_clave' in faq:
                for palabra in faq['palabras_clave']:
                    if palabra.lower() in question:
                        score += 0.3
            
            if score > best_score and score > 0.6:
                best_score = score
                best_match = faq
        
        if best_match:
            return {
                "answer": best_match['respuesta'],
                "confidence": min(0.95, best_score),
                "category": "faq",
                "source": "FAQ"
            }
        
        return None
    
    def _search_products(self, question: str) -> Optional[Dict[str, Any]]:
        """Busca productos relevantes"""
        productos = self.data.get('productos', [])
        
        matches = []
        for producto in productos:
            score = 0
            
            # Buscar en nombre
            if any(word in question for word in producto['nombre'].lower().split()):
                score += 0.5
            
            # Buscar en descripción
            if any(word in question for word in producto['descripcion'].lower().split()):
                score += 0.3
            
            # Buscar en etiquetas
            for etiqueta in producto.get('etiquetas', []):
                if etiqueta.lower() in question:
                    score += 0.4
            
            if score > 0.4:
                matches.append((score, producto))
        
        if matches:
            matches.sort(reverse=True, key=lambda x: x[0])
            best_product = matches[0][1]
            
            response = f"**{best_product['nombre']}**\n\n"
            response += f"{best_product['descripcion']}\n\n"
            response += f"Precio: **S/{best_product['precio']:.2f}**\n"
            response += f"Tallas: {', '.join(best_product['tallas'])}\n"
            response += f"Colores: {', '.join(best_product['colores'])}\n\n"
            response += "¿Te gustaría más información sobre este producto o ver otros similares?"
            
            return {
                "answer": response,
                "confidence": min(0.9, matches[0][0]),
                "category": "productos",
                "product_id": best_product['id']
            }
        
        return None
    
    def _generate_fallback_response(self, question: str) -> Dict[str, Any]:
        """Genera una respuesta de fallback inteligente"""
        fallback_responses = [
            "Interesante pregunta. Para ayudarte mejor, ¿podrías ser más específico? Por ejemplo, ¿buscas información sobre productos, precios, tallas o servicios?",
            "Me gustaría darte la mejor respuesta. ¿Podrías reformular tu pregunta? Puedo ayudarte con nuestro catálogo, ofertas, ubicación, horarios y más.",
            "¡Estoy aquí para ayudarte! ¿Te interesa consultar sobre alguno de estos temas: productos, ofertas, devoluciones, ubicación o horarios?"
        ]
        
        return {
            "answer": random.choice(fallback_responses),
            "confidence": 0.5,
            "category": "fallback",
            "suggestions": self.get_suggestions("", 3)
        }
    
    def get_suggestions(self, query: str = "", limit: int = 5) -> List[Dict[str, str]]:
        """Retorna sugerencias basadas en la consulta"""
        if not query:
            return random.sample(self.suggestions, min(limit, len(self.suggestions)))
        
        # Filtrar sugerencias relevantes
        query_lower = query.lower()
        filtered = [
            s for s in self.suggestions 
            if query_lower in s['text'].lower() or query_lower in s['category'].lower()
        ]
        
        if filtered:
            return filtered[:limit]
        
        # Si no hay coincidencias, retornar sugerencias aleatorias
        return random.sample(self.suggestions, min(limit, len(self.suggestions)))
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna el estado de salud del motor de chat"""
        return {
            "status": "healthy",
            "data_loaded": bool(self.data),
            "total_products": len(self.data.get('productos', [])),
            "total_faqs": len(self.data.get('faq', [])),
            "total_offers": len(self.data.get('ofertas_actuales', [])),
            "intent_processor_ready": self.intent_processor is not None,
            "stats": self.get_stats()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del motor de chat"""
        total = self.stats['total_questions']
        cache_hit_rate = (self.stats['cache_hits'] / total * 100) if total > 0 else 0
        success_rate = (self.stats['successful_responses'] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            'cache_hit_rate_percentage': round(cache_hit_rate, 2),
            'success_rate_percentage': round(success_rate, 2),
            'intent_stats': self.intent_processor.get_stats() if self.intent_processor else {}
        }