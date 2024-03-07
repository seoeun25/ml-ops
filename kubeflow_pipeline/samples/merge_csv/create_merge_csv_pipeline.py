import kfp
import merge_csv_pipeline

kfp.compiler.Compiler().compile(
    pipeline_func=merge_csv_pipeline.my_pipeline("/Users/seoeun/mywork/aladin/pipeline/samples/merge_csv/component.yaml"),
    package_path='pipeline.yaml')