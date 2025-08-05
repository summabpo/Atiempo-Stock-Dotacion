from django.utils.text import slugify

ABREVIATURAS_CIUDADES = {
    'bta': 'Bogotá',
    'bogota': 'Bogotá',
    'bogotá': 'Bogotá',
    'bog': 'Bogotá',
    'med': 'Medellín',
    'medellin': 'Medellín',
    'medellín': 'Medellín',
    'bquilla': 'Barranquilla',
    'barranquilla': 'Barranquilla',
    'barranq': 'Barranquilla',
    'cali': 'Cali',
    'cartagena': 'Cartagena',
    'ctg': 'Cartagena',
    'bucaramanga': 'Bucaramanga',
    'bucara': 'Bucaramanga',
    'pereira': 'Pereira',
    'manizales': 'Manizales',
    'neiva': 'Neiva',
    'villavo': 'Villavicencio',
    'villavicencio': 'Villavicencio',
    'santa marta': 'Santa Marta',
    'stmarta': 'Santa Marta',
    'armenia': 'Armenia',
    'ibague': 'Ibagué',
    'ibagué': 'Ibagué',
    'pasto': 'Pasto',
    'cúcuta': 'Cúcuta',
    'cucuta': 'Cúcuta',
    'popayan': 'Popayán',
    'popayán': 'Popayán',
}

def normalizar_ciudad(nombre):
    clave = slugify(nombre).replace('-', '')
    return ABREVIATURAS_CIUDADES.get(clave, nombre.title().strip())