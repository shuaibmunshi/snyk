import pulumi
import pulumi_gcp as gcp

# Get some provider-namespaced configuration values
provider_cfg = pulumi.Config("gcp")
gcp_project_name = "snyk"
gcp_project = provider_cfg.require("project")
gcp_region = provider_cfg.get("region", "northamerica-northeast2")
# Get some additional configuration values
config = pulumi.Config()
nodes_per_zone = config.get_int("nodesPerZone", 1)

# Create a new network
gke_network = gcp.compute.Network(
    "gke-network",
    auto_create_subnetworks=False,
    description="A virtual network for your GKE cluster(s)"
)

# Create a subnet in the new network
gke_subnet = gcp.compute.Subnetwork(
    "gke-subnet",
    ip_cidr_range="10.128.0.0/12",
    network=gke_network.id,
    private_ip_google_access=True
)

# https://www.pulumi.com/registry/packages/gcp/api-docs/compute/routernat/
# Create router
gke_router = gcp.compute.Router("router",
    region=gcp_region,
    network=gke_network.id,
    bgp=gcp.compute.RouterBgpArgs(
        asn=64514,
    ))

# NAT
gke_nat = gcp.compute.RouterNat("nat",
    router=gke_router.name,
    region=gcp_region,
    nat_ip_allocate_option="AUTO_ONLY",
    source_subnetwork_ip_ranges_to_nat="ALL_SUBNETWORKS_ALL_IP_RANGES",
    log_config=gcp.compute.RouterNatLogConfigArgs(
        enable=True,
        filter="ERRORS_ONLY",
    ))


# Create a cluster in the new network and subnet
gke_cluster = gcp.container.Cluster(
    "gke-cluster",
    addons_config=gcp.container.ClusterAddonsConfigArgs(
        dns_cache_config=gcp.container.ClusterAddonsConfigDnsCacheConfigArgs(
            enabled=True
        ),
    ),
    binary_authorization=gcp.container.ClusterBinaryAuthorizationArgs(
        evaluation_mode="PROJECT_SINGLETON_POLICY_ENFORCE"
    ),
    datapath_provider="ADVANCED_DATAPATH",
    description="A GKE cluster",
    initial_node_count=1,
    ip_allocation_policy=gcp.container.ClusterIpAllocationPolicyArgs(
        cluster_ipv4_cidr_block="/14",
        services_ipv4_cidr_block="/20"
    ),
    location=gcp_region,
    master_authorized_networks_config=gcp.container.ClusterMasterAuthorizedNetworksConfigArgs(
        cidr_blocks=[gcp.container.ClusterMasterAuthorizedNetworksConfigCidrBlockArgs(
            cidr_block="0.0.0.0/0",
            display_name="All networks"
        )]
    ),
    # router=gke_router,
    # nat=gke_nat,
    network=gke_network.name,
    networking_mode="VPC_NATIVE",
    private_cluster_config=gcp.container.ClusterPrivateClusterConfigArgs(
        enable_private_nodes=True,
        enable_private_endpoint=False,
        master_ipv4_cidr_block="10.100.0.0/28"
    ),
    remove_default_node_pool=True,
    release_channel=gcp.container.ClusterReleaseChannelArgs(
        channel="STABLE"
    ),
    subnetwork=gke_subnet.name,
    workload_identity_config=gcp.container.ClusterWorkloadIdentityConfigArgs(
        workload_pool=f"{gcp_project}.svc.id.goog"
    )
)

# Create a GCP service account for the nodepool
gke_nodepool_sa = gcp.serviceaccount.Account(
    "gke-nodepool-sa",
    account_id=pulumi.Output.concat(gke_cluster.name, "-np-1-sa"),
    display_name="Nodepool 1 Service Account"
)

# Create a nodepool for the cluster
gke_nodepool = gcp.container.NodePool(
    "gke-nodepool",
    cluster=gke_cluster.id,
    node_count=nodes_per_zone,
    node_config=gcp.container.NodePoolNodeConfigArgs(
        machine_type="e2-small",
        disk_size_gb="50",
        oauth_scopes=["https://www.googleapis.com/auth/cloud-platform","https://www.googleapis.com/auth/devstorage.read_only"],
        service_account=gke_nodepool_sa.email
    )
)

# https://www.pulumi.com/registry/packages/gcp/api-docs/compute/firewall/
gke_firewall_rule = gcp.compute.Firewall("pulumi-firewall-rules",
    name="pulumi-firewall-rules",
    network=gke_network.name,
    allows=[
        gcp.compute.FirewallAllowArgs(
            protocol="tcp",
            ports=[
                "22",
                "3389"
            ]
        ),
        gcp.compute.FirewallAllowArgs(
            protocol="tcp",
            ports=[
                "443",
            ],
        ),
    ],
    source_ranges=[
        "0.0.0.0/0"
    ]
)


# Build a Kubeconfig to access the cluster
cluster_kubeconfig = pulumi.Output.all(
    gke_cluster.master_auth.cluster_ca_certificate,
    gke_cluster.endpoint,
    gke_cluster.name).apply(lambda l:
    f"""apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {l[0]}
    server: https://{l[1]}
  name: {l[2]}
contexts:
- context:
    cluster: {l[2]}
    user: {l[2]}
  name: {l[2]}
current-context: {l[2]}
kind: Config
preferences: {{}}
users:
- name: {l[2]}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      installHint: Install gke-gcloud-auth-plugin for use with kubectl by following
        https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke
      provideClusterInfo: true
""")

# Export some values for use elsewhere
pulumi.export("networkName", gke_network.name)
pulumi.export("networkId", gke_network.id)
pulumi.export("clusterName", gke_cluster.name)
pulumi.export("clusterId", gke_cluster.id)
pulumi.export("kubeconfig", cluster_kubeconfig)
pulumi.export('firewall_rule_name', gke_firewall_rule.name)
