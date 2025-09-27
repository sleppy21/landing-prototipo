import random
from typing import Dict, List, Optional, Any

class IntentProcessor:
    """Procesador de intenciones completamente limpio sin caracteres especiales"""
    
    INTENCIONES = {
        'saludo': {
            'patrones': [
                'hola', 'buenos dias', 'buenas tardes', 'buenas noches',
                'hi', 'hello', 'que tal', 'saludos', 'hey', 'buenas'
            ],
            'respuestas': [
                "Hola! Soy tu asistente de Fashion Store. En que puedo ayudarte hoy?",
                "Bienvenido/a! Que estas buscando el dia de hoy?", 
                "Hola! Me alegra verte. Necesitas ayuda con algo en particular?"
            ]
        },
        'despedida': {
            'patrones': [
                'adios', 'chau', 'hasta luego', 'bye', 'gracias',
                'nos vemos', 'hasta pronto', 'goodbye'
            ],
            'respuestas': [
                "Hasta pronto! Fue un placer ayudarte. Vuelve cuando quieras!",
                "Gracias por tu visita! Si necesitas algo mas, aqui estare.",
                "Que tengas un excelente dia! Recuerda que estamos 24/7 para ti."
            ]
        },
        'precio': {
            'patrones': [
                'precio', 'cuanto cuesta', 'valor', 'costo', 'cuanto vale',
                'cuanto es', 'precios'
            ],
            'respuestas': [
                "Te puedo ayudar con precios! Que producto te interesa?",
                "Claro! Dime que articulo quieres consultar el precio.",
                "Perfecto! Cual es el producto que quieres conocer su precio?"
            ]
        },
        'stock': {
            'patrones': [
                'hay', 'tienen', 'disponible', 'stock', 'queda', 'talla',
                'disponibilidad', 'existe'
            ],
            'respuestas': [
                "Te ayudo a verificar disponibilidad! Que producto buscas?",
                "Claro! Dime que articulo y talla necesitas consultar.",
                "Perfecto! Cual es el producto que quieres verificar?"
            ]
        },
        'ubicacion': {
            'patrones': [
                'donde', 'ubicacion', 'direccion', 'tienda', 'local',
                'encuentro', 'como llego'
            ],
            'respuestas': [
                "Estamos en Av. Las Flores 123, Centro Comercial Plaza Mayor, Local 45, Lima.",
                "Nuestra direccion es Av. Las Flores 123, en Plaza Mayor. Tenemos estacionamiento gratuito!",
                "Nos encuentras en Plaza Mayor, Local 45. Horario de 10:00 AM a 9:00 PM."
            ]
        },
        'ofertas': {
            'patrones': [
                'ofertas', 'descuentos', 'promociones', 'oferta', 'descuento',
                'promocion', 'rebajas', 'liquidacion'
            ],
            'respuestas': [
                "Tenemos excelentes ofertas! Te muestro las promociones actuales.",
                "Perfecto! Aqui tienes nuestras mejores ofertas del momento.",
                "Genial! Te comparto las promociones disponibles ahora."
            ]
        }
    }

    @staticmethod
    def detectar_intencion(texto: str) -> Optional[str]:
        """Detecta la intencion del usuario basada en patrones simples"""
        texto_lower = texto.lower().strip()
        
        # Buscar coincidencias directas
        for intencion, data in IntentProcessor.INTENCIONES.items():
            for patron in data['patrones']:
                if patron in texto_lower:
                    return intencion
        
        return None

    @staticmethod
    def obtener_respuesta(intencion: str) -> str:
        """Obtiene una respuesta aleatoria para la intencion detectada"""
        if intencion and intencion in IntentProcessor.INTENCIONES:
            respuestas = IntentProcessor.INTENCIONES[intencion]['respuestas']
            return random.choice(respuestas)
        
        # Respuesta por defecto
        return "Hola! Como puedo ayudarte hoy? Puedo asistirte con productos, precios, ubicacion y mas."

    @staticmethod
    def procesar_mensaje(texto: str) -> Dict[str, Any]:
        """Procesa un mensaje completo y retorna la respuesta"""
        intencion = IntentProcessor.detectar_intencion(texto)
        respuesta = IntentProcessor.obtener_respuesta(intencion)
        
        return {
            'answer': respuesta,
            'intent': intencion or 'general',
            'confidence': 1.0 if intencion else 0.5
        }