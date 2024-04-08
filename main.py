import os
from typing import Union
from fastapi import FastAPI
import vertexai
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool

# Function to get GKE credential 
get_credentail_func = FunctionDeclaration(
    name="get_credential",
    description="Configure the credential and connect to the GKE cluster.",
    parameters={
        "type": "object",
        "properties": {
            "cluster_name": {
                "type": "string",
                "description": "The name of the Kubernetes cluster"
            },
            "region": {
                "type": "string",
                "description": "The region of the Kubernetes cluster"
            },
            "project_id": {
                "type": "string",
                "description": "The project ID of the Kubernetes cluster"
            },
            "isZonal": {
                "type": "boolean",
                "description": "If the cluster is zonal, set this to True, otherwise set this to False"
            }
        },
        "required": [
            "cluster_name",
            "region",
            "project_id",
            "isZonal"
        ],
        "required": [
            "cluster_name",
            "region",
            "project_id"
        ]
    }
)

# Function to collect infomation of issued pod and analyse
troubleshoot_pod_func = FunctionDeclaration(
    name="troubleshoot_pod",
    description="""
        Troubleshooting the potential issues of the pod through collecting metrics, logs, events, etc. from the GKE cluster.
    """,
    parameters={
        "type": "object",
        "properties": {
            "namespace": {
                "type": "string",
                "description": "The namespace where to list pods, which is a lowercase RFC 1123 label must consist of lower case alphanumeric characters or '-', and must start and end with an alphanumeric character (e.g. 'my-name',  or '123-abc', regex used for validation is '[a-z0-9]([-a-z0-9]*[a-z0-9])?')"
            },
            "name": {
                "type": "string",
                "description": "The name of the pod to get by"
            },
            "kubernetes_context": {
                "type": "string",
                "description": "The kubernetes context to use, defaults to the current context"
            }
        },
        "required": [
            "kubernetes_context"
        ],         
    },
)

gke_cluster_tool = Tool (
    function_declarations= [
        get_credentail_func, 
        troubleshoot_pod_func
    ]
)

# 1. Initialize the model
PROJECT_ID = os.environ["PROJECT_ID"]  # @param {type:"string"}
REGION =os.environ["REGION"]  # @param {type:"string"}

# 2. Initialize Vertex AI SDK
vertexai.init(project=PROJECT_ID, location=REGION)

# 3. Initialize the model
model = GenerativeModel("gemini-1.0-pro", generation_config={"temperature": 0.5}, tools=[gke_cluster_tool])
chat = model.start_chat(response_validation=False)

# 4. Initialize HTTP Server
app = FastAPI()


@app.post("/alerting")
def analyse_alerting(message: Union[str, dict]) -> dict:
    prompt = """
        You are an Kubernetes expert and highly skilled in all Google Cloud services, Linux, and shell scripts. 
        Your task is to answer the question as per conext with a concise and summarized response with actionable step by step guidance. 
        Only use information that we have or you collected from the context, do not make up information.

        QUESTION:
        {}

        Helpful Answer:
        """.format(message)
    
    response = chat.send_message(prompt)
    response = response.candidates[0].content.parts[0]
    print("----------------")
    print(response)
    print("----------------\n")
    function_calling_in_process = True
    while function_calling_in_process:
        try:
            params = {}
            for key, value in response.function_call.args.items():
                params[key] = value
            print(params)

            if response.function_call.name == "get_credential":
                api_response={
                    "get_credential":  "gcloud container clusters get-credentials {} --zone {} --project {}".format(
                        response.function_call.args["cluster_name"],
                        response.function_call.args["region"], 
                        response.function_call.args["project_id"])
                }
                print(api_response["get_credential"])
                print(os.popen(api_response["get_credential"]).read())


            if response.function_call.name == "troubleshoot_pod":
                api_response = {
                    "cmd_pod_description": "kubectl describe pods {} -n {}".format(response.function_call.args["name"], response.function_call.args["namespace"]),
                    "cmd_pod_logs": "kubectl logs {} -n {}".format(response.function_call.args["name"], response.function_call.args["namespace"]),
                    "cmd_events": "kubectl get events -n {}".format(response.function_call.args["namespace"]),
                    }
                api_response["pod_description"]=os.popen(api_response["cmd_pod_description"]).read()
                api_response["pod_logs"]=os.popen(api_response["cmd_pod_logs"]).read()
                api_response["events"]=os.popen(api_response["cmd_events"]).read()


            api_response = str(api_response)
            print(api_response)

            response = chat.send_message(
                        Part.from_function_response(
                            name=response.function_call.name,
                            response={
                                "content": api_response,
                            },
                        ),
                    )
            response = response.candidates[0].content.parts[0]
        except AttributeError:
                    function_calling_in_process = False

    return {"response": response.text}


@app.get("/health")
def health_check():
    return {"health": "ok"}

