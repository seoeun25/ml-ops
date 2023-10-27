# Kubeflow pipeline example

## basic
Inside cluster만 working. 
kubeflow outside cluster 에서 kubeflow로 호출하는 걸 테스트 하였으나 동작하지 않음.
- central dashboard: istio-ingressgateway
    - [https://kubeflow.ml.dev.aladin.apollo-ai.io](https://kubeflow.ml.dev.aladin.apollo-ai.io/?ns=seoeun)
- API_ENDPOINT: ml-pipline ??
    - ml-pipeline (내부  IP): 10.100.108.186:8888(8887)
    - [http://ml-pipeline.kubeflow.svc.cluster.local:8888](http://ml-pipeline.kubeflow.svc.cluster.local:8888/)
- ml-pipeline-ui
    - 10.100.62.98: 80

## samples
### add
add function을 step으로 구성.

### iris_python
iris 예제를 python function based pipeline로 구현. 

### edd_monitor
edd dataloading monitoring

### merge_csv
Not working. 코드만 참조.

### test
각종 테스트.
 
