import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import difflib
import re
from sentence_transformers import SentenceTransformer
import numpy as np
import torch

# Obtener la ruta del directorio de datos
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data' / 'context'

class IntentProcessor:
 """Procesa y maneja las intenciones del usuario"""

 INTENCIONES = {
 'saludo': {
 'patrones': [
 'hola', 'buenos días', 'buenas tardes', 'buenas noches',
 'hi', 'que tal', 'saludos', 'hey', 'buenas'
 ],
 'respuestas': [
 "Hola! Soy tu asistente de Fashion Store. En que puedo ayudarte hoy?",
 "Bienvenido/a! Que estas buscando el dia de hoy?",
 "Hola! Me alegra verte. Necesitas ayuda con algo en particular?"
 ],
 'prioridad': 1
 },
 'despedida': {
 'patrones': [
 'adios', 'chau', 'hasta luego', 'bye', 'gracias', 
 'nos vemos', 'hasta pronto', 'adiós'
 ],
 'respuestas': [
 "Hasta pronto! Fue un placer ayudarte. Vuelve cuando quieras!",
 "Gracias por tu visita! Si necesitas algo mas, aqui estare.",
 "Que tengas un excelente dia! Recuerda que estamos 24/7 para ti."
 ],
 'prioridad': 1
 },
 'continuar': {
 'patrones': [
 '@agent continuar', '@agent Continuar', 'continuar', 'seguir',
 'desea continuar', 'quiere continuar', 'sigue', 'más'
 ],
 'respuestas': [
 "Por supuesto! Continuemos con nuestra conversacion. En que estabamos?",
 "Claro! Sigo aqui para ayudarte. Que mas necesitas saber?",
 "Adelante! En que mas puedo ayudarte?"
 ],
 'prioridad': 1
 },
 'consultaPrecio': {
 'patrones': [
 'precio', 'cuanto cuesta', 'valor', 'costo', 'cuanto vale',
 'cuanto es', 'precios', 'cuánto', 'vale'
 ],
 'contexto_requerido': ['productos', 'ofertas']
 },
 'consultaStock': {
 'patrones': [
 'hay', 'tienen', 'disponible', 'stock', 'queda', 'talla',
 'disponibilidad', 'existe', 'tengo'
 ],
 'contexto_requerido': ['productos']
 },
 'consultaUbicacion': {
 'patrones': [
 'donde', 'ubicacion', 'direccion', 'tienda', 'local',
 'ubicación', 'dirección', 'encuentro'
 ],
 'contexto_requerido': ['tiendas']
 },
 'consultaOfertas': {
 'patrones': [
 'ofertas', 'descuentos', 'promociones', 'oferta', 'descuento',
 'promoción', 'rebajas', 'liquidación', 'ver ofertas'
 ],
 'contexto_requerido': ['ofertas']
 }
 }

 @staticmethod
 def detectar_intencion(texto: str) -> Optional[Dict[str, Any]]:
 texto = texto.lower().strip()
 mejor_match = None
 max_similitud = 0

 for intencion, data in IntentProcessor.INTENCIONES.items():
 for patron in data['patrones']:
 # Búsqueda exacta primero
 if patron in texto:
 similitud = 1.0 if patron == texto else 0.8
 else:
 # Similitud por difflib
 similitud = difflib.SequenceMatcher(None, texto, patron).ratio()

 if similitud > max_similitud and similitud > 0.5:
 max_similitud = similitud
 mejor_match = {'intencion': intencion, 'data': data, 'similitud': similitud}

 return mejor_match

