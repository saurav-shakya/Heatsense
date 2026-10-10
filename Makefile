# HeatShield — one entry point for local dev and deploys.
# Backend: AWS SAM (profile saurav-cli, us-east-1). Frontend: Cloudflare Pages (wrangler).

AWS_PROFILE ?= saurav-cli
AWS_REGION  ?= us-east-1
STACK       ?= heatshield-dev
CITY        ?= delhi
PAGES_PROJECT ?= heatshield
FN          ?= api

export AWS_PROFILE AWS_REGION
export SAM_CLI_TELEMETRY = 0

BACKEND  := backend
FRONTEND := frontend

.PHONY: help install lint test build deploy-backend seed invoke-risk dev env-frontend \
        deploy-frontend deploy logs outputs destroy

help:  ## List targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-16s %s\n", $$1, $$2}'

install:  ## Install backend (uv) and frontend (npm) dependencies
	cd $(BACKEND) && uv sync
	cd $(FRONTEND) && npm install

lint:  ## Lint backend, validate SAM template, type-check frontend
	cd $(BACKEND) && uv run ruff check . && uv run ruff format --check . && sam validate --lint
	cd $(FRONTEND) && npx tsc -b

test:  ## Run backend unit tests
	cd $(BACKEND) && uv run pytest

build:  ## Build Lambda artifacts and the frontend bundle
	cd $(BACKEND) && sam build
	cd $(FRONTEND) && npm run build

deploy-backend:  ## sam build + deploy the stack
	cd $(BACKEND) && sam build && sam deploy

seed:  ## Regenerate the Delhi fixture grid and load it into S3 + DynamoDB
	python3 data/scripts/make_hex_grid.py
	cd $(BACKEND) && uv run python ../data/scripts/seed.py --stack $(STACK) --city $(CITY)

invoke-risk:  ## Run the risk engine once now (instead of waiting for the 3-hour schedule)
	cd $(BACKEND) && sam remote invoke RiskEngineFunction --stack-name $(STACK)

dev:  ## Run the frontend locally against the deployed API
	cd $(FRONTEND) && npm run dev

env-frontend:  ## Write frontend/.env.production from the stack's ApiUrl output
	@url=$$(aws cloudformation describe-stacks --stack-name $(STACK) \
	  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text) && \
	echo "VITE_API_URL=$$url" > $(FRONTEND)/.env.production && \
	cp $(FRONTEND)/.env.production $(FRONTEND)/.env.local && \
	echo "VITE_API_URL=$$url"

deploy-frontend: env-frontend  ## Build and publish to Cloudflare Pages
	cd $(FRONTEND) && npm run build && npx wrangler pages deploy dist --project-name $(PAGES_PROJECT) --branch main

deploy: deploy-backend deploy-frontend  ## Deploy everything

outputs:  ## Show stack outputs
	@aws cloudformation describe-stacks --stack-name $(STACK) --query "Stacks[0].Outputs" --output table

logs:  ## Tail a function's logs: make logs FN=api|risk-engine|alert-dispatcher|whatsapp-webhook
	aws logs tail /aws/lambda/heatshield-dev-$(FN) --follow

destroy:  ## Delete the stack (asks first; Subscribers table is retained)
	@read -p "Delete stack $(STACK) in $(AWS_REGION)? [y/N] " ans && [ "$$ans" = y ]
	cd $(BACKEND) && sam delete --stack-name $(STACK) --no-prompts
