"""Script wrapper pour lancer le générateur de livre sur la gestion de l'anxiété"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Force UTF-8 encoding
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import subprocess
result = subprocess.run([
    sys.executable,
    'orchestrator.py',
    '--niche', 'Ansiedad y Técnicas de Relajación Práctica',
    '--cible', 'Adultos jóvenes estresados buscan calma mental',
    '--step', 'architect',
    '--chapitres', '10'
], capture_output=True, text=True, encoding='utf-8')
print(result.stdout)
if result.stderr:
    print("ERREUR:", result.stderr)