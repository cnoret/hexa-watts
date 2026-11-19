"""
Outils pour rendre la mémoire au système après la lecture des gros fichiers.

Arrow et la libc conservent souvent la mémoire libérée pour la réutiliser,
ce qui gonfle durablement la consommation du processus. Sur Streamlit
Community Cloud (environ 1 Go de RAM), cela suffit à faire redémarrer l'app.
"""

import ctypes
import gc

import pyarrow as pa

# L'allocateur par défaut d'Arrow (mimalloc ou jemalloc) garde la mémoire
# libérée pour lui : avec l'allocateur système, malloc_trim peut la rendre.
# streamlit_app.py le choisit déjà via ARROW_DEFAULT_MEMORY_POOL ; ceci
# couvre le cas où pyarrow aurait été importé avant.
pa.set_memory_pool(pa.system_memory_pool())


def liberer_memoire():
    """Rend au système la mémoire inutilisée (Arrow puis glibc)."""
    gc.collect()
    pa.default_memory_pool().release_unused()
    try:
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except (OSError, AttributeError):
        # libc absente (macOS, Windows) : rien à faire
        pass
