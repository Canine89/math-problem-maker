.PHONY: install validate render clean help

VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python

help:
	@echo "사용법:"
	@echo "  make install          Python 의존성 설치"
	@echo "  make validate FILE=   YAML 문제 파일 검증"
	@echo "  make render FILE=     YAML -> PDF/Word/HTML 렌더링"
	@echo "  make render-all       problems/ 내 모든 YAML 렌더링"
	@echo "  make clean            output/ 비우기"

install:
	python3 -m venv $(VENV_DIR)
	$(PYTHON) -m pip install -r requirements.txt

validate:
	@test -n "$(FILE)" || (echo "ERROR: FILE 인자 필요. 예: make validate FILE=problems/examples/sample-calculus.yaml" && exit 1)
	$(PYTHON) scripts/validate.py $(FILE)

render:
	@test -n "$(FILE)" || (echo "ERROR: FILE 인자 필요. 예: make render FILE=problems/examples/sample-calculus.yaml" && exit 1)
	$(PYTHON) scripts/render.py $(FILE)

render-all:
	@for f in problems/**/*.yaml problems/*.yaml; do \
		[ -f "$$f" ] && echo "=== $$f ===" && $(PYTHON) scripts/render.py "$$f"; \
	done

clean:
	rm -rf output/*
	@echo "output/ 정리 완료"
