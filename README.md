# LLM Alerting

## Description
Leveraging LLMs on GCP to gernerate meaningful guidance for each alerting in order to accelerate problem solving rather than a simple alerting message.

## Prerequisite 

- docker
- gcloud
- skaffold


## Deployment
```bash
# 1. Modify initial setting in bin/config.env
vi bin/config.env

# 2. Update all related parametes.
bin/config.sh var

# 3. Deploy llm-alerting Cloud Run.
bin/config.sh run

# 4. Create a GKE cluster for demo (Ignore this step if using existed GKE)
bin/config.sh demo

# 5. Create a notification channel and alerting policy for demo.
config.sh alert


```