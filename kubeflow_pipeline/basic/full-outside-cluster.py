import istio_auth
import kfp

KUBEFLOW_ENDPOINT = "http://localhost:8080"
#KUBEFLOW_ENDPOINT = "https://kubeflow.ml.dev.aladin.apollo-ai.io/"
KUBEFLOW_USERNAME = "seoeun@sk.com"
KUBEFLOW_PASSWORD = "Sk181001!!"
client_namespace="seoeun"

auth_session = istio_auth.get_istio_auth_session(
    url=KUBEFLOW_ENDPOINT,
    username=KUBEFLOW_USERNAME,
    password=KUBEFLOW_PASSWORD
)
print(auth_session);

client = kfp.Client(host=f"{KUBEFLOW_ENDPOINT}/pipeline", cookies=auth_session["session_cookie"])
print(client.list_experiments())

#client = kfp.Client(
#    host=f"{KUBEFLOW_ENDPOINT}/pipeline", cookies=auth_session["session_cookie"], namespace=client_namespace
#)
#print(client.list_pipelines())
