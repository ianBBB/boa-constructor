# Detect operating system
ifeq ($(OS),Windows_NT)
	SCRIPT_BOOTSTRAP := bootstrap.bat
    SCRIPT_RUN := run.bat
else
	SCRIPT_BOOTSTRAP := ./bootstrap.sh
    SCRIPT_RUN := ./run.sh
endif

.PHONY: bootstrap
bootstrap:
	$(SCRIPT_BOOTSTRAP)

.PHONY: run
run:
	$(SCRIPT_RUN)
