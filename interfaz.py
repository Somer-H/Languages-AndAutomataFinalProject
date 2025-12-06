import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
from typing import List, Tuple, Set

class AnalizadorLexico:
    def __init__(self):
        self.diccionario_palabras_validas: Set[str] = set()
        self.ER_PALABRA_BASICA = re.compile(r'^[a-záéíóúüñ]+$')
        self.ER_PUNTUACION = re.compile(r'^[.,;:¿?¡!]+$')
        self.ER_DIGITO = re.compile(r'^\d+$')
    
    def cargar_diccionario(self, ruta: str) -> Tuple[bool, str]:
        palabras = set()
        try:
            with open(ruta, 'r', encoding='utf-8') as archivo:
                for linea in archivo:
                    palabra = linea.strip().lower().split(',')[0] 
                    if palabra:
                        palabras.add(palabra)
            self.diccionario_palabras_validas = palabras
            return True, f"Diccionario cargado: {len(palabras)} palabras"
        except FileNotFoundError:
            return False, f"Error: No se encontró el archivo '{ruta}'"
        except Exception as e:
            return False, f"Error al cargar diccionario: {str(e)}"
    
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
    
    def obtener_estadisticas(self, tokens: List[Tuple[str, str]]) -> dict:
        total = len(tokens)
        validas = sum(1 for t, _ in tokens if t == "PALABRA_VALIDA_ESPANOL")
        errores = sum(1 for t, _ in tokens if t == "ERROR_ORTOGRAFICO")
        digitos = sum(1 for t, _ in tokens if t == "DIGITO")
        puntuacion = sum(1 for t, _ in tokens if t == "PUNTUACION")
        return {
            "total": total,
            "validas": validas,
            "errores": errores,
            "digitos": digitos,
            "puntuacion": puntuacion
        }


