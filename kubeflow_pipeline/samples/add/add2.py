###
# $ python add_2.py
# Need manually upload add_pipeline_2.yaml on kubeflow-pipeline-ui
#
###
import kfp.compiler
from kfp.components import create_component_from_func

def add(a: int, b: int) -> int:
    ret = a + b
    return ret

def substract(a: int, b: int) -> int:
    ret = a - b
    return ret

def multiply(a: int, b: int) -> int:
    return a * b

add_op = create_component_from_func(add)
substract_op = create_component_from_func(substract)
multiply_op = create_component_from_func(multiply)

import kfp.dsl as dsl
@dsl.pipeline(name='Addition pipeline', description='An example pipeline that perform addition calculations')
def my_pipeline(a: int, b: int):
    task_1 = add_op(a, b)
    task_2 = substract_op(a, b)
    task_3 = multiply_op(task_1.output, task_2.output)

if __name__ == "__main__":
    kfp.compiler.Compiler(mode=kfp.dsl.PipelineExecutionMode.V1_LEGACY).compile(my_pipeline, "./add_pipeline_2.yaml")
