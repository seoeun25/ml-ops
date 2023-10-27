import kfp.components
import merge_csv_component

#component_url="https://github.com/seoeun25/pipeline/blob/master/samples/merge_csv/component.yaml"
file="/Users/seoeun/mywork/aladin/pipeline/samples/merge_csv/component.yaml"
web_downloader_op= kfp.components.load_component_from_file(file)

# Define a pipeline and create a task from a component
def my_pipeline(file):
    web_downloader_task = web_downloader_op(file=file)
    merge_csv_task = merge_csv_component.create_step_merge_csv(file=web_downloader_task.outputs['data'])
    # The outputs of the merge_csv_task can be referenced using the
    # merge_csv_task.outputs dictionary: merge_csv_task.outputs['output_csv']