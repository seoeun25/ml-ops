import kfp

# the namespace in which you deployed Kubeflow Pipelines
namespace = "kubeflow"

# the KF_PIPELINES_SA_TOKEN_PATH environment variable is used when no `path` is set
# the default KF_PIPELINES_SA_TOKEN_PATH is /var/run/secrets/kubeflow/pipelines/token
credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
print("credentials=", credentials)
print('hello kfp')

#endpoint="http://ml-pipeline-ui.{}".format(namespace)
## ml-pipelin-ui
#HOST="http://ml-pipeline-ui:80"
#HOST="http://10.100.62.98:80"
## ml-pipeline
#HOST="http://10.100.108.186:8888"
HOST="http://ml-pipeline.kubeflow.svc.cluster.local:8888"
print("endpoint={}".format(HOST))
client = kfp.Client(host=HOST, credentials=credentials)

print(client.list_experiments())
print("--------------")
print(client.list_pipelines())
