
install:
	poetry install

run:
	poetry run project

build:
	poetry build

publish:
	poetry publish

package-install:
	pip install dist/*.whl