import psutil
import time
from datetime import datetime
import platform
import os

class SystemMonitor:
    def __init__(self, interval=1):
        self.interval = interval
    
    def get_size(self, bytes):
        """
        Convert bytes to human readable format
        """
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
                return f"{bytes:.2f}{unit}B"
            bytes /= 1024

    def get_cpu_info(self):
        """
        Get CPU information including usage and frequency
        """
        cpu_freq = psutil.cpu_freq()
        cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
        return {
            'usage_per_cpu': cpu_usage,
            'avg_usage': sum(cpu_usage) / len(cpu_usage),
            'current_freq': cpu_freq.current if cpu_freq else "N/A",
            'cores': psutil.cpu_count(logical=False),
            'threads': psutil.cpu_count(logical=True)
        }

    def get_memory_info(self):
        """
        Get memory usage information
        """
        memory = psutil.virtual_memory()
        return {
            'total': self.get_size(memory.total),
            'available': self.get_size(memory.available),
            'used': self.get_size(memory.used),
            'percentage': memory.percent
        }

    def get_disk_info(self):
        """
        Get disk usage information
        """
        partitions = psutil.disk_partitions()
        disk_info = []
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'total': self.get_size(usage.total),
                    'used': self.get_size(usage.used),
                    'free': self.get_size(usage.free),
                    'percentage': usage.percent
                })
            except:
                continue
        return disk_info

    def get_network_info(self):
        """
        Get network information
        """
        network = psutil.net_io_counters()
        return {
            'bytes_sent': self.get_size(network.bytes_sent),
            'bytes_received': self.get_size(network.bytes_recv),
            'packets_sent': network.packets_sent,
            'packets_received': network.packets_recv
        }

    def monitor(self):
        """
        Main monitoring function
        """
        print(f"System Monitor Started - {platform.system()} {platform.release()}\n")
        
        try:
            while True:
                print(f"\n{'='*50}")
                print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*50}")

                # CPU Information
                cpu_info = self.get_cpu_info()
                print("\nCPU Information:")
                print(f"Cores: {cpu_info['cores']} (Physical), {cpu_info['threads']} (Logical)")
                print(f"Current Frequency: {cpu_info['current_freq']:.2f} MHz")
                print(f"Average CPU Usage: {cpu_info['avg_usage']:.1f}%")

                # Memory Information
                mem_info = self.get_memory_info()
                print("\nMemory Information:")
                print(f"Total: {mem_info['total']}")
                print(f"Available: {mem_info['available']}")
                print(f"Used: {mem_info['used']} ({mem_info['percentage']}%)")

                # Disk Information
                print("\nDisk Information:")
                for disk in self.get_disk_info():
                    print(f"\nDevice: {disk['device']}")
                    print(f"Mount Point: {disk['mountpoint']}")
                    print(f"Total: {disk['total']}")
                    print(f"Used: {disk['used']} ({disk['percentage']}%)")
                    print(f"Free: {disk['free']}")

                # Network Information
                net_info = self.get_network_info()
                print("\nNetwork Information:")
                print(f"Bytes Sent: {net_info['bytes_sent']}")
                print(f"Bytes Received: {net_info['bytes_received']}")
                print(f"Packets Sent: {net_info['packets_sent']}")
                print(f"Packets Received: {net_info['packets_received']}")

                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    monitor = SystemMonitor(interval=2)  # Update every 2 seconds
    monitor.monitor()
