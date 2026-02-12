import psutil
from typing import Dict, Any

from utils.logger import logger

class ResourceMonitor:
    """
    Provides methods to monitor system resources like CPU and memory.
    """

    def get_cpu_usage(self) -> float:
        """
        Returns the system-wide CPU utilization as a percentage.
        
        Note: The first call returns 0.0 or a meaningless value; subsequent
        calls with a non-zero interval will provide a meaningful result.
        """
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Returns system memory usage statistics.
        """
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent_used": mem.percent,
        }

    def get_disk_usage(self) -> Dict[str, Any]:
        """
        Returns disk usage statistics for the root partition.
        """
        disk = psutil.disk_usage('/')
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent_used": disk.percent,
        }
    
    def get_process_info(self) -> Dict[str, Any]:
        """
        Returns resource usage for the current process.
        """
        process = psutil.Process()
        with process.oneshot():
            return {
                "pid": process.pid,
                "name": process.name(),
                "cpu_percent": process.cpu_percent(),
                "memory_mb": round(process.memory_info().rss / (1024**2), 2)
            }


    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Returns a consolidated dictionary of all key resource metrics.
        """
        logger.info("Gathering resource metrics.")
        try:
            return {
                "system_cpu_percent": self.get_cpu_usage(),
                "system_memory": self.get_memory_usage(),
                "system_disk": self.get_disk_usage(),
                "application_process": self.get_process_info(),
            }
        except Exception as e:
            logger.error(f"Failed to gather resource metrics: {e}")
            return {"error": str(e)}

# Singleton instance
resource_monitor = ResourceMonitor()

def get_resource_metrics() -> Dict[str, Any]:
    """
    High-level function to get all resource metrics.
    """
    return resource_monitor.get_all_metrics()
