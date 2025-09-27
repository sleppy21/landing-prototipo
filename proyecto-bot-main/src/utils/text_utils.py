"""
Utilidades para procesamiento de texto en el Bot Asistente de Consultas
"""
import re
import difflib
from typing import List, Set
import unicodedata


def normalize_text(text: str) -> str:
    """
    Normaliza texto para mejor comparación y búsqueda
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if not text:
        return ""
    
    # Convertir a minúsculas
    text = text.lower().strip()
    
    # Normalizar caracteres Unicode (quitar acentos)
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    # Remover caracteres especiales excepto espacios y números
    text = re.sub(r'[^\w\s]', '', text)
    
    # Normalizar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calcula la similitud entre dos textos usando múltiples métricas
    
    Args:
        text1: Primer texto
        text2: Segundo texto
        
    Returns:
        Similitud entre 0.0 y 1.0
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalizar textos
    norm_text1 = normalize_text(text1)
    norm_text2 = normalize_text(text2)
    
    if norm_text1 == norm_text2:
        return 1.0
    
    # Similitud por secuencia
    sequence_similarity = difflib.SequenceMatcher(None, norm_text1, norm_text2).ratio()
    
    # Similitud por palabras comunes
    words1 = set(norm_text1.split())
    words2 = set(norm_text2.split())
    
    if not words1 or not words2:
        return sequence_similarity
    
    common_words = words1.intersection(words2)
    word_similarity = len(common_words) / max(len(words1), len(words2))
    
    # Similitud por substrings
    substring_similarity = 0.0
    for word1 in words1:
        for word2 in words2:
            if word1 in word2 or word2 in word1:
                substring_similarity += 0.1
    
    substring_similarity = min(1.0, substring_similarity)
    
    # Combinar métricas con pesos
    final_similarity = (
        sequence_similarity * 0.4 +
        word_similarity * 0.5 +
        substring_similarity * 0.1
    )
    
    return min(1.0, final_similarity)


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extrae palabras clave relevantes de un texto
    
    Args:
        text: Texto del cual extraer keywords
        min_length: Longitud mínima de las palabras
        
    Returns:
        Lista de palabras clave
    """
    # Palabras vacías en español
    stop_words = {
        'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le',
        'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como',
        'pero', 'sus', 'me', 'hasta', 'hay', 'donde', 'han', 'quien', 'están', 'estado',
        'desde', 'todo', 'nos', 'durante', 'todos', 'uno', 'les', 'ni', 'contra', 'otros',
        'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos',
        'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes',
        'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 'estas', 'algunas', 'algo', 'nosotros'
    }
    
    normalized_text = normalize_text(text)
    words = normalized_text.split()
    
    keywords = []
    for word in words:
        if (len(word) >= min_length and 
            word not in stop_words and 
            not word.isdigit()):
            keywords.append(word)
    
    # Remover duplicados manteniendo orden
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords


def highlight_matches(text: str, query: str, tag: str = "**") -> str:
    """
    Resalta las coincidencias de búsqueda en un texto
    
    Args:
        text: Texto donde buscar
        query: Términos a resaltar
        tag: Etiqueta para resaltar (por defecto markdown bold)
        
    Returns:
        Texto con coincidencias resaltadas
    """
    if not query or not text:
        return text
    
    query_words = extract_keywords(query)
    result_text = text
    
    for word in query_words:
        # Buscar coincidencias ignorando mayúsculas
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        result_text = pattern.sub(f"{tag}\\g<0>{tag}", result_text)
    
    return result_text


def truncate_text(text: str, max_length: int = 150, suffix: str = "...") -> str:
    """
    Trunca un texto a una longitud máxima manteniendo palabras completas
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
        
    Returns:
        Texto truncado
    """
    if not text or len(text) <= max_length:
        return text
    
    # Truncar en el último espacio antes del límite
    truncated = text[:max_length].rsplit(' ', 1)[0]
    
    # Si no se pudo truncar en un espacio, truncar directamente
    if len(truncated) < max_length * 0.8:  # Al menos 80% del límite
        truncated = text[:max_length - len(suffix)]
    
    return truncated + suffix


def format_price(price: float, currency: str = "S/") -> str:
    """
    Formatea un precio para mostrar
    
    Args:
        price: Precio numérico
        currency: Símbolo de moneda
        
    Returns:
        Precio formateado
    """
    return f"{currency}{price:.2f}"


def clean_html(text: str) -> str:
    """
    Limpia etiquetas HTML de un texto
    
    Args:
        text: Texto con posibles etiquetas HTML
        
    Returns:
        Texto limpio sin HTML
    """
    # Remover etiquetas HTML
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Normalizar espacios
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    return clean_text.strip()


def validate_email(email: str) -> bool:
    """
    Valida si un email tiene formato correcto
    
    Args:
        email: Email a validar
        
    Returns:
        True si es válido, False si no
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def extract_numbers(text: str) -> List[float]:
    """
    Extrae números de un texto
    
    Args:
        text: Texto del cual extraer números
        
    Returns:
        Lista de números encontrados
    """
    # Patrón para números decimales y enteros
    pattern = r'\d+(?:\.\d+)?'
    matches = re.findall(pattern, text)
    
    numbers = []
    for match in matches:
        try:
            if '.' in match:
                numbers.append(float(match))
            else:
                numbers.append(float(match))
        except ValueError:
            continue
    
    return numbers


def generate_slug(text: str, max_length: int = 50) -> str:
    """
    Genera un slug URL-friendly a partir de un texto
    
    Args:
        text: Texto original
        max_length: Longitud máxima del slug
        
    Returns:
        Slug generado
    """
    # Normalizar texto
    slug = normalize_text(text)
    
    # Reemplazar espacios con guiones
    slug = re.sub(r'\s+', '-', slug)
    
    # Remover caracteres no alfanuméricos excepto guiones
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    
    # Remover guiones múltiples
    slug = re.sub(r'-+', '-', slug)
    
    # Remover guiones al inicio y final
    slug = slug.strip('-')
    
    # Truncar si es necesario
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    return slug


def count_words(text: str) -> int:
    """
    Cuenta las palabras en un texto
    
    Args:
        text: Texto a analizar
        
    Returns:
        Número de palabras
    """
    if not text:
        return 0
    
    normalized = normalize_text(text)
    words = normalized.split()
    
    return len(words)


def fuzzy_match(query: str, choices: List[str], threshold: float = 0.6) -> List[tuple]:
    """
    Encuentra coincidencias difusas en una lista de opciones
    
    Args:
        query: Texto a buscar
        choices: Lista de opciones donde buscar
        threshold: Umbral mínimo de similitud
        
    Returns:
        Lista de tuplas (choice, similarity_score)
    """
    if not query or not choices:
        return []
    
    matches = []
    normalized_query = normalize_text(query)
    
    for choice in choices:
        normalized_choice = normalize_text(choice)
        similarity = calculate_text_similarity(normalized_query, normalized_choice)
        
        if similarity >= threshold:
            matches.append((choice, similarity))
    
    # Ordenar por similitud descendente
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches