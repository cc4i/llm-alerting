#!/bin/bash

SERVICE_NAME=llm-alerting
REGION=asia-southeast1
PROJECT_ID=play-dev-ops

# Parse input arguments 
ACTION=$1


# Build base image for Cloud Run
function build_image()
{
    IMG=${REGION}-docker.pkg.dev/${PROJECT_ID}/k8s-asst/${SERVICE_NAME}-base
    docker build -t ${IMG} -f run.Dockerfile .
    docker push ${IMG}
}

# Provision a new GKE cluster for demo
function create_gke_cluster()
{
    echo "nothing"
}

# Replaces variables in the all related files
function config_variables()
{
    echo "nothing" 
}

# Created a new policy and bind to the service
function create_policy()
{
    CLOUR_RUN=`gcloud run services describe  ${SERVICE_NAME} \
                    --platform managed \
                    --region ${REGION} \
                    --format 'value(status.url)'`
}


# Take action based on the input argument
if [ ${ACTION} == "build" ]
then
    build_image
elif [ ${ACTION} == "create" ]
then
    create_gke_cluster
elif [ ${ACTION} == "config" ]
then
    config_variables
elif [ ${ACTION} == "policy" ]
then
    create_policy
fi