class ContextProcessor:
 """Procesa y selecciona el contexto relevante"""

 def __init__(self, context_data: Dict[str, Any]):
 self.context_data = context_data
 self.cached_embeddings = {}

 def get_context_for_query(self, query: str, intent: Optional[Dict[str, Any]] = None) -> str:
 """Selecciona y formatea el contexto más relevante para la consulta"""
 relevant_sections = []
 query_lower = query.lower()

 # Si hay una intención detectada, priorizar su contexto requerido
 if intent and 'contexto_requerido' in intent['data']:
 for context_type in intent['data']['contexto_requerido']:
 relevant_sections.extend(self._get_context_by_type(context_type, query_lower))
 else:
 # Búsqueda general en todo el contexto
 for context_type in ['productos', 'ofertas', 'tiendas', 'faqs']:
 relevant_sections.extend(self._get_context_by_type(context_type, query_lower))

 # Ordenar por relevancia y limitar el contexto
 relevant_sections = sorted(relevant_sections, key=lambda x: x['score'], reverse=True)[:3]
 return "\n\n".join(section['text'] for section in relevant_sections)

 def _get_context_by_type(self, context_type: str, query: str) -> List[Dict[str, Any]]:
 """Obtiene contexto específico según el tipo"""
 sections = []

 if context_type == 'productos':
 # Corregir acceso a productos - ahora accede directamente a la lista
 productos = self.context_data.get('productos', [])
 for producto in productos:
 score = self._calculate_relevance(query, producto)
 if score > 0.2:
 sections.append({
 'text': self._format_product(producto),
 'score': score
 })

 elif context_type == 'ofertas':
 # Corregir acceso a ofertas
 ofertas = self.context_data.get('ofertas_actuales', [])
 for oferta in ofertas:
 score = self._calculate_relevance(query, oferta)
 if score > 0.2:
 sections.append({
 'text': self._format_offer(oferta),
 'score': score
 })

 elif context_type == 'faqs':
 # Añadir manejo de FAQs
 faqs = self.context_data.get('faq', [])
 for faq in faqs:
 score = self._calculate_relevance(query, faq)
 if score > 0.2:
 sections.append({
 'text': self._format_faq(faq),
 'score': score
 })

 return sections

 def _calculate_relevance(self, query: str, item: Dict[str, Any]) -> float:
 """Calcula la relevancia de un item para la consulta"""
 relevance = 0.0
 query_words = set(query.lower().split())

 # Comparar con diferentes campos según el tipo de item
 for key, value in item.items():
 if isinstance(value, str):
 item_words = set(value.lower().split())
 common_words = query_words.intersection(item_words)
 relevance += len(common_words) * 0.3
 elif isinstance(value, list):
 for v in value:
 if isinstance(v, str):
 item_words = set(v.lower().split())
 common_words = query_words.intersection(item_words)
 relevance += len(common_words) * 0.2

 return min(1.0, relevance)

 @staticmethod
 def _format_product(product: Dict[str, Any]) -> str:
 """Formatea la información de un producto"""
 return f"""
PRODUCTO: {product['nombre']}
Descripción: {product['descripcion']}
Precio: S/{float(product['precio']):.2f}
Tallas: {', '.join(product['tallas'])}
Colores: {', '.join(product['colores'])}
Categoría: {product.get('categoria', 'General')}
Etiquetas: {', '.join(product.get('etiquetas', []))}
"""

 @staticmethod
 def _format_offer(offer: Dict[str, Any]) -> str:
 """Formatea la información de una oferta"""
 return f"""
OFERTA: {offer['titulo']}
{offer['descripcion']}
Válido: {offer.get('validez', 'Consultar en tienda')}
Condiciones: {offer.get('condiciones', offer.get('exclusiones', 'Ver términos y condiciones'))}
"""

 @staticmethod
 def _format_faq(faq: Dict[str, Any]) -> str:
 """Formatea la información de una FAQ"""
 return f"""
PREGUNTA: {faq['pregunta']}
RESPUESTA: {faq['respuesta']}
"""

