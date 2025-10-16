"""Script para realizar web scraping en coppel.com.

El programa solicita al usuario una palabra de búsqueda y consulta la
página de resultados de Coppel usando requests. Posteriormente analiza la
respuesta con BeautifulSoup para extraer nombre, precio y enlace de los
productos mostrados y guarda la información en un CSV.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from typing import Iterable, List
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

# Encabezados HTTP para disminuir la probabilidad de bloqueos por parte del sitio.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}
BASE_URL = "https://www.coppel.com"
CSV_FILENAME = "productos_coppel.csv"


@dataclass
class Product:
    """Representa la información básica de un producto."""

    name: str
    price: str
    url: str


def request_search_page(query: str) -> requests.Response:
    """Obtiene la página de resultados para la consulta proporcionada."""

    search_url = f"{BASE_URL}/buscar?q={quote_plus(query)}"
    response = requests.get(search_url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response


def extract_products(html: str) -> List[Product]:
    """Analiza el HTML y devuelve una lista de productos encontrados."""

    soup = BeautifulSoup(html, "html.parser")

    products: List[Product] = []
    seen_urls: set[str] = set()

    # Primero intentamos extraer información estructurada a partir de JSON-LD.
    for product_data in _extract_products_from_json_ld(soup):
        name = product_data.get("name")
        raw_url = product_data.get("url") or product_data.get("@id")
        if not name or not raw_url:
            continue

        absolute_url = urljoin(BASE_URL, raw_url)
        price = _extract_price_from_offers(product_data.get("offers"))
        if not price:
            # Si no existe precio explícito, revisamos si hay especificaciones.
            price_spec = product_data.get("priceSpecification")
            price = _extract_price_from_offers(price_spec)

        if absolute_url not in seen_urls:
            products.append(
                Product(
                    name=name.strip(),
                    price=price or "Precio no disponible",
                    url=absolute_url,
                )
            )
            seen_urls.add(absolute_url)

    # Si no se encontró nada mediante JSON-LD, utilizamos una extracción heurística.
    if not products:
        products.extend(_extract_products_from_markup(soup, seen_urls))

    return products


def _extract_products_from_json_ld(soup: BeautifulSoup) -> Iterable[dict]:
    """Extrae estructuras de producto desde etiquetas JSON-LD."""

    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        json_text = script.string or script.get_text(strip=True)
        if not json_text:
            continue
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            continue
        yield from _walk_json_ld(data)


def _walk_json_ld(data) -> Iterable[dict]:
    """Recorre recursivamente la estructura JSON-LD buscando productos."""

    if isinstance(data, list):
        for item in data:
            yield from _walk_json_ld(item)
    elif isinstance(data, dict):
        data_type = data.get("@type")
        if data_type in {"Product", "ProductGroup"}:
            yield data
        if data_type == "ItemList":
            for item in data.get("itemListElement", []):
                if isinstance(item, dict):
                    # Los elementos de la lista suelen ser diccionarios con la clave "item".
                    nested = item.get("item") or item
                    yield from _walk_json_ld(nested)
        if "@graph" in data:
            yield from _walk_json_ld(data["@graph"])


def _extract_price_from_offers(offers) -> str | None:
    """Intenta obtener el precio desde la sección offers de JSON-LD."""

    if not offers:
        return None

    if isinstance(offers, list):
        for offer in offers:
            price = _extract_price_from_offers(offer)
            if price:
                return price
        return None

    if isinstance(offers, dict):
        price = offers.get("price") or offers.get("priceValue")
        if price:
            try:
                # Intentamos formatear el precio numéricamente.
                price_number = float(price)
                return f"${price_number:,.2f}".replace(",", "_").replace("_", ",")
            except (ValueError, TypeError):
                return str(price)

        # Algunos esquemas usan priceSpecification anidado.
        price_spec = offers.get("priceSpecification")
        if price_spec:
            return _extract_price_from_offers(price_spec)

    return None


def _extract_products_from_markup(soup: BeautifulSoup, seen_urls: set[str]) -> List[Product]:
    """Extrae productos mediante selectores heurísticos del HTML."""

    products: List[Product] = []
    product_selectors = [
        "[data-test='molecule-product-card']",
        "[data-test='product-card']",
        "article[class*='product']",
        "div[class*='product']",
    ]
    price_selectors = [
        "[data-test='product-price']",
        "span[class*='price']",
        "p[class*='price']",
    ]

    combined_selector = ",".join(product_selectors)
    for card in soup.select(combined_selector):
        link = card.find("a", href=True)
        if not link:
            continue
        raw_url = link.get("href")
        if not raw_url:
            continue
        absolute_url = urljoin(BASE_URL, raw_url)
        if absolute_url in seen_urls:
            continue

        # Intentamos obtener el nombre del producto.
        name = link.get("title") or link.get_text(strip=True)
        if not name:
            name_elem = None
            for selector in ["h2", "h3", "p", "span"]:
                name_elem = card.select_one(selector)
                if name_elem and name_elem.get_text(strip=True):
                    name = name_elem.get_text(strip=True)
                    break
        if not name:
            continue

        # Buscamos un precio cercano al enlace usando diferentes selectores.
        price_text = None
        for selector in price_selectors:
            price_elem = card.select_one(selector)
            if price_elem and price_elem.get_text(strip=True):
                price_text = price_elem.get_text(strip=True)
                break
        if not price_text:
            # Como último recurso, buscamos texto con un símbolo de moneda.
            price_elem = card.find(string=lambda text: text and "$" in text)
            if price_elem:
                price_text = price_elem.strip()

        products.append(
            Product(
                name=name.strip(),
                price=price_text or "Precio no disponible",
                url=absolute_url,
            )
        )
        seen_urls.add(absolute_url)

    return products


def save_products_to_csv(products: Iterable[Product], filename: str = CSV_FILENAME) -> None:
    """Guarda la lista de productos en un archivo CSV."""

    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["nombre", "precio", "enlace"])
        for product in products:
            writer.writerow([product.name, product.price, product.url])


def display_products(products: Iterable[Product]) -> None:
    """Muestra la información de los productos en consola."""

    for product in products:
        print(f"Producto: {product.name}")
        print(f"Precio: {product.price}")
        print(f"Enlace: {product.url}\n")


def main() -> None:
    """Punto de entrada del script."""

    try:
        query = input("Ingresa la palabra de búsqueda: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada cancelada. Saliendo...")
        return

    if not query:
        print("No se proporcionó una palabra de búsqueda.")
        return

    try:
        response = request_search_page(query)
    except requests.RequestException as exc:
        print("Ocurrió un error al consultar el sitio de Coppel:", exc)
        return

    products = extract_products(response.text)
    if not products:
        print("No se encontraron productos para la búsqueda proporcionada.")
        return

    display_products(products)
    save_products_to_csv(products)
    print(f"Se guardaron {len(products)} productos en '{CSV_FILENAME}'.")


if __name__ == "__main__":
    main()
