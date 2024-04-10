#!/bin/bash

source bin/config.env

# Parse input arguments 
ACTION=$1


# Build base image for Cloud Run
function build_image()
{
    IMG=${REGION}-docker.pkg.dev/${PROJECT_ID}/k8s-asst/${SERVICE_NAME}-base
    docker build -t ${IMG} -f run.Dockerfile .
    docker push ${IMG}
}

# Deploy Cloud Run service
function deploy_run_service()
{
    skaffold build
    skaffold run
    gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
        --region ${REGION} \
        --project ${PROJECT_ID} \
        --member="allUsers" \
        --role="roles/run.invoker"
}

# Provision a new GKE cluster for demo
function create_gke_cluster()
{
    echo "Create a GKE Autopilot for demo"
    gcloud beta container clusters create-auto "gke-autopilot-demo" \
        --project ${PROJECT_ID} \
        --region ${REGION}
    
    echo "Deploy a sample application"
    echo "..."
}

# Replaces variables in the all related files
function config_variables()
{
    echo "Replace variables in the all related files"
    sed -i 's/<_REGION>/'${REGION}'/g' bin/config.env
    sed -i 's/<_PROJECT_ID>/'${PROJECT_ID}'/g' bin/config.env
    sed -i 's/<_WEBHOOK_URL>/'${WEBHOOK_URL}'/g' bin/config.env
 
    sed -i 's/<_REGION>/'${REGION}'/g' resources/cloud-run-service.yaml
    sed -i 's/<_PROJECT_ID>/'${PROJECT_ID}'/g' resources/cloud-run-service.yaml
    sed -i 's/<_WEBHOOK_URL>/'${WEBHOOK_URL}'/g' resources/cloud-run-service.yaml

    sed -i 's/<_REGION>/'${REGION}'/g' skaffold.yaml
    sed -i 's/<_PROJECT_ID>/'${PROJECT_ID}'/g' skaffold.yaml


}

# Created a new policy and bind to the service
function create_policy()
{
    # Get the Cloud Run service URL
    CLOUR_RUN=`gcloud run services describe  ${SERVICE_NAME} \
                    --platform managed \
                    --region ${REGION} \
                    --format 'value(status.url)'`
    # Get the project number
    # https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects
    PROJECT_NUMBER=`gcloud projects describe ${PROJECT_ID} --format="value(project_number)"`

    # Create a Pub/Sub topic
    gcloud pubsub topics create gke-monitor-ps \
        --project ${PROJECT_ID}

    # Binding the service account to the topic in order to publish messages by Incident Policy
    gcloud pubsub topics add-iam-policy-binding \
        projects/${PROJECT_NUMBER}/topics/gke-monitor-ps \
        --role=roles/pubsub.publisher \
        --member=serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-monitoring-notification.iam.gserviceaccount.com

    # Create a Pub/Sub subscription and bind with Cloud Run
    gcloud pubsub subscriptions create gke-monitor-ps-sub \
        --topic gke-monitor-ps \
        --push-endpoint ${CLOUR_RUN} \
        --message-encoding json \
        --payload-format none

    # Create a notification channel
    # https://cloud.google.com/monitoring/support/notification-options#channels
    gcloud alpha monitoring channels create gke-monitor-channel \
        --project ${PROJECT_ID} \
        --display-name "gke-monitor-channel" \
        --type "pubsub" \
        --topic-name "projects/${PROJECT_ID}/topics/gke-monitor-ps"
    NOTIFICATION_CHANNEL_ID=`gcloud alpha monitoring channels list \
        --project ${PROJECT_ID} \
        --format json |jq -c '.[]|select(.displayName == "gke-monitor-channel")'|jq -r -c '.name'`
    sed -i 's/<_PROJECT_ID>/'${PROJECT_ID}'/g' bin/alert-policy.json
    sed -i 's/<_NOTIFICATION_CHANNEL_ID>/'${NOTIFICATION_CHANNEL_ID}'/g' bin/alert-policy.json

    # Create a incident policy
    # https://cloud.google.com/monitoring/alerts/using-alerting-api#incident_policies
    gcloud alpha monitoring policies create "pod-restart-policy" \
        --project ${PROJECT_ID} \
        --policy-from-file bin/alert-policy.json

    echo "Policy created"
}


#  ACTION is the first argument of the script
if [ $# -ne 1 ]
then
    echo "Usage: $0 {run|demo|var|alert}"
    exit 1
fi

#
# "run" to build image and deploy to CR
if [ ${ACTION} == "run" ]
then
    build_image
    deploy_run_service

# "demo" to provision a new GKE cluster for demo
elif [ ${ACTION} == "demo" ]
then
    create_gke_cluster

# "var" to replace variables in the all related files
elif [ ${ACTION} == "var" ]
then
    config_variables

# "alert" to create a new policy and bind to the service
elif [ ${ACTION} == "alert" ]
then
    create_policy
fi
