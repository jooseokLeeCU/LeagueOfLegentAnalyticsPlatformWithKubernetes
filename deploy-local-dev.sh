#!/bin/sh
#
# You can use this script to launch Redis and minio on Kubernetes
# and forward their connections to your local computer. That means
# you can then work on your worker-server.py and rest-server.py
# on your local computer rather than pushing to Kubernetes with each change.
#
# To kill the port-forward processes us e.g. "ps augxww | grep port-forward"
# to identify the processes ids
#

# kubectl apply -f minio/minio-external-service.yaml

kubectl apply -f logs/logs-deployment.yaml
kubectl apply -f redis/redis-deployment.yaml
kubectl apply -f redis/redis-service.yaml

kubectl apply -f mysql/mysql-R1-pv.yaml
kubectl apply -f mysql/mysql-R1-deployment.yaml
kubectl apply -f mysql/mysql-R1-service.yaml

kubectl apply -f mysql/mysql-R2-pv.yaml
kubectl apply -f mysql/mysql-R2-deployment.yaml
kubectl apply -f mysql/mysql-R2-service.yaml

kubectl apply -f worker/R1-deployment.yaml
kubectl apply -f worker/R1-service.yaml

kubectl apply -f worker2/R2-deployment.yaml
kubectl apply -f worker2/R2-service.yaml


# kubectl apply -f cassandra/cassandra-pv.yaml
# kubectl apply -f cassandra/cassandra-statefulset.yaml
# kubectl apply -f cassandra/cassandra-service.yaml

# kubectl port-forward --address 0.0.0.0 service/mysql 3306:3306 &
# kubectl port-forward --address 0.0.0.0 service/cassandra 9042:9042 &

# If you're using minio from the kubernetes tutorial this will forward those
# kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9000:9000 &
# kubectl port-forward -n minio-ns --address 0.0.0.0 service/minio-proj 9001:9001 &