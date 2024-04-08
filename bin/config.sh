#!/bin/bash

SERVICE_NAME=llm-alerting
REGION= asia-southeast1
PROJECT_ID=play-dev-ops

# Build base image for Cloud Run
build_image()
{
    IMG=${REGION}-docker.pkg.dev/${PROJECT_ID}/k8s-asst/${SERVICE_NAME}-base:v1
    docker build -t ${IMG} -f run.Dockerfile .
    docker push ${IMG}
}

# Provision a new GKE cluster for demo
create_gke_cluster()
{

}

# Replaces variables in the all related files
config_variables()
{
    # 1. replace variables in the config file
    # 2. 
}

# Created a new policy and bind to the service
create_policy()
{
    CLOUR_RUN=`gcloud run services describe  ${SERVICE_NAME} \
                    --platform managed \
                    --region ${REGION} \
                    --format 'value(status.url)'`
}

