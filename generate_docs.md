# Automated Documentation with Sphinx

1. Install requirements: `MusicPlayer> pip install sphinx sphinx-rtd-theme`
2. Prepare Base files: `MusicPlayer/docs> sphinx-quickstart` (follow terminal instructions)
3. Generate .rst files: `MusicPlayer> sphinx-apidoc -o docs .`
4. Generate HTML Documentation: 
   - Windows: `MusicPlayer/docs> ./make.bat html`
   - Linux: `MusicPlayer/docs> make html`

(Tutorial Video: https://www.youtube.com/watch?v=BWIrhgCAae0)