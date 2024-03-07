import kfp

## no need credentail
client = kfp.Client(host="http://ml-pipeline-ui:80")

print(client.list_experiments())