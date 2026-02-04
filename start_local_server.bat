@echo off
echo Starting local web server on http://localhost:8000
echo.
echo Open your browser to: http://localhost:8000/npc_mindmap_viewer.html
echo.
echo Press Ctrl+C to stop the server
echo.
python -m http.server 8000
