# LLM Alerting

## Description
Leveraging LLMs on GCP to gernerate meaningful guidance for each alerting in order to accelerate problem solving rather than a simple alerting message.

## Prerequisite 


## Deployment
```bash
# 1. Configure parameters as initial setting
export _PROJECT_ID=
export _REGION=asia-southeast1

# 1. Update all related parametes
config.sh variable

# 2. Create a notification channel and alerting policy
config.sh policy

# 3. Deploy llm-alerting to handle alerting message
skaffold build
skaffold run

```