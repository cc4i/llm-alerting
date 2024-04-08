# LLM Alerting

## Description
Leveraging LLMs on GCP to gernerate meaningful guidance for each alerting in order to accelerate problem solving rather than a simple alerting message.

## Prerequisite 

- docker
- gcloud
- skaffold


## Deployment
```bash
# 1. Configure parameters as initial setting
export _PROJECT_ID=play-dev-ops
export _REGION=asia-southeast1
export _GKE_CLUSTER=gke-demo
export _PUB_SUB=gke-monitor-ps

# 1. Update all related parametes
config.sh variable

# 2. Deploy llm-alerting to handle alerting message
skaffold build
skaffold run


# 3. Create a notification channel and alerting policy
config.sh policy


```