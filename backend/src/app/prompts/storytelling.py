from __future__ import annotations

SYSTEM_PROMPT = (
    "Eres un asistente de redacción profesional especializado en portfolios "
    "de desarrolladores de software. Tu objetivo es mejorar el contenido "
    "manteniendo la voz del usuario y enfocándote en impacto mediable. "
    "Responde SOLO con el texto mejorado, sin explicaciones."
)


def improve_section_prompt(section_type: str, title: str, content: str) -> str:
    return (
        f"Mejora la siguiente sección de un portfolio profesional.\n\n"
        f"Tipo de sección: {section_type}\n"
        f"Título: {title}\n\n"
        f"Contenido actual:\n{content}\n\n"
        f"Instrucciones:\n"
        f"- Cuantificar logros cuando sea posible (%, números, métricas)\n"
        f"- Usar verbos de acción fuertes (lideré, optimicé, implementé)\n"
        f"- Mantener la voz y tono originales del usuario\n"
        f"- Mejorar la claridad sin cambiar el significado\n"
        f"- Formato: devuelve solo el texto mejorado"
    )


def expand_section_prompt(section_type: str, title: str, content: str) -> str:
    format_hint = ""
    if section_type in ("proceso", "solution", "impact"):
        format_hint = (
            "\nSigue el formato: Proceso → Solución → Impacto.\n"
            "Describe el problema/enfoque, la implementación, y el resultado mediable.\n"
        )
    return (
        f"Expande narrativamente la siguiente sección de un portfolio.\n\n"
        f"Tipo de sección: {section_type}\n"
        f"Título: {title}\n\n"
        f"Contenido actual:\n{content}\n"
        f"{format_hint}\n"
        f"Instrucciones:\n"
        f"- Agregar contexto y detalles que enriquezcan la historia\n"
        f"- Mantener coherencia con el tono profesional\n"
        f"- No inventar información falsa, expandir sobre lo existente\n"
        f"- Formato: devuelve solo el texto expandido"
    )


def suggest_headline_prompt(current_title: str, current_bio: str, target_role: str) -> str:
    return (
        f"Sugiere un título profesional y una bio corta optimizados para el rol objetivo.\n\n"
        f"Título actual: {current_title}\n"
        f"Bio actual: {current_bio}\n"
        f"Rol objetivo: {target_role}\n\n"
        f"Instrucciones:\n"
        f"- El título debe ser impactante y relevante para el rol\n"
        f"- La bio debe ser concisa (máx 2 oraciones) y resaltar valor\n"
        f"- Usar keywords del sector sin sonar genérico\n"
        f'- Responde en formato JSON: {{"title": "...", "bio": "..."}}'
    )


def apply_suggestion_prompt(original: str, suggestion: str) -> str:
    return (
        f"El usuario tiene este contenido y recibió una sugerencia de mejora.\n"
        f"Aplica la sugerencia manteniendo la esencia del original.\n\n"
        f"Original:\n{original}\n\n"
        f"Sugerencia:\n{suggestion}\n\n"
        f"Responde SOLO con el texto resultante."
    )
