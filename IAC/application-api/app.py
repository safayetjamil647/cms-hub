from flask import Flask, jsonify ,request
from kubernetes import client, config

app = Flask(__name__)
# Define the path to your kubeconfig file
kubeconfig_path = './kubeconfig'

# Load the Kubernetes configuration (assuming you have kubectl configured)
config.load_kube_config(config_file=kubeconfig_path)

# Kubernetes client setup
v1 = client.CoreV1Api()

@app.route('/pods', methods=['GET'])
def get_pods():
    # Retrieve information about pods in the default namespace
    pods = v1.list_namespaced_pod(namespace="default")
    
    # Process the response and convert to a more user-friendly format
    pod_list = []
    for pod in pods.items:
        pod_list.append({
            "name": pod.metadata.name,
            "status": pod.status.phase,
        })

    return jsonify(pod_list)


@app.route('/nodes', methods=['GET'])
def get_nodes():
    # Retrieve information about nodes in the cluster
    nodes = v1.list_node()

    # Process the response and convert to a more user-friendly format
    node_list = []
    for node in nodes.items:
        node_list.append({
            "name": node.metadata.name,
            "status": node.status.conditions[-1].type if node.status.conditions else "Unknown",
        })

    return jsonify(node_list)


def create_namespace(namespace_name):
    try:
        metadata = client.V1ObjectMeta(name=namespace_name)
        namespace = client.V1Namespace(metadata=metadata)
        v1.create_namespace(namespace)
        return True, None
    except Exception as e:
        return False, str(e)

@app.route('/create-namespace', methods=['POST'])
def handle_create_namespace():
    data = request.get_json()
    if not data or 'namespace' not in data:
        return jsonify({"error": "Invalid request data"}), 400
    
    namespace_name = data['namespace']
    success, message = create_namespace(namespace_name)
    if success:
        return jsonify({"message": f"Namespace '{namespace_name}' created successfully"}), 201
    else:
        return jsonify({"error": f"Failed to create namespace: {message}"}), 500
    
def delete_namespace(namespace_name):
    try:
        v1.delete_namespace(namespace_name)
        return True, None
    except Exception as e:
        return False, str(e)
@app.route('/delete-namespace', methods=['POST'])
def handle_delete_namespace():
    data = request.get_json()
    if not data or 'namespace' not in data:
        return jsonify({"error": "Invalid request data"}), 400
    
    namespace_name = data['namespace']
    success, message = delete_namespace(namespace_name)
    if success:
        return jsonify({"message": f"Namespace '{namespace_name}' deleted successfully"}), 200
    else:
        return jsonify({"error": f"Failed to delete namespace: {message}"}), 500

def deploy_nginx_with_loadbalancer():
    try:
        # Create a Deployment for NGINX
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "nginx-deployment"},
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {"app": "nginx"}
                },
                "template": {
                    "metadata": {"labels": {"app": "nginx"}},
                    "spec": {
                        "containers": [{
                            "name": "nginx",
                            "image": "nginx:latest",
                            "ports": [{"containerPort": 80}]
                        }]
                    }
                }
            }
        }
        v1.create_namespaced_deployment(namespace="default", body=deployment)
        
        # Create a LoadBalancer Service
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "nginx-service"},
            "spec": {
                "type": "LoadBalancer",
                "selector": {"app": "nginx"},
                "ports": [{"protocol": "TCP", "port": 80, "targetPort": 80}]
            }
        }
        v1.create_namespaced_service(namespace="default", body=service)
        
        return True, None
    except Exception as e:
        return False, str(e)

@app.route('/deploy-nginx', methods=['POST'])
def handle_deploy_nginx():
    success, message = deploy_nginx_with_loadbalancer()
    if success:
        return jsonify({"message": "NGINX deployed with LoadBalancer"}), 201
    else:
        return jsonify({"error": f"Failed to deploy NGINX: {message}"}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

