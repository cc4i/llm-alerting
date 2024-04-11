# Building an intelligent alerting with Gemini & Function calling

## Description
Leveraging LLMs on GCP to gernerate meaningful guidance for each alerting in order to accelerate problem solving rather than a simple alerting message.

## Prerequisite 

- [Docker](https://docs.docker.com/engine/install/)
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [Skaffold](https://skaffold.dev/docs/install/)


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