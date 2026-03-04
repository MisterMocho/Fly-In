VENV_DIR = venv
VENV_BIN = $(VENV_DIR)/bin
PYTHON = $(VENV_BIN)/python3
PIP = $(VENV_BIN)/pip

SRC_DIR = src
MAIN = $(SRC_DIR)/main.py

# Mapa por defeito
ARGS ?= maps/easy/01_linear_path.txt

# --- Regras ---

$(VENV_BIN)/activate:
	python3 -m venv $(VENV_DIR)

install: $(VENV_BIN)/activate
	@echo "A garantir dependências..."
	$(PIP) install flake8 mypy

# Regra 1: Execução normal (sem visual)
run:
	@echo "A executar o Fly-in (Modo Texto)..."
	$(PYTHON) $(MAIN) $(ARGS)

# Regra 2: Execução visual (adiciona a flag explicitamente)
visual:
	@echo "A executar o Fly-in (Modo Visual)..."
	$(PYTHON) $(MAIN) $(ARGS) --visual

debug:
	@echo "A iniciar em modo debug..."
	$(PYTHON) -m pdb $(MAIN) $(ARGS)

clean:
	@echo "A limpar ficheiros temporários..."
	rm -rf __pycache__
	rm -rf $(SRC_DIR)/__pycache__
	rm -rf .mypy_cache
	find . -type f -name "*.pyc" -delete

fclean: clean
	@echo "A remover ambiente virtual..."
	rm -rf $(VENV_DIR)

lint: install
	@echo "A correr flake8..."
	$(VENV_BIN)/flake8 .
	@echo "A correr mypy..."
	$(VENV_BIN)/mypy .

lint-strict: install
	@echo "A correr mypy (strict)..."
	$(VENV_BIN)/mypy --strict .

.PHONY: install run visual debug clean fclean lint lint-strict
