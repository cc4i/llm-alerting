# An intelligent alerting with Gemini & Function calling

## Description
Leveraging LLMs on GCP to gernerate meaningful guidance for each alerting in order to accelerate problem solving rather than a simple alerting message.

## Architecture
![architecture](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*aJZ7D70lyjp8-R6vJa669g.png)

## Prerequisite 

- [Docker](https://docs.docker.com/engine/install/)
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [Skaffold](https://skaffold.dev/docs/install/)


## Deployment
```bash
# 1. Modify initial setting in bin/config.env
#
# Notice: 
# To replace webhook url, I use sed here. In sed's replacement section, the '&' represents the entire text that matched your search pattern. To include a literal '&' in the replacement, you need to escape it with a backslash.
#

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

## Advanced 

Make sure your have enough [quota for Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/quotas) to run more Funtion Calling, such as [main-ext.py](./main-ext.py). Otherwise you would meet following error: 

```

google.api_core.exceptions.ResourceExhausted: 429 Quota exceeded for aiplatform.googleapis.com/generate_content_requests_per_minute_per_project_per_base_model with base model: gemini-pro. Please submit a quota increase request. https://cloud.google.com/vertex-ai/docs/generative-ai/quotas-genai.
```