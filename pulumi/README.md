# Pulumi
## Installation
- curl -fsSL https://get.pulumi.com | sh
- alias pulumi="/home/shuaib/.pulumi/bin/pulumi"
## Usage
- pulumi new kubernetes-gcp-python
- pulumi config set gcp:project resonant-gizmo-415423
- pulumi up
# GKE
## Gcloud Install/Config
- curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-465.0.0-linux-x86_64.tar.gz
- ./google-cloud-sdk/install.sh
- gcloud auth application-default login
- gcloud auth login --brief
- gcloud components install kubectl
- gke-gcloud-auth-plugin --version # Make sure gcloud installed the auto plugin during installation
- gcloud container clusters get-credentials gke-cluster-fc50b24 --region=northamerica-northeast2 --project resonant-gizmo-415423 # There's a bug in the GCP documentation here, --project is required but not in the docs
- kubectl get namespaces