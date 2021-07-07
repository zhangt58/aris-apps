UIC_FLAGS := --from-imports -x

all: main rc

main: rc
	pyuic5 ui_app.ui -o ui_app.py $(UIC_FLAGS)
	yapf -i ui_app.py

rc:
	pyrcc5 resources.qrc -o resources_rc.py
	yapf -i resources_rc.py
