import kfp
import requests

USERNAME = "seoeun@sk.com"
PASSWORD = "********"
#NAMESPACE = "kubeflow-user-example-com"
NAMESPACE = "seoeun"
HOST = "https://kubeflow.ml.dev.aladin.apollo-ai.io/" # istio-ingressgateway's external-ip created by the load balancer.
#HOST="http://localhost:38888"
#HOST = "http://localhost:8080" # istio-ingressgateway's external-ip created by the load balancer.

print("username= {0}, namespace= {1}".format(USERNAME, NAMESPACE))

session = requests.Session()
response = session.get(HOST)
print("response", response.url)
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}

data = {"login": USERNAME, "password": PASSWORD}
session.post(response.url, headers=headers, data=data)
print("-- session.cookies", session.cookies)
print(session.cookies.get_dict())
session_cookie = session.cookies.get_dict()["authservice_session"]
print(session_cookie)

client = kfp.Client(
    host=f"{HOST}",
    namespace=f"{NAMESPACE}",
    cookies=f"authservice_session={session_cookie}",
)
print(client.list_pipelines())
