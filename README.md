Goals:

* Have an EKS/GKE Kubernetes cluster using AWS/GCP cloud (free tier).

* Have 2 services: "service-a" and "service-b".

* For “service-a”: Write a script/application that retrieves the bitcoin value in dollars from an API on the web (any API of your choice) every minute and displays it.

* “service-b” should redirect requests from service-b/rate to service-a/rate and simply return “nothing here” for anything else (/*).

```
╭─ ~/Documents/projects/snyk/service-b master !1 ?1                                             ○ gke-cluster-fc50b24
╰─❯ kubectl get ingress basic-ingress
NAME            CLASS    HOSTS   ADDRESS        PORTS   AGE
basic-ingress   <none>   *       34.49.136.69   80      3d23h
```
```
╭─ ~/Documents/projects/snyk/service-b master !1 ?1                                                                  
╰─❯ curl http://34.49.136.69/rate
61376.48520255%                                                               
╰─❯ curl http://34.49.136.69/test
nothing here%  
```
