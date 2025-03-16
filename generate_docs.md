# Automated Documentation with Sphinx

1. Install requirements: `MusicPlayer> pip install sphinx sphinx-rtd-theme`
2. Prepare Base files: `MusicPlayer/docs> sphinx-quickstart` (follow terminal instructions)
3. Generate .rst files: `MusicPlayer> sphinx-apidoc --force -o docs .`
4. Generate HTML Documentation: 
   - Windows: `MusicPlayer/docs> ./make.bat html`
   - Linux: `MusicPlayer/docs> make html`

(Tutorial Video: https://www.youtube.com/watch?v=BWIrhgCAae0)

### Troubleshooting RTD submodule not rendering
tried:
1. clean re-/build script
2. commiting `__init__.py` files
3. RTD build process: "WARNING: autodoc: failed to import module \[...\] ModuleNotFoundError: No module named 'numpy'" &rarr; add requirements.txt to readthedocs.yaml
   ```
   ['Traceback (most recent call last):\n', '  File "/home/docs/checkouts/readthedocs.org/user_builds/musicplayer/envs/latest/lib/python3.13/site-packages/sphinx/ext/autodoc/importer.py", line 269, in import_object\n    module = import_module(modname, try_reload=True)\n', '  File "/home/docs/checkouts/readthedocs.org/user_builds/musicplayer/envs/latest/lib/python3.13/site-packages/sphinx/ext/autodoc/importer.py", line 175, in import_module\n    module = importlib.import_module(modname)\n', '  File "/home/docs/.asdf/installs/python/3.13.0/lib/python3.13/importlib/__init__.py", line 88, in import_module\n    return _bootstrap._gcd_import(name[level:], package, level)\n           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n', '  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import\n', '  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load\n', '  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked\n', '  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked\n', '  File "<frozen importlib._bootstrap_external>", line 1022, in exec_module\n', '  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed\n', '  File "/home/docs/checkouts/readthedocs.org/user_builds/musicplayer/checkouts/latest/code_backend/database_access.py", line 1, in <module>\n    from code_backend.shared_config import *\n', '  File "/home/docs/checkouts/readthedocs.org/user_builds/musicplayer/checkouts/latest/code_backend/shared_config.py", line 30, in <module>\n    import numpy\n', "ModuleNotFoundError: No module named 'numpy'\n"] [autodoc.import_object]
   ```
$\Rightarrow$ 3 fixed the Problem