import re
from typing import List, Tuple, Set

class AnalizadorLexico:
    def __init__(self, ruta_diccionario: str):
        self.diccionario_palabras_validas: Set[str] = self._cargar_diccionario(ruta_diccionario)

        self.ER_PALABRA_BASICA = re.compile(r'^[a-záéíóúüñ]+$')
        self.ER_PUNTUACION = re.compile(r'^[.,;:¿?¡!]+$')
        self.ER_DIGITO = re.compile(r'^\d+$')
    
    def _cargar_diccionario(self, ruta: str) -> Set[str]:
        palabras = set()
        try:
            with open(ruta, 'r', encoding='utf-8') as archivo:
                for linea in archivo:
                    palabra = linea.strip().lower().split(',')[0] 
                    if palabra:
                        palabras.add(palabra)
            print(f"Diccionario cargado: {len(palabras)} palabras")
        except FileNotFoundError:
            print(f"Advertencia: No se encontró el archivo '{ruta}'")
        return palabras
    
    def _preprocesar_texto(self, texto: str) -> List[str]:
        texto = texto.lower()

        patron = r'([a-záéíóúüñ]+|[.,;:¿?¡!]+|\d+)'
        lexemas = re.findall(patron, texto)
        
        return lexemas
    
    def _clasificar_lexema(self, lexema: str) -> str:
        if lexema in self.diccionario_palabras_validas:
            return "PALABRA_VALIDA_ESPANOL"

        if self.ER_PUNTUACION.match(lexema):
            return "PUNTUACION"

        if self.ER_DIGITO.match(lexema):
            return "DIGITO"

        return "ERROR_ORTOGRAFICO"
    
    def analizar_texto(self, texto: str) -> List[Tuple[str, str]]:
        lexemas = self._preprocesar_texto(texto)
        
        tokens = []
        for lexema in lexemas:
            tipo_token = self._clasificar_lexema(lexema)
            tokens.append((tipo_token, lexema))
        
        return tokens
    
    def analizar_archivo(self, ruta_entrada: str, ruta_salida: str):
        try:
            with open(ruta_entrada, 'r', encoding='utf-8') as archivo:
                texto = archivo.read()
            
            tokens = self.analizar_texto(texto)
            
            self._generar_salida(tokens, ruta_salida)
        
            self._mostrar_estadisticas(tokens)
            
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo '{ruta_entrada}'")
    
    def _generar_salida(self, tokens: List[Tuple[str, str]], ruta_salida: str):
        with open(ruta_salida, 'w', encoding='utf-8') as archivo:
            archivo.write(f"{'Token':<30} {'Lexema':<20}\n")
            
            for tipo_token, lexema in tokens:
                archivo.write(f"{tipo_token:<30} {lexema:<20}\n")
        
        print(f"Archivo generado: {ruta_salida}")
    
    def _mostrar_estadisticas(self, tokens: List[Tuple[str, str]]):
        total = len(tokens)
        validas = sum(1 for t, _ in tokens if t == "PALABRA_VALIDA_ESPANOL")
        errores = sum(1 for t, _ in tokens if t == "ERROR_ORTOGRAFICO")
        digitos = sum(1 for t, _ in tokens if t == "DIGITO")
        puntuacion = sum(1 for t, _ in tokens if t == "PUNTUACION")

        print("ESTADÍSTICAS DEL ANÁLISIS")
        print(f"Total de tokens:        {total}")
        print(f"Palabras válidas:       {validas}")
        print(f"Errores ortográficos:   {errores}")
        print(f"Dígitos:                {digitos}")
        print(f"Puntuación:             {puntuacion}")

def main():
    print("ANALIZADOR LÉXICO - ESPAÑOL")
    analizador = AnalizadorLexico('diccionario_espanol.txt')

    analizador.analizar_archivo('texto_entrada.txt', 'tokens_salida.txt')


if __name__ == "__main__":
    main()