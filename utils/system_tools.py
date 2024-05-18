import psutil
import subprocess

def get_system_info():
    # 获取CPU使用率
    cpu_usage = psutil.cpu_percent(interval=1)

    # 获取内存使用率
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent

    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage
    }

def kill_vscode_server():
    result = subprocess.run(['pkill', '-f','vscode-server'], stdout=subprocess.PIPE)
    return result.returncode