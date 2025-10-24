# Makefile for Synthetic Document Generation AI Agent Project
# This Makefile handles environment setup, credential management, and common tasks

# Default configuration
CREDENTIALS_FILE ?= credentials.json
ENV_FILE ?= .env
PYTHON ?= python3
PIP ?= pip3

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help setup-env check-credentials install-deps generate-docs run-agent run-multi-agent clean test

# Default target
help: ## Show this help message
	@echo "$(BLUE)Synthetic Document Generation AI Agent - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup-env: ## Set up environment variables from credentials file
	@echo "$(BLUE)Setting up environment variables...$(NC)"
	@if [ -f "$(CREDENTIALS_FILE)" ]; then \
		echo "$(GREEN)✓ Found $(CREDENTIALS_FILE)$(NC)"; \
		$(MAKE) load-credentials CREDENTIALS_FILE=$(CREDENTIALS_FILE); \
	elif [ -f "$(ENV_FILE)" ]; then \
		echo "$(GREEN)✓ Found $(ENV_FILE)$(NC)"; \
		$(MAKE) load-env-file ENV_FILE=$(ENV_FILE); \
	else \
		echo "$(RED)✗ No credentials file found!$(NC)"; \
		echo "$(YELLOW)Please create either:$(NC)"; \
		echo "  - $(CREDENTIALS_FILE) (JSON format)"; \
		echo "  - $(ENV_FILE) (key=value format)"; \
		echo ""; \
		echo "$(YELLOW)You can copy from templates:$(NC)"; \
		echo "  cp credentials.json.template $(CREDENTIALS_FILE)"; \
		echo "  cp .env.example $(ENV_FILE)"; \
		exit 1; \
	fi

load-credentials: ## Load environment variables from JSON credentials file
	@echo "$(BLUE)Loading credentials from $(CREDENTIALS_FILE)...$(NC)"
	@$(PYTHON) -c " \
	import json, os; \
	data = json.load(open('$(CREDENTIALS_FILE)')); \
	os.environ['OPENAI_API_KEY'] = data.get('openai_api_key', ''); \
	os.environ['YDATA_LICENSE_KEY'] = data.get('ydata_license_key', ''); \
	os.environ['OPENAI_MODEL'] = data.get('openai_model', 'gpt-4o-mini'); \
	print('Environment variables set from JSON file') \
	" && echo "$(GREEN)✓ Environment variables loaded from $(CREDENTIALS_FILE)$(NC)"

load-env-file: ## Load environment variables from .env file
	@echo "$(BLUE)Loading environment from $(ENV_FILE)...$(NC)"
	@export $$(grep -v '^#' $(ENV_FILE) | xargs) && echo "$(GREEN)✓ Environment variables loaded from $(ENV_FILE)$(NC)"

check-credentials: ## Verify that required credentials are set
	@echo "$(BLUE)Checking credentials...$(NC)"
	@$(PYTHON) -c " \
	import os; \
	required = ['OPENAI_API_KEY', 'YDATA_LICENSE_KEY']; \
	missing = [k for k in required if not os.getenv(k)]; \
	if missing: \
		print('$(RED)✗ Missing required environment variables: ' + ', '.join(missing) + '$(NC)'); \
		exit(1); \
	else: \
		print('$(GREEN)✓ All required credentials are set$(NC)'); \
		print('OPENAI_API_KEY: ' + ('✓' if os.getenv('OPENAI_API_KEY') else '✗')); \
		print('YDATA_LICENSE_KEY: ' + ('✓' if os.getenv('YDATA_LICENSE_KEY') else '✗')); \
		print('OPENAI_MODEL: ' + os.getenv('OPENAI_MODEL', 'gpt-4o-mini')); \
	"

install-deps: ## Install Python dependencies
	@echo "$(BLUE)Installing Python dependencies...$(NC)"
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

install-conda: ## Install dependencies using conda
	@echo "$(BLUE)Installing dependencies with conda...$(NC)"
	@conda env create -f environment.yml
	@echo "$(GREEN)✓ Conda environment created$(NC)"
	@echo "$(YELLOW)To activate: conda activate synthetic-doc-generation$(NC)"

test: setup-env check-credentials ## Run basic tests
	@echo "$(BLUE)Running basic tests...$(NC)"
	@$(PYTHON) -c " \
	import os; \
	print('Testing environment setup...'); \
	assert os.getenv('OPENAI_API_KEY'), 'OPENAI_API_KEY not set'; \
	assert os.getenv('YDATA_LICENSE_KEY'), 'YDATA_LICENSE_KEY not set'; \
	print('✓ Environment variables are set'); \
	"
	@echo "$(GREEN)✓ Basic tests passed$(NC)"


setup: install-deps setup-env check-credentials ## Complete setup (install deps + setup env)
	@echo "$(GREEN)✓ Complete setup finished$(NC)"

quick-start: setup generate-docs run-agent ## Quick start: setup + generate docs + run agent
	@echo "$(GREEN)✓ Quick start completed$(NC)"

# Development helpers
dev-setup: install-deps ## Development setup without credentials check
	@echo "$(GREEN)✓ Development setup completed (credentials not checked)$(NC)"

# Show current environment status
status: ## Show current environment status
	@echo "$(BLUE)Environment Status:$(NC)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version)"
	@echo "Credentials file: $$(if [ -f '$(CREDENTIALS_FILE)' ]; then echo '$(GREEN)✓ Found$(NC)'; else echo '$(RED)✗ Not found$(NC)'; fi)"
	@echo "Env file: $$(if [ -f '$(ENV_FILE)' ]; then echo '$(GREEN)✓ Found$(NC)'; else echo '$(RED)✗ Not found$(NC)'; fi)"
	@echo "Synthetic PDFs: $$(ls synthetic_pdfs/*.pdf 2>/dev/null | wc -l | tr -d ' ') files"
	@echo "Artifacts: $$(if [ -d 'artifacts' ]; then echo '$(GREEN)✓ Directory exists$(NC)'; else echo '$(RED)✗ Not found$(NC)'; fi)"
