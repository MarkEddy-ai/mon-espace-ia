"""
pytest.py - Module d'exécution compatible pour 'python -m pytest <fichiers>.py'.
Permet l'exécution directe des suites de tests sans dépendance externe.
Supporte une ou plusieurs cibles : test_suite.py test_extensions.py ...

Correctifs QA : stdout UTF-8 (Windows cp1252), cibles normalisées/dédupliquées,
capture de SystemExit pour agréger TOUTES les suites même en cas d'échec.
"""
import sys
import traceback
from pathlib import Path

# La console Windows redirigée utilise cp1252 : sans ceci, le premier emoji
# (🚀) fait échouer la commande avant même le premier test.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

SUITES_CONNUES = {
    "test_suite.py",
    "test_extensions.py",
    "test_new_extensions.py",
    "test_saas_auth.py",
    "test_media_and_coloring.py",
    "test_multilingual_kdp.py",
}


def _executer_cible(target_file: str) -> int:
    """Exécute une cible de test et retourne son code de sortie (0 = succès)."""
    print(f"\n🚀 [PYTEST] Exécution automatisée sur la cible : {target_file}")

    if target_file == "test_suite.py":
        import test_suite
        test_suite.main()
        if test_suite.tests_total > 0 and test_suite.tests_reussis == test_suite.tests_total:
            return 0
        return 1

    if target_file == "test_extensions.py":
        import test_extensions
        return int(test_extensions.main() or 0)

    if target_file == "test_new_extensions.py":
        import test_new_extensions
        return int(test_new_extensions.main() or 0)

    if target_file == "test_multilingual_kdp.py":
        import test_multilingual_kdp
        return int(test_multilingual_kdp.main() or 0)

    if target_file == "test_saas_auth.py":
        # Le module s'auto-exécute à l'import : un SystemExit(1) est capturé
        # par main() et agrégé avec les autres suites.
        import test_saas_auth  # noqa: F401
        return 0

    if target_file == "test_media_and_coloring.py":
        import test_media_and_coloring
        resultat = test_media_and_coloring.main()
        return int(resultat or 0)

    import unittest
    suite = unittest.defaultTestLoader.discover(".", pattern=target_file)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


def main():
    args = sys.argv[1:]
    bruts = [Path(arg).name for arg in args if arg.endswith(".py")]
    cibles = []
    for brut in bruts:
        if brut not in SUITES_CONNUES:
            print(f"⚠️ [PYTEST] Cible inconnue ignorée : {brut}")
            continue
        if not Path(brut).exists():
            print(f"⚠️ [PYTEST] Fichier introuvable ignoré : {brut}")
            continue
        if brut not in cibles:
            cibles.append(brut)
    if not cibles:
        cibles = ["test_suite.py"]

    code_sortie = 0
    for target_file in cibles:
        try:
            code = _executer_cible(target_file)
        except SystemExit as e:
            code = int(e.code or 0)
        except Exception:
            traceback.print_exc()
            code = 1
        if code != 0:
            code_sortie = code

    if len(cibles) > 1 or code_sortie != 0:
        print("\n" + "=" * 65)
        print(f"📊 [PYTEST] Récapitulatif : {len(cibles)} cible(s) exécutée(s) -> "
              f"{'SUCCÈS' if code_sortie == 0 else 'ÉCHEC'} (code {code_sortie})")
        print("=" * 65)

    sys.exit(code_sortie)


if __name__ == "__main__":
    main()
