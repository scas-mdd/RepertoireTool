GUI_FILES= \
		ui/page_ccfx.ui  \
		ui/page_confirm.ui  \
		ui/page_projdir.ui   \
		ui/page_vcs_suffix.ui \
		ui/page_vcs_when.ui \
		ui/page_vcs_where.ui \
		ui/page_vcs_which.ui \
		ui/page_welcome.ui \
		ui/page_working.ui \
		ui/page_final.ui \
		ui/wizard.ui \
		ui/wizard_generic.ui \
		ui/rep_output.ui \
		ui/file_display.ui


GUI_PYTHON_FILES := $(patsubst %.ui,%.py,$(GUI_FILES))

ui/%.py : ui/%.ui
	pyuic4 $< -o $@

all: $(GUI_PYTHON_FILES)
	@echo Building Repertoire UI
	@touch ui/__init__.py

clean_data:
	rm -rf repertoire_tmp_*

clean: clean_data
	rm -f ui/*.py
	rm -f ui/*.pyc
	rm -f *.pyc