class VectorProcessor:
 def __init__(self):
 try:
 # Usar un modelo más liviano y rápido
 self.model = SentenceTransformer('all-MiniLM-L6-v2')
 self.data = self._load_data()
 self.vectors = {}
 if self.data:
 self.initialize_vectors()
 except Exception as e:
 print(f"Error inicializando VectorProcessor: {e}")
 self.model = None
 self.data = {}
 self.vectors = {}

 def _load_data(self) -> Dict:
 """Carga todos los datos del catálogo"""
 try:
 with open("data/catalogue.json", "r", encoding="utf-8") as f:
 return json.load(f)
 except Exception as e:
 print(f"Error cargando datos: {e}")
 return {}

 def initialize_vectors(self):
 """Inicializa los vectores para todos los elementos del catálogo - VERSIÓN MEJORADA"""
 if not self.model:
 return

 try:
 # Vectorizar productos con más detalle
 for producto in self.data.get("productos", []):
 # Texto principal del producto
 texto_principal = f"{producto['nombre']} {producto['descripcion']} {producto.get('categoria', '')}"
 self.vectors[f"producto_{producto['id']}"] = {
 "vector": self.get_embedding(texto_principal),
 "data": producto,
 "tipo": "producto"
 }

 # Vectores adicionales por características específicas
 # Vector para precio/costo
 texto_precio = f"precio costo valor {producto['nombre']} {producto['precio']} soles"
 self.vectors[f"producto_precio_{producto['id']}"] = {
 "vector": self.get_embedding(texto_precio),
 "data": producto,
 "tipo": "producto"
 }

 # Vector para tallas
 texto_tallas = f"tallas disponibles {producto['nombre']} {' '.join(producto['tallas'])}"
 self.vectors[f"producto_tallas_{producto['id']}"] = {
 "vector": self.get_embedding(texto_tallas),
 "data": producto,
 "tipo": "producto"
 }

 # Vector para colores
 texto_colores = f"colores disponibles {producto['nombre']} {' '.join(producto['colores'])}"
 self.vectors[f"producto_colores_{producto['id']}"] = {
 "vector": self.get_embedding(texto_colores),
 "data": producto,
 "tipo": "producto"
 }

 # Vector para etiquetas
 if producto.get('etiquetas'):
 texto_etiquetas = f"{producto['nombre']} {' '.join(producto['etiquetas'])}"
 self.vectors[f"producto_etiquetas_{producto['id']}"] = {
 "vector": self.get_embedding(texto_etiquetas),
 "data": producto,
 "tipo": "producto"
 }

 # Vectorizar FAQs con variaciones
 for i, faq in enumerate(self.data.get("faq", [])):
 # Texto principal FAQ
 texto = f"{faq['pregunta']} {faq['respuesta']}"
 self.vectors[f"faq_{i}"] = {
 "vector": self.get_embedding(texto),
 "data": faq,
 "tipo": "faq"
 }

 # Vector solo para la pregunta (para mejor matching)
 self.vectors[f"faq_pregunta_{i}"] = {
 "vector": self.get_embedding(faq['pregunta']),
 "data": faq,
 "tipo": "faq"
 }

 # Vector por categoría
 if faq.get('categoria'):
 texto_categoria = f"{faq['categoria']} {faq['pregunta']}"
 self.vectors[f"faq_categoria_{i}"] = {
 "vector": self.get_embedding(texto_categoria),
 "data": faq,
 "tipo": "faq"
 }

 # Vectorizar ofertas con más contexto
 for i, oferta in enumerate(self.data.get("ofertas_actuales", [])):
 # Texto principal oferta
 texto = f"oferta descuento promoción {oferta['titulo']} {oferta['descripcion']}"
 self.vectors[f"oferta_{i}"] = {
 "vector": self.get_embedding(texto),
 "data": oferta,
 "tipo": "oferta"
 }

 # Vector específico para búsqueda de ofertas
 texto_busqueda = f"ver ofertas promociones descuentos {oferta['titulo']}"
 self.vectors[f"oferta_busqueda_{i}"] = {
 "vector": self.get_embedding(texto_busqueda),
 "data": oferta,
 "tipo": "oferta"
 }

 # Vectorizar políticas con más detalle
 for i, politica in enumerate(self.data.get("politicas", [])):
 # Texto principal política
 texto = f"política {politica['tipo']} {politica['descripcion']}"
 self.vectors[f"politica_{i}"] = {
 "vector": self.get_embedding(texto),
 "data": politica,
 "tipo": "politica"
 }

 # Vector por tipo específico
 texto_tipo = f"{politica['tipo']} información servicio"
 self.vectors[f"politica_tipo_{i}"] = {
 "vector": self.get_embedding(texto_tipo),
 "data": politica,
 "tipo": "politica"
 }

 # Vectores adicionales para consultas comunes
 consultas_comunes = [
 {"texto": "horarios atención horario atencion cuando abren cierran", "tipo": "horario", "respuesta": "Nuestro horario de atención es: Lunes a Sábado de 10:00 AM a 9:00 PM y Domingos de 11:00 AM a 8:00 PM. En fechas especiales puede haber variaciones."},
 {"texto": "ubicación dirección donde están ubicados como llegar", "tipo": "ubicacion", "respuesta": "Estamos ubicados en Av. Las Flores 123, Centro Comercial Plaza Mayor, Local 45, Lima. Contamos con estacionamiento gratuito y acceso para personas con movilidad reducida."},
 {"texto": "métodos pago formas pagar tarjetas efectivo", "tipo": "pagos", "respuesta": "Aceptamos todas las tarjetas de crédito/débito, efectivo, transferencias bancarias, Yape, Plin y PayPal. También ofrecemos cuotas sin intereses en tarjetas seleccionadas."},
 {"texto": "cambios devoluciones devolver cambiar talla", "tipo": "cambios", "respuesta": "Realizamos cambios y devoluciones dentro de los 15 días (30 días online) presentando el ticket y la prenda con etiquetas en estado original."},
 {"texto": "envíos delivery despacho enviar pedido", "tipo": "envios", "respuesta": "Envío gratis en compras mayores a S/150. Tiempos: 24-48h en Lima, 2-4 días provincias. Seguimiento en tiempo real disponible."}
 ]

 for i, consulta in enumerate(consultas_comunes):
 self.vectors[f"consulta_comun_{i}"] = {
 "vector": self.get_embedding(consulta["texto"]),
 "data": {"respuesta": consulta["respuesta"], "tipo": consulta["tipo"]},
 "tipo": "consulta_comun"
 }

 print(f"Vectores inicializados: {len(self.vectors)} elementos")
 except Exception as e:
 print(f"Error en initialize_vectors: {e}")

 def get_embedding(self, text: str) -> np.ndarray:
 """Obtiene el embedding de un texto"""
 if not self.model:
 return np.array([])
 try:
 return self.model.encode(text)
 except Exception as e:
 print(f"Error obteniendo embedding: {e}")
 return np.array([])

 def semantic_search(self, query: str, top_k: int = 3) -> List[Dict]:
 """Realiza una búsqueda semántica y devuelve los resultados más relevantes"""
 if not self.model or not self.vectors:
 return []

 try:
 query_vector = self.get_embedding(query)
 if query_vector.size == 0:
 return []

 # Calcular similitud con todos los vectores
 similarities = []
 for key, item in self.vectors.items():
 if item["vector"].size > 0:
 similarity = self.cosine_similarity(query_vector, item["vector"])
 similarities.append((similarity, key, item))

 # Ordenar por similitud y obtener los top_k
 similarities.sort(reverse=True, key=lambda x: x[0])
 results = []

 for similarity, key, item in similarities[:top_k]:
 if similarity < 0.3: # Umbral mínimo de similitud
 continue

 result = {
 "score": float(similarity),
 "tipo": item["tipo"],
 "data": item["data"]
 }
 results.append(result)

 return results
 except Exception as e:
 print(f"Error en búsqueda semántica: {e}")
 return []

 def cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
 """Calcula la similitud del coseno entre dos vectores"""
 try:
 return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
 except:
 return 0.0

 def generate_response(self, query: str) -> Dict[str, Any]:
 """Genera una respuesta basada en la búsqueda semántica - VERSIÓN MEJORADA"""
 if not self.model:
 return None

 results = self.semantic_search(query, top_k=5) # Aumentar resultados para mejor análisis

 if not results:
 return None

 best_match = results[0]
 response = ""

 # Manejar consultas comunes específicas
 if best_match["tipo"] == "consulta_comun":
 return {
 "answer": best_match["data"]["respuesta"],
 "confidence": float(best_match["score"])
 }

 # Manejar ofertas específicamente - MEJORADO
 if any(word in query.lower() for word in ['ofertas', 'oferta', 'descuento', 'promocion', 'ver ofertas', 'rebajas', 'liquidación']):
 ofertas_encontradas = [r for r in results if r["tipo"] == "oferta"]

 if ofertas_encontradas:
 response = " **Ofertas disponibles:**\n\n"
 for oferta in ofertas_encontradas:
 data = oferta["data"]
 response += f"• **{data['titulo']}**\n"
 response += f" {data['descripcion']}\n"
 response += f" Válido: {data.get('validez', 'Consultar términos')}\n\n"
 else:
 # Mostrar todas las ofertas si no hay coincidencias específicas
 response = " **Nuestras ofertas actuales:**\n\n"
 for oferta in self.data.get("ofertas_actuales", []):
 response += f"• **{oferta['titulo']}**\n"
 response += f" {oferta['descripcion']}\n"
 response += f" Válido: {oferta.get('validez', 'Consultar términos')}\n\n"

 return {"answer": response.strip(), "confidence": 0.9}

 # Manejar productos - MEJORADO
 if best_match["tipo"] == "producto":
 data = best_match["data"]
 response = f" **{data['nombre']}**\n\n"
 response += f"{data['descripcion']}\n\n"
 response += f" **Precio:** S/{data['precio']:.2f}\n"
 response += f" **Tallas disponibles:** {', '.join(data['tallas'])}\n"
 response += f" **Colores:** {', '.join(data['colores'])}\n"

 if data.get('categoria'):
 response += f" **Categoría:** {data['categoria']}\n"

 if data.get('etiquetas'):
 response += f" **Características:** {', '.join(data['etiquetas'])}"

 # Manejar FAQs - MEJORADO
 elif best_match["tipo"] == "faq":
 data = best_match["data"]
 response = f" **{data['pregunta']}**\n\n"
 response += f"{data['respuesta']}"

 if data.get('categoria'):
 response += f"\n\n *Categoría: {data['categoria']}*"

 # Manejar políticas - MEJORADO
 elif best_match["tipo"] == "politica":
 data = best_match["data"]
 response = f" **{data['tipo']}**\n\n"
 response += f"{data['descripcion']}"

 if "detalles" in data:
 response += "\n\n** Detalles importantes:**"
 detalles = data["detalles"]

 for key, value in detalles.items():
 if isinstance(value, dict):
 response += f"\n\n• **{key.title()}:**"
 for subkey, subvalue in value.items():
 response += f"\n - {subkey.title()}: {subvalue}"
 elif isinstance(value, list):
 response += f"\n• **{key.title()}:** {', '.join(value)}"
 else:
 response += f"\n• **{key.title()}:** {value}"

 if "iniciativas" in data:
 response += f"\n\n **Iniciativas:** {', '.join(data['iniciativas'])}"

 # Agregar sugerencias inteligentes basadas en otros resultados
 if len(results) > 1:
 sugerencias = []
 tipos_vistos = {best_match["tipo"]}

 for r in results[1:3]: # Solo los siguientes 2 mejores resultados
 if r["tipo"] not in tipos_vistos and r["score"] > 0.4:
 tipos_vistos.add(r["tipo"])

 if r["tipo"] == "producto":
 sugerencias.append(f"Ver detalles de **{r['data']['nombre']}**")
 elif r["tipo"] == "oferta":
 sugerencias.append(f"Conocer la oferta: **{r['data']['titulo']}**")
 elif r["tipo"] == "faq":
 sugerencias.append(f"Consultar: *{r['data']['pregunta'][:50]}...*")
 elif r["tipo"] == "politica":
 sugerencias.append(f"Información sobre **{r['data']['tipo']}**")

 if sugerencias:
 response += "\n\n **También podrías consultar:**\n"
 response += "\n".join(f"• {s}" for s in sugerencias[:2])

 # Agregar call-to-action contextual
 if best_match["tipo"] == "producto":
 response += "\n\n *¿Te gustaría conocer más detalles, ver otras tallas o consultar ofertas disponibles?*"
 elif best_match["tipo"] == "oferta":
 response += "\n\n *¿Quieres ver los productos incluidos en esta oferta?*"
 elif best_match["tipo"] == "politica" and "devoluc" in query.lower():
 response += "\n\n *¿Necesitas hacer una devolución o cambio específico?*"

 return {
 "answer": response,
 "confidence": float(best_match["score"])
 }

