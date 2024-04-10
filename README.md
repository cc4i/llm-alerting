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
export PROJECT_ID=<_YOUR_PROJECT_ID>
export REGION=<_YOUR_GKE_CLUSTER>
export WEBHOOK_URL=<_YOUR_CHAT_WEBHOOK_URL>

# 1. Update all related parametes.
bin/config.sh var

# 2. Deploy llm-alerting Cloud Run.
bin/config.sh run

# 3. Create a GKE cluster for demo (Ignore this step if using existed GKE)
bin/config.sh demo

# 4. Create a notification channel and alerting policy for demo.
config.sh alert


```