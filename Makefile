dist:
	rm -Rf ./dist/*
	mkdir -p dist build
	python setup.py sdist

deploy: bump dist
	ansible-playbook ./deploy/sync.yml -v

bump:
	python -c "from cztwitter.cli import bump_version; bump_version()"

reqs:
	pip-compile --output-file requirements.txt requirements.in

.PHONY: dist deploy bump reqs
