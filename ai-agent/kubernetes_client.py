import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger("ai-agent")

class K8sClient:
    def __init__(self):
        self.mock_mode = False
        try:
            # Load in-cluster config if running inside K8s, otherwise local kubeconfig
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes configuration.")
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
        except config.ConfigException:
            try:
                config.load_kube_config()
                logger.info("Loaded local kubeconfig file.")
                self.v1 = client.CoreV1Api()
                self.apps_v1 = client.AppsV1Api()
            except Exception as e:
                logger.warning(f"Failed to load Kubernetes configuration: {e}. AI Agent is falling back to MOCK mode for offline testing.")
                self.mock_mode = True
                self.v1 = None
                self.apps_v1 = None

    def get_pod_logs(self, name: str, namespace: str, container: str = None, tail_lines: int = 50) -> str:
        """
        Fetches the last N lines of logs for a specific pod. Falls back to mock data if in mock_mode.
        """
        if self.mock_mode:
            logger.info(f"[MOCK MODE] Generating simulated SRE logs for pod {name}...")
            # Generate highly realistic failure logs based on name or alert context
            if "memory" in name.lower() or "oom" in name.lower():
                return (
                    "2026-05-30 18:14:01 [INFO] Starting sre-ai-agent webserver on port 8000...\n"
                    "2026-05-30 18:14:15 [DEBUG] Allocation of 40MB heap buffer in billing_controller.py:L142\n"
                    "2026-05-30 18:14:30 [WARN] Memory consumption rising: heap_used=118MB (Limit=128MB)\n"
                    "2026-05-30 18:14:35 [CRITICAL] FATAL ERROR: Out of memory (heap allocation failed during billing export request)\n"
                    "2026-05-30 18:14:36 [CRITICAL] Process terminated: OutOfMemoryError"
                )
            else:
                # Default CrashLoopBackOff crash log
                return (
                    "2026-05-30 18:12:10 [INFO] Bootstrapping sre-ai-agent application...\n"
                    "2026-05-30 18:12:11 [INFO] Connecting to postgres-service.production.svc.cluster.local:5432...\n"
                    "2026-05-30 18:12:12 [ERROR] Database Connection Failed: password authentication failed for user 'devops-admin1'\n"
                    "Traceback (most recent call last):\n"
                    "  File \"app/database.py\", line 12, in connect_db\n"
                    "    conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)\n"
                    "psycopg2.OperationalError: FATAL: password authentication failed for user \"devops-admin1\"\n"
                    "2026-05-30 18:12:13 [CRITICAL] Core initialization error. Terminating process with exit code 1."
                )

        try:
            kwargs = {"tail_lines": tail_lines}
            if container:
                kwargs["container"] = container
                
            logs = self.v1.read_namespaced_pod_log(name=name, namespace=namespace, **kwargs)
            return logs
        except ApiException as e:
            logger.error(f"API Exception reading logs for {name}: {e}")
            return f"Error fetching logs: {e.reason}"
        except Exception as e:
            logger.error(f"Error fetching logs for {name}: {e}")
            return f"Error: {str(e)}"

    def get_pod_events(self, name: str, namespace: str) -> str:
        """
        Fetches recent events. Falls back to mock data if in mock_mode.
        """
        if self.mock_mode:
            logger.info(f"[MOCK MODE] Generating simulated namespace events for pod {name}...")
            return (
                "[2026-05-30T18:10:00Z] Normal Scheduled: Successfully assigned production/sre-ai-agent to node-1\n"
                "[2026-05-30T18:10:05Z] Normal Pulled: Container image already present on machine\n"
                "[2026-05-30T18:10:06Z] Normal Created: Created container sre-ai-agent\n"
                "[2026-05-30T18:10:07Z] Normal Started: Started container sre-ai-agent\n"
                "[2026-05-30T18:11:15Z] Warning Unhealthy: Liveness probe failed: HTTP probe failed with statuscode: 500\n"
                "[2026-05-30T18:11:20Z] Normal Killing: Container sre-ai-agent failed liveness probe, will be restarted\n"
                "[2026-05-30T18:11:35Z] Warning BackOff: Back-off restarting failed container sre-ai-agent"
            )

        try:
            events = self.v1.list_namespaced_event(namespace=namespace)
            related_events = []
            for event in events.items:
                if event.involved_object.name == name:
                    related_events.append(
                        f"[{event.last_timestamp}] {event.type} {event.reason}: {event.message}"
                    )
            return "\n".join(related_events) if related_events else "No related events found."
        except ApiException as e:
            logger.error(f"API Exception listing events: {e}")
            return f"Error fetching events: {e.reason}"

    def get_pod_details(self, name: str, namespace: str) -> str:
        """
        Gathers Pod spec status. Falls back to mock data if in mock_mode.
        """
        if self.mock_mode:
            logger.info(f"[MOCK MODE] Generating simulated pod details for {name}...")
            return (
                f"Pod Name: {name}\n"
                f"Namespace: {namespace}\n"
                f"Status: CrashLoopBackOff\n"
                f"Restart Count: 5\n"
                f"Limits - CPU: 100m, Memory: 128Mi\n"
                f"Requests - CPU: 50m, Memory: 64Mi\n"
            )

        try:
            pod = self.v1.read_namespaced_pod(name=name, namespace=namespace)
            details = (
                f"Pod Name: {pod.metadata.name}\n"
                f"Namespace: {pod.metadata.namespace}\n"
                f"Status: {pod.status.phase}\n"
                f"Restart Count: {pod.status.container_statuses[0].restart_count if pod.status.container_statuses else 0}\n"
                f"Limits - CPU: {pod.spec.containers[0].resources.limits.get('cpu') if pod.spec.containers[0].resources.limits else 'None'}, "
                f"Memory: {pod.spec.containers[0].resources.limits.get('memory') if pod.spec.containers[0].resources.limits else 'None'}\n"
            )
            return details
        except ApiException as e:
            logger.error(f"API Exception getting pod details: {e}")
            return f"Error fetching pod details: {e.reason}"

