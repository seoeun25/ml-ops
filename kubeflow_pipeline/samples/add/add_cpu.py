"""
# $ python add_cpu.py
# This will upload add_cpu.yaml. Check this on kubeflow-pipeline-ui
#
"""

import kfp
from kfp.components import create_component_from_func
from kubernetes.client import V1Toleration, V1Affinity, V1NodeSelector, V1NodeSelectorRequirement, V1NodeSelectorTerm

def kfp_client():
    """
    Kubeflow pipelines client inside cluster.
    """
    end_point="http://ml-pipeline.kubeflow.svc.cluster.local:8888"
    credentials = kfp.auth.ServiceAccountTokenVolumeCredentials(path=None)
    client = kfp.Client(host=end_point, credentials=credentials)

    return client

def add(a: float, b: float) -> float:
    '''Calculates sum of two arguments'''
    return a + b

add_op = create_component_from_func(add, output_component_file='add_component.yaml')

import kfp.dsl as dsl
@dsl.pipeline(name="First Addition pipeline - python function base", description="example of python function based pipeline")
def add_pipeline(a='1', b='7',):
    toleration = V1Toleration(
        effect='NoSchedule',
        key='cpu.aladin.skt/type',
        value='common'
    )
    # toleration1 = V1Toleration(
    #     effect='NoSchedule',
    #     key='gpu.aladin.skt/type',
    #     value='v100'
    # )

    first_add_task = add_op(a, 4)
    first_add_task.add_toleration(toleration)
    #first_add_task.add_toleration(toleration1)
    first_add_task.set_cpu_request("4").set_cpu_limit("4").set_memory_request("16G").set_memory_limit("16G")
    second_add_task = add_op(first_add_task.output, b)

# Specify argument values for your pipeline run.
arguments = {'a': '7', 'b': '8'}

# Create a pipeline run, using the client you initialized in a prior step.
client=kfp_client()
kfp.compiler.Compiler(mode=kfp.dsl.PipelineExecutionMode.V1_LEGACY).compile(add_pipeline, "./add_cpu.yaml")
client.upload_pipeline(pipeline_package_path="./add_cpu.yaml", pipeline_name="add_cpu", description="Addition Python function based pipeline")
