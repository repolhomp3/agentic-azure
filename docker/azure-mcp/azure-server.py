#!/usr/bin/env python3
import json
import sys
import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import *
from openai import AzureOpenAI
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class AzureMCP:
    def __init__(self):
        self.credential = None
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'agentic-rg')
        self.init_azure_clients()
    
    def init_azure_clients(self):
        try:
            self.credential = DefaultAzureCredential()
            # Test credential
            self.credential.get_token("https://management.azure.com/.default")
        except Exception as e:
            print(f"Azure credential error: {e}")
            self.credential = None
    
    def handle_request(self, request):
        method = request.get('method')
        params = request.get('params', {})
        
        if method == 'tools/list':
            return {
                "tools": [
                    {
                        "name": "list_blob_containers",
                        "description": "List Azure Blob Storage containers",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "invoke_azure_openai",
                        "description": "Invoke Azure OpenAI model",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string", "description": "Text prompt"},
                                "max_tokens": {"type": "integer", "default": 100}
                            },
                            "required": ["prompt"]
                        }
                    },
                    {
                        "name": "list_data_factory_pipelines",
                        "description": "List Azure Data Factory pipelines",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "factory_name": {"type": "string", "description": "Data Factory name"}
                            },
                            "required": ["factory_name"]
                        }
                    },
                    {
                        "name": "start_data_factory_pipeline",
                        "description": "Start a Data Factory pipeline run",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "factory_name": {"type": "string", "description": "Data Factory name"},
                                "pipeline_name": {"type": "string", "description": "Pipeline name"}
                            },
                            "required": ["factory_name", "pipeline_name"]
                        }
                    },
                    {
                        "name": "get_pipeline_status",
                        "description": "Get Data Factory pipeline run status",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "factory_name": {"type": "string", "description": "Data Factory name"},
                                "run_id": {"type": "string", "description": "Pipeline run ID"}
                            },
                            "required": ["factory_name", "run_id"]
                        }
                    }
                ]
            }
        
        elif method == 'tools/call':
            if not self.credential:
                return {"error": "Azure credentials not configured"}
            
            tool_name = params.get('name')
            args = params.get('arguments', {})
            
            if tool_name == 'list_blob_containers':
                return self.list_blob_containers()
            elif tool_name == 'invoke_azure_openai':
                return self.invoke_azure_openai(args['prompt'], args.get('max_tokens', 100))
            elif tool_name == 'list_data_factory_pipelines':
                return self.list_data_factory_pipelines(args['factory_name'])
            elif tool_name == 'start_data_factory_pipeline':
                return self.start_data_factory_pipeline(args['factory_name'], args['pipeline_name'])
            elif tool_name == 'get_pipeline_status':
                return self.get_pipeline_status(args['factory_name'], args['run_id'])
        
        return {"error": "Unknown method"}
    
    def list_blob_containers(self):
        try:
            storage_account = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
            if not storage_account:
                return {"error": "AZURE_STORAGE_ACCOUNT_NAME not configured"}
            
            blob_service_client = BlobServiceClient(
                account_url=f"https://{storage_account}.blob.core.windows.net",
                credential=self.credential
            )
            
            containers = []
            for container in blob_service_client.list_containers():
                containers.append({
                    "name": container.name,
                    "last_modified": container.last_modified.isoformat() if container.last_modified else None
                })
            
            return {"content": [{"type": "text", "text": f"Blob Containers: {json.dumps(containers, indent=2)}"}]}
        except Exception as e:
            return {"error": f"Blob Storage error: {str(e)}"}
    
    def invoke_azure_openai(self, prompt, max_tokens):
        try:
            azure_openai = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-01",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            
            response = azure_openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(max_tokens, 200),
                temperature=0.7
            )
            
            output_text = response.choices[0].message.content
            return {"content": [{"type": "text", "text": output_text}]}
        except Exception as e:
            return {"error": f"Azure OpenAI error: {str(e)}"}
    
    def list_data_factory_pipelines(self, factory_name):
        try:
            if not self.subscription_id:
                return {"error": "AZURE_SUBSCRIPTION_ID not configured"}
            
            adf_client = DataFactoryManagementClient(
                self.credential, 
                self.subscription_id
            )
            
            pipelines = []
            for pipeline in adf_client.pipelines.list_by_factory(self.resource_group, factory_name):
                pipelines.append({
                    "name": pipeline.name,
                    "type": pipeline.type,
                    "etag": pipeline.etag
                })
            
            return {"content": [{"type": "text", "text": json.dumps(pipelines, indent=2)}]}
        except Exception as e:
            return {"error": f"Data Factory error: {str(e)}"}
    
    def start_data_factory_pipeline(self, factory_name, pipeline_name):
        try:
            if not self.subscription_id:
                return {"error": "AZURE_SUBSCRIPTION_ID not configured"}
            
            adf_client = DataFactoryManagementClient(
                self.credential, 
                self.subscription_id
            )
            
            run_response = adf_client.pipeline_runs.create_run(
                self.resource_group, 
                factory_name, 
                pipeline_name
            )
            
            result = {
                "factory_name": factory_name,
                "pipeline_name": pipeline_name,
                "run_id": run_response.run_id,
                "status": "InProgress"
            }
            
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        except Exception as e:
            return {"error": f"Data Factory pipeline start error: {str(e)}"}
    
    def get_pipeline_status(self, factory_name, run_id):
        try:
            if not self.subscription_id:
                return {"error": "AZURE_SUBSCRIPTION_ID not configured"}
            
            adf_client = DataFactoryManagementClient(
                self.credential, 
                self.subscription_id
            )
            
            run_info = adf_client.pipeline_runs.get(
                self.resource_group, 
                factory_name, 
                run_id
            )
            
            result = {
                "factory_name": factory_name,
                "run_id": run_id,
                "status": run_info.status,
                "run_start": run_info.run_start.isoformat() if run_info.run_start else None,
                "run_end": run_info.run_end.isoformat() if run_info.run_end else None,
                "duration_in_ms": run_info.duration_in_ms
            }
            
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        except Exception as e:
            return {"error": f"Data Factory pipeline status error: {str(e)}"}

class MCPHandler(BaseHTTPRequestHandler):
    def __init__(self, mcp_server, *args, **kwargs):
        self.mcp_server = mcp_server
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request = json.loads(post_data.decode('utf-8'))
            response = self.mcp_server.handle_request(request)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')

if __name__ == "__main__":
    server = AzureMCP()
    
    def handler(*args, **kwargs):
        MCPHandler(server, *args, **kwargs)
    
    httpd = HTTPServer(('0.0.0.0', 8000), handler)
    print("Azure MCP Server running on port 8000")
    httpd.serve_forever()