import re


def identificar_intencion(mensaje: str) -> str:
    """Clasifica la intención del usuario usando reglas basadas en expresiones regulares."""
    mensaje = mensaje.strip().lower()

    # Las reglas se evalúan en orden: cada una busca palabras clave que
    # indiquen una intención específica. Si se detecta un patrón se devuelve
    # la etiqueta correspondiente.
    if re.search(r"\b(hola|buen[ao]s? (d[ií]as|tardes|noches))\b", mensaje):
        return "saludo"
    if re.search(r"\b(ad[ií]os|hasta luego|nos vemos|chao)\b", mensaje):
        return "despedida"
    if re.search(r"\b(c[oó]mo est[aá]s|qu[eé] tal)\b", mensaje):
        return "estado"
    if re.search(r"\b(clima|tiempo|temperatura|climat[oó]logo)\b", mensaje):
        return "clima"
    if re.search(r"\b(hora|tiempo actual|reloj)\b", mensaje):
        return "hora"
    if re.search(r"\b(c[oó]mo te llamas|tu nombre|qui[eé]n eres)\b", mensaje):
        return "nombre"

    return "desconocido"


def generar_respuesta(intencion: str) -> str:
    """Genera una respuesta según la intención detectada."""
    if intencion == "saludo":
        return "¡Hola! ¿En qué puedo ayudarte hoy?"
    if intencion == "despedida":
        return "¡Hasta luego! Gracias por conversar conmigo."
    if intencion == "estado":
        return "Estoy muy bien, gracias por preguntar. ¿Y tú?"
    if intencion == "clima":
        return "No tengo acceso al clima en tiempo real, pero espero que el día esté agradable."
    if intencion == "hora":
        return "No puedo ver un reloj, pero te recomiendo revisar tu dispositivo."
    if intencion == "nombre":
        return "Soy un chatbot sencillo listo para charlar contigo."

    return "Lo siento, aún estoy aprendiendo y no entendí tu mensaje."


def iniciar_chat() -> None:
    """Mantiene un bucle de conversación hasta que el usuario escriba 'salir'."""
    print("Bienvenido al chatbot. Escribe 'salir' para terminar la conversación.\n")

    while True:
        mensaje = input("Tú: ").strip()
        if mensaje.lower() == "salir":
            print("Chatbot: ¡Hasta pronto!")
            break

        intencion = identificar_intencion(mensaje)
        respuesta = generar_respuesta(intencion)
        print(f"Chatbot: {respuesta}")


if __name__ == "__main__":
    iniciar_chat()
