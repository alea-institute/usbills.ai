# setup poetry
poetry update

# set env
export PYTHONPATH=.

# set up database
poetry run bash alembic/revision.sh
poetry run bash alembic/upgrade.sh

# setup npm
npm install
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest

# run tailwind gen
npx tailwindcss -i static/tailwind.input.css -o static/tailwind.css --minify

# run update optionally
# poetry run bash update.sh



