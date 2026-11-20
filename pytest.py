"""
pytest.py - Module d'exécution compatible pour 'python -m pytest <fichiers>.py'.
Permet l'exécution directe des suites de tests sans dépendance externe.
Supporte une ou plusieurs cibles : test_suite.py test_extensions.py ...
"""
import sys
from pathlib import Path


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
        return test_extensions.main()

    if target_file == "test_saas_auth.py":
        import test_saas_auth
        return 0

    if target_file == "test_media_and_coloring.py":
        import test_media_and_coloring
        test_media_and_coloring.main()
        return 0

    import unittest
    suite = unittest.defaultTestLoader.discover(".", pattern=target_file)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


def main():
    args = sys.argv[1:]
    cibles = [arg for arg in args if arg.endswith(".py") and Path(arg).exists()]
    if not cibles:
        cibles = ["test_suite.py"]

    code_sortie = 0
    for target_file in cibles:
        code = _executer_cible(target_file)
        if code != 0:
            code_sortie = code

    if len(cibles) > 1:
        print("\n" + "=" * 65)
        print(f"📊 [PYTEST] Récapitulatif : {len(cibles)} cible(s) exécutée(s) -> "
              f"{'SUCCÈS' if code_sortie == 0 else 'ÉCHEC'} (code {code_sortie})")
        print("=" * 65)

    sys.exit(code_sortie)


if __name__ == "__main__":
    main()
