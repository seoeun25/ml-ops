"""
# $ python addition_pipeline.py
# This will upload addition_pipeline.yaml. Check this on kubeflow-pipeline-ui
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

def add(a: float, b: float) -> float:
    '''Calculates sum of two arguments'''
    return a + b

add_op = create_component_from_func(add, output_component_file='add_component.yaml')

import kfp.dsl as dsl
@dsl.pipeline(name="First Addition pipeline - python function base", description="example of python function based pipeline")
def add_pipeline(
        a='1',
        b='7',
):
    # Passes a pipeline parameter and a constant value to the `add_op` factory
    # function.
    first_add_task = add_op(a, 4)
    # Passes an output reference from `first_add_task` and a pipeline parameter
    # to the `add_op` factory function. For operations with a single return
    # value, the output reference can be accessed as `task.output` or
    # `task.outputs['output_name']`.
    second_add_task = add_op(first_add_task.output, b)

# Specify argument values for your pipeline run.
arguments = {'a': '7', 'b': '8'}

# Create a pipeline run, using the client you initialized in a prior step.
client=kfp_client()
## experiments
list_experiments = client.list_experiments()
print("experiments", )
for i in range(list_experiments.total_size):
    print(list_experiments.experiments[i].id)
# create experiment
#client.create_experiment(name="add_org", description="addition pipeline using python function base")

# creat run. not pipeline
#client.create_run_from_pipeline_func(add_pipeline, arguments=arguments)
# compile: create pipeline.yaml
kfp.compiler.Compiler(mode=kfp.dsl.PipelineExecutionMode.V1_LEGACY).compile(add_pipeline, "./addition_pipeline.yaml")
client.upload_pipeline(pipeline_package_path="./addition_pipeline.yaml", pipeline_name="addition_pipeline", description="Addition Python function based pipeline")
