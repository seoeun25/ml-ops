"""
This is kubeflow pipeline built using python sdk.
We define a stand-alone python function which is converted to pipeline component.

1. create persistent volume on Kubeflow Volumes UI
    name: test-data-volume
2. Execute below command inside kubeflow cluster.
    $ python iris_python_pipeline.py
This will create iris_python pipeline and upload it. Check this on Kubeflow Pipeline UI.
"""

import kfp.compiler
from kfp.components import create_component_from_func
import kfp

def kfp_client():
    """
    Kubeflow pipelines client inside cluster.
    """
    ## TODO os.environ
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

def load_data(id_from: int, id_to: int) -> str:
    print("data_from={}, data_to={}".format(id_from, id_to))
    import os
    import pandas as pd
    from pathlib import Path

    catalog_name = "aidp_bigquery"
    schema_name = "aladin"
    label_table_name = 'iris'
    metadata_table_name = 'iris_metadata'
    columns = ['Id', 'SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm', 'Species']

    def load_helper(id_from: int, id_to: int):
        # Fetch iris dataset from trino (federated query)
        query = f"SELECT t.id, m.sepallengthcm, m.sepalwidthcm, m.petallengthcm, m.petalwidthcm, t.species \
        FROM {catalog_name}.{schema_name}.{label_table_name} t \
        JOIN {catalog_name}.{schema_name}.{metadata_table_name} m on m.id = t.id \
        WHERE m.id >= {id_from} AND m.id <= {id_to}"

        cursor = conn.cursor()
        cursor.execute(query)

        # Convert data to a pandas dataframe
        df = pd.DataFrame(cursor.fetchall(), columns=columns)

        # Write iris dataset to csv file
        df.to_csv(iris_csv_file, index=False)

    from aladin import trino
    conn = trino.connect(catalog=catalog_name, schema=schema_name)
    id_from = int(os.environ.get("data_id_from", '1'))
    id_to = int(os.environ.get("data_id_to", '150'))
    iris_csv_file = os.environ.get("iris_csv_file", '/data/dataset/iris.csv')
    print("iris_csv_file(os,environ)=", iris_csv_file)
    print("iris_csv_file(default)=", os.environ.get("iris_csv_file", "default_csv"))

    Path(iris_csv_file).parent.mkdir(parents=True, exist_ok=True)
    load_helper(id_from, id_to)
    # Close trino connection
    conn.close()
    print("hello load_data. saved=", iris_csv_file)
    return iris_csv_file

def train_model(iris_csv_file: str) -> str:
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import accuracy_score
    import pickle
    import pandas as pd
    from pathlib import Path
    import os
    def read_helper(iris_csv_file):
        iris = pd.read_csv(iris_csv_file, sep=',')
        print(iris.shape)
        return iris
    def get_train_test_data_helper(iris):
        encode = LabelEncoder()
        iris.Species = encode.fit_transform(iris.Species)

        train , test = train_test_split(iris, test_size=0.2, random_state=0)
        print('shape of training data : ', train.shape)
        print('shape of testing data', test.shape)

        X_train = train.drop(columns=['Species'], axis=1)
        y_train = train['Species']
        X_test = test.drop(columns=['Species'], axis=1)
        y_test = test['Species']

        return X_train, X_test, y_train, y_test

    iris_csv_file = '/data/dataset/iris.csv'
    model_pickle = '/data/models/model.pkl'

    iris_data = read_helper(iris_csv_file)
    iris_data.drop(columns='Id', inplace=True)

    X_train, X_test, y_train, y_test = get_train_test_data_helper(iris_data)

    model = LogisticRegression(max_iter=5000)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Create metric file to check in UI
    from aladin import metric

    metric.update(key='accuracy-score', value=accuracy, percent=True)
    metric.update(key="power", value=0.5, percent=False)
    metric.dump()
    # Save trained model
    Path(model_pickle).parent.mkdir(parents=True, exist_ok=True)
    with open(model_pickle, 'wb') as file:
        pickle.dump(model, file)

    import numpy as np

    with open("/data/models/model.pkl", "rb") as file:
        m = pickle.load(file)
    req = pd.DataFrame(columns=["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"], data= [[5.6, 1.0, 3.5, 1.7]])
    iris_type = {
        0: 'setosa',
        1: 'versicolor',
        2: 'virginica'
    }

    proba = m.predict_proba(req)
    print(iris_type[np.argmax(proba)])
    print(round(max(proba[0]),4))

    return model_pickle

def upload_to_msp(model_file: str):
    import subprocess
    import os
    import time

    print("pwd = ", subprocess.check_output("pwd", shell=True))
    output_path="./aladin_msp"
    model_path = "/data/models"
    command = "aladin msp init -i {}".format(model_path)
    result = subprocess.check_output(command, shell=True)
    print("aladin msp init = ", result)

    command = "aladin msp deploy -d aladin_msp -n 'iris-python'"
    result = subprocess.check_output(command, shell=True)
    print("aladin msp deploy = ", result)
    time.sleep(1)
    print(output_path, os.listdir(output_path))
    print("{}/code".format(output_path), os.listdir("{}/code".format(output_path)))

base_image = base_image()
load_data_op = create_component_from_func(load_data, base_image=base_image)
train_model_op = create_component_from_func(train_model, base_image=base_image)
upload_to_msp_op = create_component_from_func(upload_to_msp, base_image=base_image)

import kfp.dsl as dsl
@dsl.pipeline(name='iris-python-pipeline', description='An example pipeline using python function.')
def my_pipeline(id_from: int, id_to: int):
    print("my_pipeline: id_from={}, id_to={}".format(id_from, id_to))
    data_op = dsl.VolumeOp(name="data-pvc",
                           resource_name="test-data-volume",
                           generate_unique_name=False,
                           action='apply',
                           size="2Gi",
                           modes=dsl.VOLUME_MODE_RWO)
    task_1 = load_data_op(id_from, id_to).add_pvolumes({"/data": data_op.volume})
    task_2 = train_model_op(task_1.output).add_pvolumes({"/data": data_op.volume})
    task_3 = upload_to_msp_op(task_2.output).add_pvolumes({"/data": data_op.volume})

if __name__ == "__main__":
    kfp.compiler.Compiler(mode=kfp.dsl.PipelineExecutionMode.V1_LEGACY).compile(my_pipeline, "./iris_python.yaml")
    client = kfp_client()
    client.upload_pipeline(pipeline_package_path="./iris_python.yaml", pipeline_name="iris_python", description="Iris python function based pipeline")

