# Project 3 REST API with AWS running on local stack

## Overview
Flask REST API with CRUD operation backed by Dynamodb and S3,
emulated locally via local stack. Built for foundations of cloud computing
Summer 2026. This program supports GET, POST, PUT AND DELETE actions
as well as runs automated tests for these actions. Test results are run in Github actions and
results are sent to slack.

## Design Decisions
- Items are uniquely identified by a server generated UUID (id) 
and must have a unique name
- GET supports '"id=' or '?name=' query params; 'id' takes precedence if both given.
-PUT? Delete are path based

## Setup
1. Sign up for a free local stack account and get an auth token
2. create a .env file in this directory with your auth token
LOCALSTACK_AUTH_TOKEN=your-token-here
SLACK_WEBHOOK_URL=your-webhook-here

## running the stack
```bash
./run_stack.sh
```

runs the API + local stack until manually stopped wth ctrl+c

## running tests
```bash
./run_tests.sh
```

runs the test suit in a fresh containerized stack posts results to slack and exits with pytest
status code

## CI/CD
Tests run automatically when pushed to github. Runs via Github actions. Can also be 
triggered manually from actions tab.

