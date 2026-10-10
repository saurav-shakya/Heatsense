# HeatShield — one entry point for local dev and deploys.
# Backend: AWS SAM (profile saurav-cli, us-east-1). Frontend: Cloudflare Pages (wrangler).

AWS_PROFILE ?= saurav-cli
AWS_REGION  ?= us-east-1
STACK       ?= heatshield-dev
CITY        ?= delhi
PAGES_PROJECT ?= heatshield
FN          ?= api
WARDS_FILE  ?= data/fixtures/delhi_wards.geojson
DATE        ?= 2024-05-28
DATA_DEPS   := --with numpy --with rasterio --with shapely --with pyproj --with pytest

export AWS_PROFILE AWS_REGION
export SAM_CLI_TELEMETRY = 0
SHELL := /bin/bash

BACKEND  := backend
FRONTEND := frontend

.PHONY: help install lint test test-data build deploy-backend fixture seed invoke-risk replay-fetch replay live \
        snapshot invoke-alerts twilio-params sms-setup dev env-frontend deploy-frontend deploy logs outputs destroy

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

test-data:  ## Run the data pipeline tests (rasterio etc. via uv, no network)
	uv run --no-project $(DATA_DEPS) pytest -q -p no:cacheprovider data/tests

build:  ## Build Lambda artifacts and the frontend bundle
	cd $(BACKEND) && sam build
	cd $(FRONTEND) && npm run build

deploy-backend:  ## sam build + deploy the stack
	cd $(BACKEND) && sam build && sam deploy

fixture:  ## Regenerate the synthetic hex-grid ward layer
	python3 data/scripts/make_hex_grid.py

seed:  ## Load a ward layer into S3 + DynamoDB: make seed [WARDS_FILE=data/processed/delhi_wards.geojson]
	cd $(BACKEND) && uv run python ../data/scripts/seed.py --stack $(STACK) --city $(CITY) --file ../$(WARDS_FILE)

invoke-risk:  ## Run the risk engine once now (instead of waiting for the 3-hour schedule)
	cd $(BACKEND) && sam remote invoke RiskEngineFunction --stack-name $(STACK)

replay-fetch:  ## Download a past heatwave from Open-Meteo and upload it: make replay-fetch DATE=2024-05-28
	cd $(BACKEND) && uv run python ../data/scripts/fetch_replay.py --date $(DATE) --stack $(STACK) \
	  --city $(CITY) --file ../$(WARDS_FILE) --upload

replay:  ## Score from the stored heatwave until the next 3-hourly run: make replay DATE=2024-05-28
	cd $(BACKEND) && sam remote invoke RiskEngineFunction --stack-name $(STACK) --event '{"replay": "$(DATE)"}'

live:  ## Score from live forecasts now (ends a one-off replay)
	cd $(BACKEND) && sam remote invoke RiskEngineFunction --stack-name $(STACK) --event '{"replay": ""}'

invoke-alerts:  ## Run the alert dispatcher once now (respects quiet hours and the daily cap)
	cd $(BACKEND) && sam remote invoke AlertDispatcherFunction --stack-name $(STACK)

twilio-params:  ## Store Twilio credentials in SSM Parameter Store (prompts; nothing lands in shell history)
	@read -p "Twilio account SID: " sid && read -s -p "Twilio auth token: " token && echo && \
	read -p "WhatsApp sender (sandbox: +14155238886): " from && \
	for kv in "account-sid=$$sid" "auth-token=$$token" "whatsapp-from=$$from"; do \
	  aws ssm put-parameter --name "/heatshield/dev/twilio/$${kv%%=*}" --type SecureString --overwrite \
	    --value "$${kv#*=}" >/dev/null || exit 1; \
	done && echo "stored /heatshield/dev/twilio/{account-sid,auth-token,whatsapp-from}"

sms-setup:  ## Set SNS SMS to transactional with a 1 USD/month spend cap
	aws sns set-sms-attributes --attributes DefaultSMSType=Transactional,MonthlySpendLimit=1

snapshot:  ## Save a scored forecast as static JSON for the map without an API: make snapshot [REPLAY=2024-05-28]
	cd $(BACKEND) && uv run python ../data/scripts/build_snapshot.py --file ../$(WARDS_FILE) $(if $(REPLAY),--replay $(REPLAY))

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
