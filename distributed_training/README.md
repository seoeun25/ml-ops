# Distributed Training

kubeflow 에서 분산학습 적용하기
https://v1-7-branch.kubeflow.org/docs/components/training/

## pytorch operation

### mnist
mnist pipeline 예제

#### Create Pipeline

```
$ cd pytorch-op/mnist
$ python pytorch_mnist_pipeline.py
```
kubeflow 의 pipelines 에서 pytorch_mnist_pipeline 확인한후, 파이프라인을  run 한다.

#### PytorchJob 으로 monitoring

```
$ kubectl get pytorchjob -n <namespace>
NAME                                                 STATE       AGE
pytorch-mnist-201c21b1-b234-40ec-a364-e7160c14693e   Succeeded   7h11m
pytorch-mnist-8529c57a-b42a-4311-9503-b07fe11dc046   Succeeded   7h16m
pytorch-mnist-f21d9731-e7a8-480d-9c49-99a3a575c584   Succeeded   6h34m
```

* 개별 job 으로 status 보기
```
$ kubectl get pytorchjobs -o yaml pytorch-mnist-201c21b1-b234-40ec-a364-e7160c14693e -n <namespace>

```

* pod의 owner 정보로 해당 pytorchjob 알아보기
```
$ kubectl get po -oyaml pytorch-mnist-1381df7d-a04b-4947-bfcf-746774cdf612-master-0 -n <namespace>
```

* pytorch job 삭제하기

해당 pytorch job으로 실행된 pod들 모두 삭제됨.
```
$ kubectl delete pytorchjob pytorch-mnist-1381df7d-a04b-4947-bfcf-746774cdf612 -n seoeun
```

#### kubernetes yaml로 실행
https://v1-7-branch.kubeflow.org/docs/components/training/pytorch/

```
kubectl create -f distribued_training/simple.yaml
```

