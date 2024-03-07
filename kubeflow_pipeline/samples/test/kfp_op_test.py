"""
$ python iris_python_pipeline.py
# This will upload iris_python.yaml. Check this on kubeflow-pipeline-ui
"""

import kfp.compiler
from kfp.components import create_component_from_func
import kfp

def kfp_client():
    """
    Kubeflow pipelines client inside cluster.
    """
    ## TODO
    end_point="http://ml-pipeline.kubeflow.svc.cluster.local:8888"
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
    client = kfp.Client(host=end_point, credentials=credentials)

    return client
def base_image() -> str:
    import os
    import re

    iam = os.environ.get("AWS_ROLE_ARN")
    account = re.findall("arn:aws:iam::(.*):role*", iam)[0]
    region = os.environ.get("AWS_REGION")
    base_image = "{}.dkr.ecr.{}.amazonaws.com/aladin-runtime:anaconda-cpu".format(account, region)
    print("base_image={}".format(base_image))
    return base_image
def volume_test(model_file: str):
    import subprocess
    import os

    print("pwd = ", subprocess.check_output("pwd", shell=True))

    # list file and directories
    data_path="/data"
    print("dir={} :: ".format(data_path), os.listdir(data_path))

def delete_file(file:str):
    import subprocess
    import os

    print("pwd = ", subprocess.check_output("pwd", shell=True))

    # list file and directories
    data_path="/data"
    print("dir={} :: ".format(data_path), os.listdir(data_path))

base_image = base_image()
volume_test_op = create_component_from_func(volume_test, base_image=base_image)

import kfp.dsl as dsl
@dsl.pipeline(name='my-pipeline', description='An example pipeline')
def my_pipeline(id_from: int, id_to: int):
    print("my_pipeline: id_from={}, id_to={}".format(id_from, id_to))
    data_op = dsl.VolumeOp(name="data-pvc",
                           resource_name="data-volume",
                           generate_unique_name=False,
                           action='apply',
                           size="2Gi",
                           modes=dsl.VOLUME_MODE_RWO)
    task_1 = volume_test_op("models").add_pvolumes({"/data": data_op.volume})

arguments = {'id_from': '7', 'id_to': '8'}
if __name__ == "__main__":
    client = kfp_client()
    client.create_run_from_pipeline_func(my_pipeline, experiment_name="test-seoeun", arguments=arguments)


