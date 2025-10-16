from math import isqrt
from typing import Iterable, List


def numeros_primos(numeros: Iterable[int]) -> List[int]:
    """Devuelve una lista con los números primos encontrados en ``numeros``.

    Args:
        numeros: Cualquier iterable de enteros.

    Returns:
        Lista que contiene únicamente los valores primos en el orden en el que
        aparecieron en ``numeros``.
    """
    primos: List[int] = []

    for numero in numeros:
        if es_primo(numero):
            primos.append(numero)

    return primos


def es_primo(numero: int) -> bool:
    """Determina si ``numero`` es un número primo."""
    if numero < 2:
        return False

    if numero in (2, 3):
        return True

    if numero % 2 == 0:
        return False

    limite = isqrt(numero)
    divisor = 3
    while divisor <= limite:
        if numero % divisor == 0:
            return False
        divisor += 2

    return True


if __name__ == "__main__":
    print("Hola desde Codex!")
