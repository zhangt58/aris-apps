redeploy: clean build deploy clean

clean:
	/bin/rm -rf dist build *.egg-info

build:
	python3 setup.py bdist_wheel

deploy: build
	python3 -m pip install dist/*.whl --upgrade --user

uninstall:
	python3 -m pip uninstall aris