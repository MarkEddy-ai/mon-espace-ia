from pathlib import Path

def convertir_html_en_pdf(source_html: str, sortie_pdf: str) -> Path:
    p_sortie = Path(sortie_pdf)
    p_sortie.parent.mkdir(parents=True, exist_ok=True)
    return p_sortie
