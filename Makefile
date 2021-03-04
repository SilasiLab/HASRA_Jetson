VENV_LIB = HASRA/lib/python3.6
VENV_CV2 = $(VENV_LIB)/cv2.so

# Find cv2 library for the global Python installation.
GLOBAL_CV2 := $(shell /usr/bin/python -c 'import cv2; print(cv2)' | awk '{print $$4}' | sed s:"['>]":"":g)

# Link global cv2 library file inside the virtual environment.
$(VENV_CV2): $(GLOBAL_CV2) venv
	cp $(GLOBAL_CV2) $@

venv: requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate && pip install -r requirements.txt

test: $(VENV_CV2)
	. venv/bin/activate && python -c 'import cv2; print(cv2)'

clean:
	rm -rf venv
