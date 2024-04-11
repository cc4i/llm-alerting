import os
from typing import Union
from fastapi import FastAPI
import vertexai
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool
import requests
import json

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

# Function to collect information of issued pod and analyse
collect_pod_information_func = FunctionDeclaration(
    name="collect_pod_information",
    description="""
        Collect pod information from the GKE cluster.
    """,
    parameters={
        "type": "object",
        "properties": {
            "namespace_name": {
                "type": "string",
                "description": "The namespace where the pod is located, which is a lowercase RFC 1123 label must consist of lower case alphanumeric characters or '-', and must start and end with an alphanumeric character (e.g. 'my-name',  or '123-abc', regex used for validation is '[a-z0-9]([-a-z0-9]*[a-z0-9])?')"
            },
            "pod_name": {
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

send_message_to_chat_func = FunctionDeclaration(
    name="send_message_to_chat",
    description="""
        Send the message to Google Chat.
    """,
    parameters={
        "type": "object",
        "properties": {
            "response": {
                "type": "string",
                "description": "The message to send to Google Chat"
            },
            "url": {
                "type": "string",
                "description": "The URL of the Google Chat"
            }
            
        },
        "required": [
            "response",
            "url"
        ],         
    },
)



gke_cluster_tool = Tool (
    function_declarations= [
        get_credentail_func, 
        collect_pod_information_func,
        send_message_to_chat_func
    ]
)

# 1. Initialize the model
PROJECT_ID = os.environ["PROJECT_ID"]  # @param {type:"string"}
REGION =os.environ["REGION"]  # @param {type:"string"}

# 2. Initialize Vertex AI SDK
vertexai.init(project=PROJECT_ID, location=REGION)

# 3. Initialize the model
model = GenerativeModel("gemini-1.0-pro-002", generation_config={"temperature": 0.5}, tools=[gke_cluster_tool])
chat = model.start_chat(response_validation=False)

# 4. Initialize HTTP Server
app = FastAPI()


@app.post("/alerting")
def analyse_alerting(message: Union[str, dict]) -> dict:
    
    prompt = """
        You are a Kubernetes expert and highly skilled in all Google Cloud services, Linux, and shell scripts. 
        Your task is to troubleshoot the problematic pod as per CONTEXT with the following steps: 
        
        1. Configure the credential and connect to the GKE cluster.
        2. Collect the pod information from the GKE cluster.
        3. Provide a summary of pod, a concise explanation of the issue and follow by step by step solutions to address the issues. 
        4. Send the message to Google Chat.
        
        Only use information that provided, do not make up information.

        CONTEXT:
        {}

        """.format(message["incident"]["resource"]["labels"])
    
    response = chat.send_message(prompt)
    print("---------------->")
    print(prompt)
    print("---------------->\n")
    print("----------------<")
    print(response)
    print("----------------<\n")
    response = response.candidates[0].content.parts[0]

    
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


            if response.function_call.name == "collect_pod_information":
                api_response = {
                    "cmd_pod_description": "kubectl describe pods {} -n {}".format(response.function_call.args["pod_name"], response.function_call.args["namespace_name"]),
                    "cmd_pod_logs": "kubectl logs {} -n {}".format(response.function_call.args["pod_name"], response.function_call.args["namespace_name"]),
                    "cmd_events": "kubectl get events -n {}".format(response.function_call.args["namespace_name"]),
                    }
                api_response["pod_description"]=os.popen(api_response["cmd_pod_description"]).read()
                api_response["pod_logs"]=os.popen(api_response["cmd_pod_logs"]).read()
                api_response["events"]=os.popen(api_response["cmd_events"]).read()

            if response.function_call.name == "send_message_to_chat":
                api_response = {"response": response.text, "url": message["incident"]["url"]}
                send_message(api_response)

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

    notification = {"response": response.text, "url": message["incident"]["url"]}
    # send_message(notification)
    return notification


@app.get("/health")
def health_check():
    return {"health": "ok"}

@app.post("/message")
def send_message(notification: Union[str, dict])-> dict:
    webhook_url=os.environ["WEBHOOK_URL"]
    print("----------------------->>")
    print(webhook_url)
    print("----------------------->>")
    print(notification)
    print("----------------------->>")
    message_template={
        "cards": [
            {
                "header": {
                    "title": " Pod Restart Alerting"
                },
                "sections": [
                    {
                        "header": "<b><font color=\"#ff0000\">Incident Summary</font></b>",
                        "widgets": [
                            {
                                "textParagraph": {
                                    "text": notification["response"]
                                }
                            }
                        ]
                    },

                    {
                        "widgets": [
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "GO TO INCIDENT",
                                            "onClick": {
                                                "openLink": {
                                                    "url": notification["url"]
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
        
    response = requests.post(webhook_url, json=message_template, headers={"Content-Type": "application/json"})
    print(response)
    print(response.text)
    return {"status": response.status_code}


