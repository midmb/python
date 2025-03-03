Features:

Network Monitoring:

Bytes received/sent
Network throughput tracking


Cloud Storage Monitoring:

Bucket statistics
Object counts
Storage usage
Storage class information


Cloud SQL Monitoring:

Instance status
Database version
Configuration settings
Availability type


Cloud Run Monitoring:

Service status
Traffic distribution
Latest revisions
Service URLs


Custom Metrics:

Support for user-defined metrics
Flexible metric filtering
Label tracking


Alert Notifications:

Email notifications for critical events
Configurable thresholds
Error count alerts
Performance alerts


Performance Monitoring:

CPU thresholds
Memory usage tracking
Error rate monitoring



To use the enhanced version:

Install additional dependencies:

pip install google-cloud-storage
pip install google-cloud-sql
pip install google-cloud-run

export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"



python gcp_monitor.py

*******

--GCP Cloud App Monitor
from google.cloud import monitoring_v3
from google.cloud import error_reporting_v1beta1
from google.cloud import logging_v2
from google.cloud import compute_v1
from datetime import datetime, timedelta
import time
import os

class GCPMonitor:
    def __init__(self, project_id):
        """
        Initialize GCP Monitor with project ID
        """
        self.project_id = project_id
        self.project_name = f"projects/{project_id}"
        
        # Initialize clients
        self.client = monitoring_v3.MetricServiceClient()
        self.error_client = error_reporting_v1beta1.ErrorStatsServiceClient()
        self.logging_client = logging_v2.LoggingServiceV2Client()
        self.compute_client = compute_v1.InstancesClient()

    def get_cpu_usage(self, instance_name):
        """
        Get CPU usage metrics for a specific instance
        """
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        interval = monitoring_v3.TimeInterval({
            'end_time': {'seconds': seconds, 'nanos': nanos},
            'start_time': {'seconds': seconds - 3600, 'nanos': nanos}
        })

        metric_type = 'compute.googleapis.com/instance/cpu/utilization'
        
        results = self.client.list_time_series(
            request={
                "name": self.project_name,
                "filter": f'metric.type = "{metric_type}" AND resource.labels.instance_id = "{instance_name}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
            }
        )
        
        for result in results:
            return result.points[0].value.double_value * 100 if result.points else 0
        return 0

    def get_memory_usage(self, instance_name):
        """
        Get memory usage metrics for a specific instance
        """
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        interval = monitoring_v3.TimeInterval({
            'end_time': {'seconds': seconds, 'nanos': nanos},
            'start_time': {'seconds': seconds - 3600, 'nanos': nanos}
        })

        metric_type = 'compute.googleapis.com/instance/memory/usage'
        
        results = self.client.list_time_series(
            request={
                "name": self.project_name,
                "filter": f'metric.type = "{metric_type}" AND resource.labels.instance_id = "{instance_name}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
            }
        )
        
        for result in results:
            return result.points[0].value.int64_value if result.points else 0
        return 0

    def get_recent_errors(self):
        """
        Get recent error reports
        """
        time_range = error_reporting_v1beta1.QueryTimeRange()
        time_range.period = error_reporting_v1beta1.QueryTimeRange.Period.PERIOD_1_HOUR

        request = error_reporting_v1beta1.ListGroupStatsRequest(
            project_name=self.project_name,
            time_range=time_range,
            page_size=10
        )

        return self.error_client.list_group_stats(request)

    def get_recent_logs(self, severity="ERROR"):
        """
        Get recent logs with specified severity
        """
        filter_str = f'severity={severity}'
        
        request = logging_v2.ListLogEntriesRequest(
            resource_names=[self.project_name],
            filter=filter_str,
            order_by="timestamp desc",
            page_size=10
        )
        
        return self.logging_client.list_log_entries(request)

    def list_instances(self):
        """
        List all compute instances in the project
        """
        request = compute_v1.ListInstancesRequest(
            project=self.project_id,
            zone="-"  # List instances from all zones
        )
        
        return self.compute_client.list(request)

    def monitor(self, interval=300):
        """
        Main monitoring loop
        """
        print(f"Starting GCP Monitor for project: {self.project_id}")
        
        try:
            while True:
                print(f"\n{'='*50}")
                print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*50}")

                # List and monitor instances
                print("\nCompute Instances:")
                instances = self.list_instances()
                for instance in instances:
                    print(f"\nInstance: {instance.name}")
                    print(f"Status: {instance.status}")
                    print(f"Zone: {instance.zone.split('/')[-1]}")
                    
                    # Get CPU and Memory metrics
                    cpu_usage = self.get_cpu_usage(instance.name)
                    memory_usage = self.get_memory_usage(instance.name)
                    print(f"CPU Usage: {cpu_usage:.2f}%")
                    print(f"Memory Usage: {memory_usage} bytes")

                # Get recent errors
                print("\nRecent Errors:")
                error_stats = self.get_recent_errors()
                for error in error_stats:
                    print(f"Error: {error.representative.message}")
                    print(f"Count: {error.count}")
                    print(f"First Seen: {error.first_seen_time}")
                    print("---")

                # Get recent error logs
                print("\nRecent Error Logs:")
                logs = self.get_recent_logs()
                for log in logs:
                    print(f"Timestamp: {log.timestamp}")
                    print(f"Message: {log.text_payload}")
                    print("---")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    # Set your GCP project ID
    project_id = "your-project-id"
    
    # Make sure you have authenticated:
    # Either set GOOGLE_APPLICATION_CREDENTIALS environment variable
    # or run: gcloud auth application-default login
    
    monitor = GCPMonitor(project_id)
    monitor.monitor(interval=300)  # Check every 5 minutes
