"""
 $ python addition_pipeline.py
 This will upload addition_pipeline.yaml. Check this on kubeflow-pipeline-ui
#
"""

import kfp
from kfp.components import create_component_from_func

def kfp_client():
    """
    Kubeflow pipelines client inside cluster.
    """
    end_point="http://ml-pipeline.kubeflow.svc.cluster.local:8888"
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
    client = kfp.Client(host=end_point, credentials=credentials)

    return client


# Create a pipeline run, using the client you initialized in a prior step.
client=kfp_client()
## experiments
list_experiments = client.list_experiments()
print("experiments", )
for i in range(list_experiments.total_size):
    print(list_experiments.experiments[i].id, list_experiments.experiments[i].name)
# create experiment
#client.create_experiment(name="add_org", description="addition pipeline using python function base")
# delete
client.delete_experiment("8c096520-057e-48bf-b8ae-b9ca1f92bd40")

# creat run. not pipeline
#client.create_run_from_pipeline_func(add_pipeline, arguments=arguments)
# compile: create pipeline.yaml
