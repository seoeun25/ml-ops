###
# $ dsl-compile --py add.py --output add_pipeline.yaml
# Need manually upload add_pipeline.yaml on kubeflow-pipeline-ui
#
###
import kfp
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

from kfp.dsl import pipeline
@pipeline(name="add example", description="example of addition calculation")
def my_pipeline(a: int, b: int):
    task_1 = add_op(a, b)
    task_2 = substract_op(a, b)
    task_3 = multiply_op(task_1.output, task_2.output)

## $ dsl-compile --py add.py --output add_pipeline.yaml
## upload add_pipeline.yaml on kubeflow-pipeline-ui