class InterfazAnalizador:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Léxico - Español")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        self.analizador = AnalizadorLexico()
        self.diccionario_cargado = False
        
        self.crear_widgets()
    
    def crear_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="ANALIZADOR LÉXICO - ESPAÑOL", 
                          font=("Helvetica", 16, "bold"))
        titulo.pack(pady=10)
        
        # Frame para cargar diccionario
        frame_diccionario = ttk.LabelFrame(main_frame, text="1. Cargar Diccionario", padding="10")
        frame_diccionario.pack(fill=tk.X, pady=5)
        
        self.btn_cargar_diccionario = ttk.Button(frame_diccionario, 
                                                  text="Seleccionar diccionario_espanol.txt",
                                                  command=self.cargar_diccionario)
        self.btn_cargar_diccionario.pack(side=tk.LEFT, padx=5)
        
        self.lbl_estado_diccionario = ttk.Label(frame_diccionario, text="No se ha cargado ningún diccionario",
                                                 foreground="orange")
        self.lbl_estado_diccionario.pack(side=tk.LEFT, padx=10)
        
        # Frame para texto de entrada
        frame_entrada = ttk.LabelFrame(main_frame, text="2. Texto de Entrada", padding="10")
        frame_entrada.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botones para entrada
        frame_botones_entrada = ttk.Frame(frame_entrada)
        frame_botones_entrada.pack(fill=tk.X, pady=5)
        
        self.btn_cargar_texto = ttk.Button(frame_botones_entrada, 
                                           text="Cargar archivo de texto",
                                           command=self.cargar_texto)
        self.btn_cargar_texto.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_botones_entrada, text="o escribe directamente:").pack(side=tk.LEFT, padx=5)
        
        self.txt_entrada = scrolledtext.ScrolledText(frame_entrada, height=8, wrap=tk.WORD,
                                                      font=("Consolas", 10))
        self.txt_entrada.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botón analizar
        self.btn_analizar = ttk.Button(main_frame, text="ANALIZAR TEXTO", 
                                       command=self.analizar,
                                       style="Accent.TButton")
        self.btn_analizar.pack(pady=10)
        
        # Frame para resultados
        frame_resultados = ttk.LabelFrame(main_frame, text="3. Resultados del Análisis", padding="10")
        frame_resultados.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame para estadísticas
        self.frame_estadisticas = ttk.Frame(frame_resultados)
        self.frame_estadisticas.pack(fill=tk.X, pady=5)
        
        self.lbl_estadisticas = ttk.Label(self.frame_estadisticas, text="", 
                                          font=("Consolas", 10))
        self.lbl_estadisticas.pack()
        
        # Tabla de tokens
        frame_tabla = ttk.Frame(frame_resultados)
        frame_tabla.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tabla_tokens = ttk.Treeview(frame_tabla, columns=("Token", "Lexema"), 
                                          show="headings", yscrollcommand=scrollbar.set)
        self.tabla_tokens.heading("Token", text="Token")
        self.tabla_tokens.heading("Lexema", text="Lexema")
        self.tabla_tokens.column("Token", width=300)
        self.tabla_tokens.column("Lexema", width=200)
        self.tabla_tokens.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.tabla_tokens.yview)
        
        # Configurar colores para tipos de tokens
        self.tabla_tokens.tag_configure("PALABRA_VALIDA_ESPANOL", background="#90EE90")
        self.tabla_tokens.tag_configure("ERROR_ORTOGRAFICO", background="#FFB6C1")
        self.tabla_tokens.tag_configure("DIGITO", background="#ADD8E6")
        self.tabla_tokens.tag_configure("PUNTUACION", background="#FFFACD")
        
        # Botón exportar
        frame_exportar = ttk.Frame(main_frame)
        frame_exportar.pack(fill=tk.X, pady=5)
        
        self.btn_exportar = ttk.Button(frame_exportar, text="Exportar resultados a archivo",
                                       command=self.exportar_resultados)
        self.btn_exportar.pack(side=tk.RIGHT, padx=5)
    
    def cargar_diccionario(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de diccionario",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            exito, mensaje = self.analizador.cargar_diccionario(archivo)
            if exito:
                self.diccionario_cargado = True
                self.lbl_estado_diccionario.config(text=f"{mensaje}", foreground="green")
            else:
                self.diccionario_cargado = False
                self.lbl_estado_diccionario.config(text=f"{mensaje}", foreground="red")
                messagebox.showerror("Error", mensaje)
    
    def cargar_texto(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de texto",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                self.txt_entrada.delete(1.0, tk.END)
                self.txt_entrada.insert(tk.END, contenido)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")
    
    def analizar(self):
        if not self.diccionario_cargado:
            messagebox.showwarning("Advertencia", 
                                   "Primero debes cargar el archivo diccionario_espanol.txt")
            return
        
        texto = self.txt_entrada.get(1.0, tk.END).strip()
        if not texto:
            messagebox.showwarning("Advertencia", "No hay texto para analizar")
            return
        
        # Limpiar tabla anterior
        for item in self.tabla_tokens.get_children():
            self.tabla_tokens.delete(item)
        
        # Analizar
        tokens = self.analizador.analizar_texto(texto)
        self.tokens_actuales = tokens
        
        # Mostrar tokens en la tabla
        for tipo_token, lexema in tokens:
            self.tabla_tokens.insert("", tk.END, values=(tipo_token, lexema), tags=(tipo_token,))
        
        # Mostrar estadísticas
        stats = self.analizador.obtener_estadisticas(tokens)
        texto_stats = (f"ESTADÍSTICAS: Total: {stats['total']} | "
                      f"Válidas: {stats['validas']} | "
                      f"Errores: {stats['errores']} | "
                      f"Dígitos: {stats['digitos']} | "
                      f"  Puntuación: {stats['puntuacion']}")
        self.lbl_estadisticas.config(text=texto_stats)
    
    def exportar_resultados(self):
        if not hasattr(self, 'tokens_actuales') or not self.tokens_actuales:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        archivo = filedialog.asksaveasfilename(
            title="Guardar resultados",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(f"{'Token':<30} {'Lexema':<20}\n")
                    f.write("-" * 50 + "\n")
                    for tipo_token, lexema in self.tokens_actuales:
                        f.write(f"{tipo_token:<30} {lexema:<20}\n")
                    
                    # Agregar estadísticas
                    stats = self.analizador.obtener_estadisticas(self.tokens_actuales)
                    f.write("\n" + "=" * 50 + "\n")
                    f.write("ESTADÍSTICAS DEL ANÁLISIS\n")
                    f.write(f"Total de tokens:        {stats['total']}\n")
                    f.write(f"Palabras válidas:       {stats['validas']}\n")
                    f.write(f"Errores ortográficos:   {stats['errores']}\n")
                    f.write(f"Dígitos:                {stats['digitos']}\n")
                    f.write(f"Puntuación:             {stats['puntuacion']}\n")
                
                messagebox.showinfo("Éxito", f"Resultados exportados a:\n{archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")


def main():
    root = tk.Tk()
    app = InterfazAnalizador(root)
    root.mainloop()


if __name__ == "__main__":
    main()
