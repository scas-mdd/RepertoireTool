GUI_FILES= \
		ui/analysis.ui \
		ui/rep_output.ui \
		ui/file_display.ui


GUI_PYTHON_FILES := $(patsubst %.ui,%.py,$(GUI_FILES))

ui/%.py : ui/%.ui
	pyuic4 $< -o $@

all: $(GUI_PYTHON_FILES)
	@echo Building Repertoire Analysis UI
	@touch ui/__init__.py

clean_data:
	rm -rf repertoire_tmp_*

clean: clean_data
	rm -f ui/*.py
	rm -f ui/*.pyc
	rm -f *.pyc
