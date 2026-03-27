"""System monitoring plugin for David AI Assistant."""

from plugins.base import BasePlugin
from typing import Dict, List
import psutil
from core.logger import get_logger

logger = get_logger(__name__)

class SystemMonitorPlugin(BasePlugin):
    """Monitor system resources and processes."""
    
    def get_intents(self) -> List[str]:
        return ["cpu_usage", "ram_usage", "disk_usage", "battery_status", 
                "list_processes", "kill_process", "network_status"]
    
    def get_description(self) -> str:
        return "Monitor system: CPU, RAM, disk, battery, processes, network"
    
    def get_prompt_examples(self) -> str:
        return """cpu_usage:
{
  "intent": "cpu_usage"
}

ram_usage:
{
  "intent": "ram_usage"
}

disk_usage:
{
  "intent": "disk_usage"
}

battery_status:
{
  "intent": "battery_status"
}

list_processes:
{
  "intent": "list_processes",
  "limit": 5 (optional, default 5)
}

kill_process:
{
  "intent": "kill_process",
  "process_name": "chrome.exe"
}

network_status:
{
  "intent": "network_status"
}"""
    
    def execute(self, intent: Dict) -> str:
        """Execute system monitoring command."""
        intent_type = intent.get("intent")
        
        try:
            if intent_type == "cpu_usage":
                cpu_percent = psutil.cpu_percent(interval=1)
                return f"CPU usage is {cpu_percent}%"
            
            elif intent_type == "ram_usage":
                ram = psutil.virtual_memory()
                used_gb = ram.used / (1024**3)
                total_gb = ram.total / (1024**3)
                return f"RAM usage: {used_gb:.1f} GB of {total_gb:.1f} GB ({ram.percent}%)"
            
            elif intent_type == "disk_usage":
                disk = psutil.disk_usage('/')
                used_gb = disk.used / (1024**3)
                total_gb = disk.total / (1024**3)
                return f"Disk usage: {used_gb:.1f} GB of {total_gb:.1f} GB ({disk.percent}%)"
            
            elif intent_type == "battery_status":
                battery = psutil.sensors_battery()
                if battery is None:
                    return "No battery detected. This might be a desktop computer."
                
                status = "charging" if battery.power_plugged else "discharging"
                return f"Battery: {battery.percent}% ({status})"
            
            elif intent_type == "list_processes":
                limit = intent.get("limit", 5)
                processes = []
                
                for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Sort by CPU usage
                processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
                
                result = f"Top {limit} processes by CPU: "
                for i, proc in enumerate(processes[:limit], 1):
                    result += f"{i}. {proc['name']} ({proc.get('cpu_percent', 0):.1f}% CPU). "
                
                return result
            
            elif intent_type == "kill_process":
                process_name = intent.get("process_name", "").lower()
                if not process_name:
                    return "Please specify a process name."
                
                killed = False
                for proc in psutil.process_iter(['name']):
                    try:
                        if process_name in proc.info['name'].lower():
                            proc.kill()
                            killed = True
                            logger.warning(f"Killed process: {proc.info['name']}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        logger.error(f"Could not kill process: {e}")
                
                if killed:
                    return f"Killed process: {process_name}"
                else:
                    return f"Process not found: {process_name}"
            
            elif intent_type == "network_status":
                net_io = psutil.net_io_counters()
                sent_mb = net_io.bytes_sent / (1024**2)
                recv_mb = net_io.bytes_recv / (1024**2)
                return f"Network: Sent {sent_mb:.1f} MB, Received {recv_mb:.1f} MB"
            
            else:
                return "Unknown system monitoring command."
                
        except Exception as e:
            logger.error(f"System monitor plugin error: {e}")
            return "Sorry, I couldn't get the system information."
