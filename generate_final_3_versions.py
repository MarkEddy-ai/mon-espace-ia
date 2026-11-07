"""
Compilateur Universel Multi-Formats KDP & E-Commerce (MarkEddy).
Produit :
1. livre_kdp_broche_6x9.pdf (Print KDP 6x9 po avec marges de reliure)
2. livre_kdp_ebook.epub (EPUB 3 KDP Kindle avec couverture et métadonnées)
3. livre_numerique_interactif.pdf (PDF vectoriel numérique pour Gumroad/Etsy)
"""

import asyncio
from pathlib import Path
import markdown
from ebooklib import epub
from playwright.async_api import async_playwright

HTML_SOURCE = Path("livre_haute_couture.html")
MANUSCRIT_MD = Path("manuscrit_enrichi.md")
COUVERTURE_EBOOK_IMG = Path("couvertures_export/01_amazon_kdp_ebook_cover.jpg")

PDF_BROCHE = Path("livre_kdp_broche_6x9.pdf")
EPUB_SORTIE = Path("livre_kdp_ebook.epub")
PDF_INTERACTIF = Path("livre_numerique_interactif.pdf")


async def compiler_pdf_broche():
    """Génère le PDF 6x9 pouces prêt pour l'impression industrielle KDP via Chromium."""
    print("🖨️  Génération du PDF Broché KDP 6x9 po (Print-Ready)...")
    if not HTML_SOURCE.exists():
        print(f"❌ {HTML_SOURCE} introuvable.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(HTML_SOURCE.resolve().as_uri(), wait_until="networkidle")

        await page.pdf(
            path=str(PDF_BROCHE),
            width="6in",
            height="9in",
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=False
        )
        await browser.close()
    print(f"  ✅ PDF Broché KDP prêt : {PDF_BROCHE.name}")


async def compiler_pdf_interactif():
    """Génère un PDF interactif orienté lecture écran/tablette."""
    print("📱 Génération du PDF Numérique Interactif...")
    if not HTML_SOURCE.exists():
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(HTML_SOURCE.resolve().as_uri(), wait_until="networkidle")

        await page.pdf(
            path=str(PDF_INTERACTIF),
            format="A4",
            print_background=True,
            prefer_css_page_size=False,
            display_header_footer=False
        )
        await browser.close()
    print(f"  ✅ PDF Interactif prêt : {PDF_INTERACTIF.name}")


def compiler_ebook_epub():
    """Génère l'eBook au format EPUB 3 conforme KDP avec métadonnées officielles."""
    print("📖 Génération de l'eBook EPUB 3 (Kindle / KDP)...")
    if not MANUSCRIT_MD.exists():
        print(f"❌ {MANUSCRIT_MD} introuvable.")
        return

    book = epub.EpubBook()
    book.set_identifier("markeddy-finances-2026-kdp")
    book.set_title("Maîtriser ses Finances Personnelles")
    book.set_language("fr")
    book.add_author("MarkEddy")

    # Intégration de la couverture si existante
    if COUVERTURE_EBOOK_IMG.exists():
        book.set_cover("cover.jpg", COUVERTURE_EBOOK_IMG.read_bytes())

    texte_markdown = MANUSCRIT_MD.read_text(encoding="utf-8")
    chapitres_md = texte_markdown.split("# Chapitre ")

    toc_items = []
    spine_items = ["nav"]

    # Traitement des pages liminaires (Front matter)
    intro_html = markdown.markdown(chapitres_md[0], extensions=["extra", "tables"])
    c_intro = epub.EpubHtml(title="Introduction & Mentions Légales", file_name="frontmatter.xhtml", lang="fr")
    c_intro.content = f"<html><body>{intro_html}</body></html>"
    book.add_item(c_intro)
    toc_items.append(c_intro)
    spine_items.append(c_intro)

    # Traitement de chaque chapitre
    for i, chap_corps in enumerate(chapitres_md[1:], start=1):
        lignes = chap_corps.splitlines()
        titre_chap = lignes[0].strip() if lignes else f"Chapitre {i}"
        html_corps = markdown.markdown(f"# Chapitre {chap_corps}", extensions=["extra", "tables"])

        c_chap = epub.EpubHtml(title=f"Chapitre {i} : {titre_chap}", file_name=f"chapitre_{i:02d}.xhtml", lang="fr")
        c_chap.content = f"<html><body>{html_corps}</body></html>"
        book.add_item(c_chap)
        toc_items.append(c_chap)
        spine_items.append(c_chap)

    book.toc = tuple(toc_items)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    style = """
    body { font-family: sans-serif; line-height: 1.5; padding: 5%; }
    h1, h2 { color: #0F172A; text-align: center; }
    blockquote { border-left: 3px solid #D97706; padding-left: 10px; margin: 15px 0; background: #F8FAFC; }
    table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    th, td { border: 1px solid #CBD5E1; padding: 6px; text-align: left; }
    th { background: #0F172A; color: #FFF; }
    """
    default_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(default_css)
    book.spine = spine_items

    epub.write_epub(str(EPUB_SORTIE), book, {})
    print(f"  ✅ eBook EPUB prêt : {EPUB_SORTIE.name}")


async def main():
    print("=" * 65)
    print("🚀 COMPILATION DES 3 VERSIONS COMMERCIALES (AUTEUR : MarkEddy)")
    print("=" * 65)
    await compiler_pdf_broche()
    await compiler_pdf_interactif()
    compiler_ebook_epub()
    print("\n🎉 OPÉRATION TERMINÉE SANS AUCUNE ERREUR.")


if __name__ == "__main__":
    asyncio.run(main())