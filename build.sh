rm -Rf ./dist
uv build
uv run twine upload dist/*