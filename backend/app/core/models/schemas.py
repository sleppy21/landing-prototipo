"""
Modelos de datos para el Bot Asistente de Consultas
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class ProductCategory(str, Enum):
    """Categorías de productos"""
    CAMISETAS = "Camisetas"
    PANTALONES = "Pantalones"
    CASACAS = "Casacas"
    POLOS = "Polos"
    CAMISAS = "Camisas"
    SACOS = "Sacos"

class Product(BaseModel):
    """Modelo para productos"""
    id: str = Field(..., description="ID único del producto")
    nombre: str = Field(..., description="Nombre del producto")
    descripcion: str = Field(..., description="Descripción detallada")
    precio: float = Field(..., gt=0, description="Precio en soles")
    tallas: List[str] = Field(..., description="Tallas disponibles")
    colores: List[str] = Field(..., description="Colores disponibles")
    categoria: ProductCategory = Field(..., description="Categoría del producto")
    destacado: bool = Field(default=False, description="Producto destacado")
    etiquetas: List[str] = Field(default_factory=list, description="Etiquetas del producto")
    
    @validator('precio')
    def validate_precio(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return round(v, 2)

class FAQ(BaseModel):
    """Modelo para preguntas frecuentes"""
    pregunta: str = Field(..., description="Pregunta")
    respuesta: str = Field(..., description="Respuesta")
    categoria: str = Field(..., description="Categoría de la FAQ")
    palabras_clave: List[str] = Field(default_factory=list, description="Palabras clave")

class Offer(BaseModel):
    """Modelo para ofertas"""
    titulo: str = Field(..., description="Título de la oferta")
    descripcion: str = Field(..., description="Descripción de la oferta")
    validez: str = Field(..., description="Período de validez")
    condiciones: Optional[str] = Field(None, description="Condiciones de la oferta")
    exclusiones: Optional[str] = Field(None, description="Exclusiones")

class Policy(BaseModel):
    """Modelo para políticas"""
    tipo: str = Field(..., description="Tipo de política")
    descripcion: str = Field(..., description="Descripción de la política")
    detalles: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales")

class ChatMessage(BaseModel):
    """Modelo para mensajes del chat"""
    question: str = Field(..., min_length=1, description="Pregunta del usuario")
    
    @validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('La pregunta no puede estar vacía')
        return v.strip()

class ChatResponse(BaseModel):
    """Modelo para respuestas del chat"""
    answer: str = Field(..., description="Respuesta del bot")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Nivel de confianza")
    processing: bool = Field(default=False, description="Indica si el bot está procesando")
    error: Optional[str] = Field(None, description="Mensaje de error si existe")
    
class Intent(BaseModel):
    """Modelo para intenciones detectadas"""
    intencion: str = Field(..., description="Tipo de intención")
    similitud: float = Field(..., ge=0.0, le=1.0, description="Similitud detectada")
    data: Dict[str, Any] = Field(..., description="Datos de la intención")

class SearchResult(BaseModel):
    """Modelo para resultados de búsqueda"""
    score: float = Field(..., ge=0.0, le=1.0, description="Puntuación de relevancia")
    tipo: str = Field(..., description="Tipo de resultado")
    data: Dict[str, Any] = Field(..., description="Datos del resultado")

class SystemStatus(BaseModel):
    """Modelo para estado del sistema"""
    status: str = Field(..., description="Estado del sistema")
    model_loaded: bool = Field(..., description="Indica si el modelo está cargado")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del estado")