class BackendProcessor:
 def __init__(self, data):
 self.data = data
 self.cache = {}

 def process_query(self, query, context=None):
 """Procesa una consulta y retorna la respuesta más relevante"""
 try:
 # Normalizar la consulta
 query = query.lower().strip()

 # Verificar caché
 if query in self.cache:
 return self.cache[query]

 # Buscar en productos
 if any(word in query for word in ['producto', 'precio', 'talla', 'color']):
 response = self._search_products(query)
 if response:
 self.cache[query] = response
 return response

 # Buscar en ofertas
 if any(word in query for word in ['oferta', 'descuento', 'promoción']):
 response = self._search_offers(query)
 if response:
 self.cache[query] = response
 return response

 # Buscar en políticas
 if any(word in query for word in ['política', 'devolución', 'envío', 'garantía']):
 response = self._search_policies(query)
 if response:
 self.cache[query] = response
 return response

 # Fallback a FAQ
 response = self._search_faq(query)
 if response:
 self.cache[query] = response
 return response

 return {
 "answer": "Lo siento, no encontré información específica. ¿Podrías reformular tu pregunta? ",
 "confidence": 0.3
 }

 except Exception as e:
 return {
 "answer": "Ocurrió un error procesando tu consulta. Por favor, intenta de nuevo.",
 "error": str(e),
 "confidence": 0.1
 }

 def _search_products(self, query):
 """Busca en el catálogo de productos"""
 productos = self.data.get('productos', [])
 matches = []

 # Buscar por palabras clave
 keywords = query.split()
 for producto in productos:
 score = 0
 for keyword in keywords:
 if keyword in producto['nombre'].lower():
 score += 3
 if keyword in producto['descripcion'].lower():
 score += 2
 if keyword in ' '.join(producto['etiquetas']).lower():
 score += 1
 if score > 0:
 matches.append((score, producto))

 if matches:
 # Ordenar por relevancia
 matches.sort(reverse=True, key=lambda x: x[0])
 best_match = matches[0][1]

 # Formar respuesta
 response = f"{best_match['nombre']}: {best_match['descripcion']}\n"
 response += f"Precio: S/{best_match['precio']:.2f}\n"
 response += f"Tallas disponibles: {', '.join(best_match['tallas'])}\n"
 response += f"Colores: {', '.join(best_match['colores'])} "

 return {
 "answer": response,
 "confidence": min(0.9, matches[0][0] / len(keywords)),
 "product_id": best_match['id']
 }
 return None

 def _search_offers(self, query):
 """Busca en las ofertas actuales"""
 ofertas = self.data.get('ofertas_actuales', [])
 if not ofertas:
 return None

 response = " Estas son nuestras ofertas actuales:\n\n"
 for oferta in ofertas:
 response += f"• {oferta['titulo']}\n"
 response += f" {oferta['descripcion']}\n"
 response += f" Válido: {oferta['validez']}\n\n"

 return {
 "answer": response.strip(),
 "confidence": 0.8
 }

 def _search_policies(self, query):
 """Busca en las políticas de la tienda"""
 politicas = self.data.get('politicas', [])
 matches = []

 keywords = query.split()
 for politica in politicas:
 score = 0
 for keyword in keywords:
 if keyword in politica['tipo'].lower():
 score += 3
 if keyword in politica['descripcion'].lower():
 score += 2
 if score > 0:
 matches.append((score, politica))

 if matches:
 matches.sort(reverse=True, key=lambda x: x[0])
 best_match = matches[0][1]

 response = f" {best_match['tipo']}:\n{best_match['descripcion']}"

 if 'detalles' in best_match:
 response += "\n\nDetalles importantes:"
 for key, value in best_match['detalles'].items():
 if isinstance(value, list):
 response += f"\n• {key.title()}: {', '.join(value)}"
 else:
 response += f"\n• {key.title()}: {value}"

 return {
 "answer": response,
 "confidence": min(0.9, matches[0][0] / len(keywords))
 }
 return None

 def _search_faq(self, query):
 """Busca en las preguntas frecuentes"""
 faqs = self.data.get('faq', [])
 matches = []

 keywords = query.split()
 for faq in faqs:
 score = 0
 for keyword in keywords:
 if keyword in faq['pregunta'].lower():
 score += 3
 if keyword in faq['respuesta'].lower():
 score += 1
 if score > 0:
 matches.append((score, faq))

 if matches:
 matches.sort(reverse=True, key=lambda x: x[0])
 best_match = matches[0][1]

 return {
 "answer": best_match['respuesta'],
 "confidence": min(0.9, matches[0][0] / len(keywords))
 }
 return None

# Cargar el contexto al iniciar
try:
 context_data = {}
 for json_file in DATA_DIR.glob('*.json'):
 with open(json_file, 'r', encoding='utf-8') as f:
 context_data[json_file.stem] = json.load(f)

 # Inicializar procesadores
 intent_processor = IntentProcessor()
 context_processor = ContextProcessor(context_data)
except Exception as e:
 print(f"Error cargando archivos de contexto: {e}")
 context_data = {}