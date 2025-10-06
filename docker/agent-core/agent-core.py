#!/usr/bin/env python3
import json
import sys
import os
from openai import AzureOpenAI
import requests
from typing import Dict, List, Any
from http.server import HTTPServer, BaseHTTPRequestHandler

class AgentCore:
    def __init__(self):
        self.azure_openai = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.mcp_endpoints = {
            'azure': 'http://azure-mcp-service:80',
            'database': 'http://database-mcp-service:80',
            'custom': 'http://custom-mcp-service:80',
            'k8s': 'http://k8s-mcp-service.k8s-admin:80'
        }
    
    def call_mcp_tool(self, server: str, tool: str, args: Dict) -> Dict:
        """Call MCP server tool"""
        url = self.mcp_endpoints.get(server)
        if not url:
            return {"error": f"Unknown MCP server: {server}"}
        
        payload = {
            "method": "tools/call",
            "params": {"name": tool, "arguments": args}
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def invoke_azure_openai(self, prompt: str) -> str:
        """Invoke Azure OpenAI for reasoning"""
        try:
            response = self.azure_openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that provides concise, helpful analysis and recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Azure OpenAI error: {str(e)}"
    
    def execute_workflow(self, workflow: Dict) -> Dict:
        """Execute agentic workflow"""
        task = workflow.get('task', '')
        
        if 'openai' in task.lower() or 'ai' in task.lower():
            prompt = workflow.get('prompt', 'Hello from Agent Core!')
            result = self.invoke_azure_openai(prompt)
            return {'workflow': 'azure_openai_test', 'result': result}
        
        if 'blob' in task.lower() or 'storage' in task.lower():
            result = self.call_mcp_tool('azure', 'list_blob_containers', {})
            return {'workflow': 'blob_storage_list', 'result': result}
        
        if 'weather' in task.lower():
            city = workflow.get('city', 'San Francisco')
            # Multi-step workflow: Get weather -> Analyze -> Store
            weather = self.call_mcp_tool('custom', 'get_weather', {'city': city})
            analysis = self.invoke_azure_openai(f"Analyze this weather data and provide insights: {weather}")
            storage = self.call_mcp_tool('custom', 'store_data', {
                'key': f'weather_{city}',
                'value': analysis
            })
            return {
                'workflow': 'weather_analysis',
                'steps': [
                    {'step': 'get_weather', 'result': weather},
                    {'step': 'ai_analysis', 'result': analysis},
                    {'step': 'store_result', 'result': storage}
                ]
            }
        
        if 'database' in task.lower():
            query = workflow.get('query', 'SELECT * FROM users')
            result = self.call_mcp_tool('database', 'execute_query', {'query': query})
            analysis = self.invoke_azure_openai(f"Analyze this database query result: {result}")
            return {
                'workflow': 'database_analysis',
                'steps': [
                    {'step': 'execute_query', 'result': result},
                    {'step': 'ai_analysis', 'result': analysis}
                ]
            }
        
        if 'kubernetes' in task.lower() or 'k8s' in task.lower():
            if 'scale' in task.lower():
                deployment = workflow.get('deployment_name', 'agent-core')
                replicas = workflow.get('replicas', 3)
                result = self.call_mcp_tool('k8s', 'scale_deployment', {
                    'deployment_name': deployment,
                    'replicas': replicas
                })
                return {'workflow': 'k8s_scale', 'result': result}
            elif 'status' in task.lower() or 'health' in task.lower():
                result = self.call_mcp_tool('k8s', 'get_cluster_status', {})
                analysis = self.invoke_azure_openai(f"Analyze this Kubernetes cluster status and provide recommendations: {result}")
                return {
                    'workflow': 'k8s_health_check',
                    'steps': [
                        {'step': 'get_status', 'result': result},
                        {'step': 'ai_analysis', 'result': analysis}
                    ]
                }
            elif 'pods' in task.lower():
                namespace = workflow.get('namespace', 'default')
                result = self.call_mcp_tool('k8s', 'list_pods', {'namespace': namespace})
                return {'workflow': 'k8s_list_pods', 'result': result}
            elif 'troubleshoot' in task.lower():
                pod_name = workflow.get('pod_name')
                if pod_name:
                    result = self.call_mcp_tool('k8s', 'troubleshoot_pod', {'pod_name': pod_name})
                    analysis = self.invoke_azure_openai(f"Provide troubleshooting recommendations for this pod: {result}")
                    return {
                        'workflow': 'k8s_troubleshoot',
                        'steps': [
                            {'step': 'analyze_pod', 'result': result},
                            {'step': 'ai_recommendations', 'result': analysis}
                        ]
                    }
                return {'error': 'pod_name required for troubleshooting'}
            else:
                result = self.call_mcp_tool('k8s', 'get_cluster_status', {})
                return {'workflow': 'k8s_general', 'result': result}
        
        if 'data factory' in task.lower() or 'pipeline' in task.lower():
            if 'start' in task.lower() or 'run' in task.lower():
                pipeline_name = workflow.get('pipeline_name', 'sample-pipeline')
                # Multi-step: Start pipeline -> Monitor -> Report
                start_result = self.call_mcp_tool('azure', 'start_data_factory_pipeline', {'pipeline_name': pipeline_name})
                
                # Get initial status
                status_result = self.call_mcp_tool('azure', 'get_pipeline_status', {
                    'pipeline_name': pipeline_name
                })
                
                # AI analysis of pipeline execution
                analysis = self.invoke_azure_openai(f"Analyze this Data Factory pipeline execution: {status_result}")
                
                return {
                    'workflow': 'data_factory_execution',
                    'steps': [
                        {'step': 'start_pipeline', 'result': start_result},
                        {'step': 'check_status', 'result': status_result},
                        {'step': 'ai_analysis', 'result': analysis}
                    ]
                }
            else:
                # List pipelines workflow
                pipelines_result = self.call_mcp_tool('azure', 'list_data_factory_pipelines', {})
                analysis = self.invoke_azure_openai(f"Analyze these Data Factory pipelines and suggest optimizations: {pipelines_result}")
                
                return {
                    'workflow': 'data_factory_analysis',
                    'steps': [
                        {'step': 'list_pipelines', 'result': pipelines_result},
                        {'step': 'ai_analysis', 'result': analysis}
                    ]
                }
        
        return {"error": "Unknown workflow"}

class AgentHandler(BaseHTTPRequestHandler):
    def __init__(self, agent_core, *args, **kwargs):
        self.agent_core = agent_core
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request = json.loads(post_data.decode('utf-8'))
            method = request.get('method')
            
            if method == 'workflow/execute':
                result = self.agent_core.execute_workflow(request.get('params', {}))
            else:
                result = {"error": "Unknown method"}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/metrics':
            # Simple Prometheus metrics
            metrics = '''# HELP agent_core_requests_total Total requests processed
# TYPE agent_core_requests_total counter
agent_core_requests_total 42
# HELP agent_core_active_workflows Active workflows
# TYPE agent_core_active_workflows gauge
agent_core_active_workflows 3
'''
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(metrics.encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    agent = AgentCore()
    
    def handler(*args, **kwargs):
        AgentHandler(agent, *args, **kwargs)
    
    httpd = HTTPServer(('0.0.0.0', 8000), handler)
    print("Agent Core running on port 8000")
    httpd.serve_forever()