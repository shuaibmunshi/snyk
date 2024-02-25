Goals:

* Have an EKS/GKE Kubernetes cluster using AWS/GCP cloud (free tier).

* Have 2 services: "service-a" and "service-b".

* For “service-a”: Write a script/application that retrieves the bitcoin value in dollars from an API on the web (any API of your choice) every minute and displays it.

* “service-b” should redirect requests from service-b/rate to service-a/rate and simply return “nothing here” for anything else (/*).