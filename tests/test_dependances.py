"""Le requirements.txt s'installe sans conflit."""

import re
import subprocess
import sys
from importlib import metadata

import pytest

from tests.conftest import RACINE


def epinglages():
    """Paquets et versions de requirements.txt (lignes « nom==version »)."""
    paquets = {}
    for ligne in (RACINE / "requirements.txt").read_text(encoding="utf-8").splitlines():
        ligne = ligne.split("#")[0].strip()
        if not ligne:
            continue
        correspondance = re.fullmatch(r"([A-Za-z0-9_.\-]+)==([A-Za-z0-9_.\-]+)", ligne)
        assert correspondance, f"Version non épinglée dans requirements.txt : {ligne!r}"
        paquets[correspondance.group(1)] = correspondance.group(2)
    return paquets


def test_toutes_les_versions_sont_epinglees():
    assert epinglages()


@pytest.mark.parametrize("paquet,version", sorted(epinglages().items()))
def test_version_installee(paquet, version):
    """L'environnement de test utilise exactement les versions de requirements.txt."""
    assert metadata.version(paquet) == version


def test_pas_de_conflit_entre_dependances():
    """Équivalent de `pip check` : chaque dépendance des paquets installés est satisfaite."""
    if subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True).returncode:
        pytest.skip("pip n'est pas disponible dans cet environnement")
    resultat = subprocess.run(
        [sys.executable, "-m", "pip", "check"], capture_output=True, text=True
    )
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
