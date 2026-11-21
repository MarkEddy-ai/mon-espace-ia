from playwright.sync_api import sync_playwright
import pypdf

html_symmetric = """<!DOCTYPE html>
<html>
<head>
<style>
@page {
    size: 6in 9in;
    margin: 0.65in 0.50in;
    @bottom-center { content: counter(page); }
}
body {
    margin: 0;
    padding: 0;
    font-size: 11pt;
    text-align: justify;
}
</style>
</head>
<body>
<p>Ceci est un test de centrage typographique parfait. Le texte doit débuter exactement à 0.50 pouce (36 points) du bord gauche et s'arrêter exactement à 0.50 pouce (36 points) du bord droit sur toutes les pages sans aucune exception.</p>
<div style="page-break-before: always;"></div>
<p>Page 2 : Ceci est la deuxième page. Le texte doit également être rigoureusement centré avec 0.50 pouce de marge à gauche et 0.50 pouce à droite.</p>
</body>
</html>
"""

with sync_playwright() as p:
    try: browser = p.chromium.launch()
    except: browser = p.chromium.launch(channel='msedge')
    page = browser.new_page()
    page.set_content(html_symmetric)
    page.pdf(path='test_sym.pdf', prefer_css_page_size=True, print_background=True)
    browser.close()

reader = pypdf.PdfReader('test_sym.pdf')
print("Pages:", len(reader.pages))
for i in range(len(reader.pages)):
    items = []
    def visitor(text, cm, tm, font_dict, font_size):
        if text.strip():
            items.append(tm[4])
    reader.pages[i].extract_text(visitor_text=visitor)
    min_x, max_x = min(items), max(items)
    print(f"Page {i+1}: min_x={min_x:.1f}pt ({(min_x/72):.2f}in), max_x={max_x:.1f}pt (droite={((432-max_x)/72):.2f}in)")
