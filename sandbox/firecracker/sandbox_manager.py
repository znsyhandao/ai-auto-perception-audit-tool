"""
企业级沙箱管理
使用Firecracker微虚机和gVisor提供最高级别的隔离
"""

import asyncio
import aiohttp
import docker
from typing import Dict, List, Any, Optional
import tempfile
import os
import json
from dataclasses import dataclass
import time
import logging
import grpc
from concurrent import futures
import firecracker
import gvisor


@dataclass
class SandboxConfig:
    """沙箱配置"""
    cpu_cores: int = 1
    memory_mb: int = 256
    disk_mb: int = 1024
    network_enabled: bool = False
    timeout_seconds: int = 30
    isolation_level: str = 'microvm'  # microvm, gvisor, docker, process


class EnterpriseSandbox:
    """企业级沙箱管理器"""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.sandbox_pool = []
        self.metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0,
            'total_memory_used': 0
        }
        
        # 初始化隔离层
        self._init_isolation()
    
    def _init_isolation(self):
        """初始化隔离层"""
        if self.config.isolation_level == 'microvm':
            self._init_firecracker()
        elif self.config.isolation_level == 'gvisor':
            self._init_gvisor()
        elif self.config.isolation_level == 'docker':
            self._init_docker()
    
    def _init_firecracker(self):
        """初始化Firecracker微虚机"""
        self.fc_manager = firecracker.Manager(
            socket_path='/tmp/firecracker.sock',
            kernel_image='/path/to/vmlinux',
            rootfs='/path/to/rootfs.ext4'
        )
    
    def _init_gvisor(self):
        """初始化gVisor"""
        self.gvisor_runtime = gvisor.Runtime(
            runsc_path='/usr/bin/runsc',
            platform='ptrace'  # 或 kvm
        )
    
    def _init_docker(self):
        """初始化Docker"""
        self.docker_client = docker.from_env()
    
    async def execute_in_sandbox(self, code: str, plugin_path: str) -> Dict[str, Any]:
        """
        在沙箱中执行插件
        """
        execution_id = self._generate_execution_id()
        
        start_time = time.time()
        result = {
            'execution_id': execution_id,
            'success': False,
            'output': None,
            'error': None,
            'metrics': {},
            'syscalls': [],
            'network_connections': [],
            'file_operations': []
        }
        
        try:
            # 根据隔离级别选择执行方式
            if self.config.isolation_level == 'microvm':
                result = await self._execute_in_microvm(code, plugin_path)
            elif self.config.isolation_level == 'gvisor':
                result = await self._execute_in_gvisor(code, plugin_path)
            elif self.config.isolation_level == 'docker':
                result = await self._execute_in_docker(code, plugin_path)
            else:
                result = await self._execute_in_process(code, plugin_path)
            
            # 更新指标
            self._update_metrics(result, time.time() - start_time)
            
        except Exception as e:
            result['error'] = str(e)
            self.metrics['failed_executions'] += 1
        
        return result
    
    async def _execute_in_microvm(self, code: str, plugin_path: str) -> Dict[str, Any]:
        """在Firecracker微虚机中执行"""
        result = {'success': False}
        
        try:
            # 创建微虚机
            vm_id = self.fc_manager.create_vm(
                cpu_cores=self.config.cpu_cores,
                memory_mb=self.config.memory_mb,
                disk_mb=self.config.disk_mb
            )
            
            # 复制插件文件
            vm_id.copy_to(plugin_path, '/plugin.py')
            
            # 执行插件
            exec_result = await asyncio.wait_for(
                vm_id.execute(f'python3 /plugin.py'),
                timeout=self.config.timeout_seconds
            )
            
            result['success'] = exec_result.returncode == 0
            result['output'] = exec_result.stdout
            result['error'] = exec_result.stderr
            
            # 收集系统调用
            result['syscalls'] = await vm_id.get_syscalls()
            
            # 收集网络连接
            if self.config.network_enabled:
                result['network_connections'] = await vm_id.get_network_connections()
            
            # 清理
            self.fc_manager.destroy_vm(vm_id)
            
        except asyncio.TimeoutError:
            result['error'] = f'执行超时 ({self.config.timeout_seconds}秒)'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    async def _execute_in_gvisor(self, code: str, plugin_path: str) -> Dict[str, Any]:
        """在gVisor沙箱中执行"""
        result = {'success': False}
        
        try:
            # 创建gVisor容器
            container = self.gvisor_runtime.create_container(
                image='python:3.10-slim',
                command=f'python3 /plugin.py',
                mounts={plugin_path: '/plugin.py'},
                resources={
                    'cpu': self.config.cpu_cores,
                    'memory': f'{self.config.memory_mb}M'
                },
                seccomp_profile='strict'
            )
            
            # 执行
            exec_result = await asyncio.wait_for(
                container.run(),
                timeout=self.config.timeout_seconds
            )
            
            result['success'] = exec_result.exit_code == 0
            result['output'] = exec_result.stdout
            result['error'] = exec_result.stderr
            
            # 获取系统调用统计
            result['syscalls'] = container.get_syscall_stats()
            
            # 清理
            container.destroy()
            
        except asyncio.TimeoutError:
            result['error'] = f'执行超时 ({self.config.timeout_seconds}秒)'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    async def _execute_in_docker(self, code: str, plugin_path: str) -> Dict[str, Any]:
        """在Docker容器中执行"""
        result = {'success': False}
        
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as tmpdir:
                # 复制插件文件
                import shutil
                shutil.copy(plugin_path, f'{tmpdir}/plugin.py')
                
                # 运行容器
                container = self.docker_client.containers.run(
                    'python:3.10-slim',
                    command='python3 /plugin.py',
                    volumes={tmpdir: {'bind': '/app', 'mode': 'ro'}},
                    working_dir='/app',
                    mem_limit=f'{self.config.memory_mb}m',
                    nano_cpus=self.config.cpu_cores * 1_000_000_000,
                    detach=True,
                    remove=False
                )
                
                # 等待完成
                result_data = await asyncio.wait_for(
                    self._wait_container(container),
                    timeout=self.config.timeout_seconds
                )
                
                result['success'] = result_data['exit_code'] == 0
                result['output'] = result_data['stdout']
                result['error'] = result_data['stderr']
                
                # 获取容器日志
                result['logs'] = container.logs().decode()
                
                # 清理
                container.remove(force=True)
                
        except asyncio.TimeoutError:
            result['error'] = f'执行超时 ({self.config.timeout_seconds}秒)'
            container.kill()
            container.remove(force=True)
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    async def _wait_container(self, container):
        """等待容器完成"""
        result = {'exit_code': None, 'stdout': '', 'stderr': ''}
        
        # 等待容器退出
        for _ in range(self.config.timeout_seconds):
            container.reload()
            if container.status != 'running':
                result['exit_code'] = container.attrs['State']['ExitCode']
                result['stdout'] = container.logs(stdout=True).decode()
                result['stderr'] = container.logs(stderr=True).decode()
                break
            await asyncio.sleep(1)
        
        return result
    
    async def _execute_in_process(self, code: str, plugin_path: str) -> Dict[str, Any]:
        """在进程级沙箱中执行（有限隔离）"""
        import subprocess
        import resource
        
        result = {'success': False}
        
        try:
            # 设置资源限制
            resource.setrlimit(resource.RLIMIT_CPU, (self.config.timeout_seconds, self.config.timeout_seconds))
            resource.setrlimit(resource.RLIMIT_AS, (self.config.memory_mb * 1024 * 1024, self.config.memory_mb * 1024 * 1024))
            
            # 执行
            process = subprocess.run(
                ['python3', plugin_path],
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds
            )
            
            result['success'] = process.returncode == 0
            result['output'] = process.stdout
            result['error'] = process.stderr
            
        except subprocess.TimeoutExpired:
            result['error'] = f'执行超时 ({self.config.timeout_seconds}秒)'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _update_metrics(self, result: Dict, execution_time: float):
        """更新指标"""
        self.metrics['total_executions'] += 1
        
        if result['success']:
            self.metrics['successful_executions'] += 1
        else:
            self.metrics['failed_executions'] += 1
        
        # 更新平均执行时间
        total = self.metrics['average_execution_time'] * (self.metrics['total_executions'] - 1)
        self.metrics['average_execution_time'] = (total + execution_time) / self.metrics['total_executions']
    
    def _generate_execution_id(self) -> str:
        """生成执行ID"""
        import uuid
        return f"exec_{uuid.uuid4().hex[:16]}"
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取沙箱指标"""
        return self.metrics