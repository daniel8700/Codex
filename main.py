"""Aplicación de escritorio "Gestor de Números Primos" usando tkinter."""

import math
import tkinter as tk
from tkinter import messagebox


def es_primo(numero: int) -> bool:
    """Determina si un número entero es primo."""
    if numero < 2:
        return False
    if numero == 2:
        return True
    if numero % 2 == 0:
        return False

    limite = int(math.sqrt(numero)) + 1
    for candidato in range(3, limite, 2):
        if numero % candidato == 0:
            return False
    return True


def filtrar_primos(lista: list[int]) -> list[int]:
    """Devuelve una nueva lista con los números primos encontrados en ``lista``."""
    return [numero for numero in lista if es_primo(numero)]


class GestorPrimosApp:
    """Ventana principal para gestionar la interacción con el usuario."""

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("Gestor de Números Primos")
        self.master.geometry("480x260")

        # Variable asociada al resultado mostrado en pantalla.
        self.resultado_var = tk.StringVar(value="Introduce valores para ver el resultado aquí.")

        self._construir_interfaz()

    def _construir_interfaz(self) -> None:
        """Crea y ordena los componentes gráficos."""
        contenedor = tk.Frame(self.master, padx=20, pady=20)
        contenedor.pack(fill=tk.BOTH, expand=True)

        # Etiqueta descriptiva para explicar al usuario qué debe introducir.
        etiqueta_instrucciones = tk.Label(
            contenedor,
            text=(
                "Ingresa una lista de números enteros separados por comas (por ejemplo:"
                " 2, 3, 4, 5)"
            ),
            anchor="w",
            justify=tk.LEFT,
            font=("Segoe UI", 10),
        )
        etiqueta_instrucciones.pack(fill=tk.X, pady=(0, 10))

        # Campo de texto donde el usuario escribe los números.
        self.entrada_numeros = tk.Entry(contenedor, width=50)
        self.entrada_numeros.pack(fill=tk.X)

        # Botón principal que desencadena el filtrado de números primos.
        boton_filtrar = tk.Button(
            contenedor,
            text="Filtrar primos",
            command=self._manejar_filtrado,
            cursor="hand2",
        )
        boton_filtrar.pack(pady=15)

        # Etiqueta para mostrar el resultado del filtrado de manera clara.
        etiqueta_resultado = tk.Label(
            contenedor,
            textvariable=self.resultado_var,
            anchor="w",
            justify=tk.LEFT,
            font=("Segoe UI", 10, "bold"),
            wraplength=420,
        )
        etiqueta_resultado.pack(fill=tk.X)

    def _manejar_filtrado(self) -> None:
        """Procesa la entrada del usuario y actualiza el resultado en pantalla."""
        texto = self.entrada_numeros.get().strip()

        # Validamos que exista entrada y que siga el formato esperado.
        if not texto:
            messagebox.showerror(
                "Entrada vacía",
                "Por favor, introduce números separados por comas para continuar.",
            )
            return

        try:
            numeros = [int(parte.strip()) for parte in texto.split(",") if parte.strip()]
        except ValueError:
            messagebox.showerror(
                "Formato incorrecto",
                "Asegúrate de ingresar solo números enteros separados por comas.",
            )
            return

        if not numeros:
            messagebox.showerror(
                "Sin números",
                "No se detectaron números válidos en la entrada proporcionada.",
            )
            return

        primos = filtrar_primos(numeros)
        if primos:
            self.resultado_var.set(f"Números primos encontrados: {', '.join(map(str, primos))}")
        else:
            self.resultado_var.set("No se encontraron números primos en la lista proporcionada.")


def main() -> None:
    """Inicia la aplicación gráfica."""
    root = tk.Tk()
    GestorPrimosApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
