from http.server import BaseHTTPRequestHandler, HTTPServer
import importlib.util
import inspect
import json
import os
import sys

class PyLamHTTPRequestHandler(BaseHTTPRequestHandler):

  lambdaHandlerFunctionName = None
  lambdaHandler = None
  
  def __init__(self, *args, config, **kwargs):
      self.loadHandler(config['entryPoint'], config['pathFromProjectRoot'],
                       config['fileExtension'])
      super().__init__(*args, **kwargs)

  def loadHandler(self, entryPoint, pathFromProjectRoot, lhFileExtension):
    print(f"Load handler called. entryPoint={entryPoint} pathFromProjectRoot={pathFromProjectRoot}")
    parts = entryPoint.split(".")
    lhFileName = parts[0]
    self.lambdaHandlerFunctionName = parts[1]
    lhfString = "./{a}/{b}{c}".format(
      a=pathFromProjectRoot, b=lhFileName, c=lhFileExtension)

    lhfAbsPath = os.path.abspath(lhfString)
    lhfModule = lhfAbsPath.split("/")[-2]

    spec = importlib.util.spec_from_file_location(lhfModule, lhfAbsPath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    self.lambdaHandler = getattr(module, self.lambdaHandlerFunctionName)

  def invokeLambda(self, reqBody):
    try:
      event = reqBody
      context = {
        "functionName": self.lambdaHandlerFunctionName,
        "functionVersion": '1',
        "memoryLimitInMB": '1024',
        "functionVersion": '$LATEST',
        "logGroupName": '/aws/lambda/' + self.lambdaHandlerFunctionName,
        "invokedFunctionArn": 'arn:aws:lambda:LOCAL:123456789012:function:'
          + self.lambdaHandlerFunctionName,
        "logStreamName": '2024/12/08/[$LATEST]99999999999999999999',
        "callbackWaitsForEmptyEventLoop": True,
        "awsRequestId": '12345678-1234-1234-1234-123456789012'
      }
      signature = inspect.signature(self.lambdaHandler)
      numParams = len(signature.parameters.values())
      if numParams == 1:
        lambdaResults = self.lambdaHandler(event)
      elif numParams == 2: 
        lambdaResults = self.lambdaHandler(event, context)
      else:
        lambdaResults = self.lambdaHandler(event, context, None)

      return lambdaResults
    except Exception as exc:
      msg = "Exception running the Lambda handler: " + str(exc)
      print(msg)
      raise Exception(msg)
    
  def do_POST(self):
    try:
      if (self.lambdaHandler == None):
         raise Exception("Error: The Lambda handler was not initialized")

      if (self.path == '/2015-03-31/functions/function/invocations'):
        ## Read the body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode("utf-8")
        json_body = json.loads(body)
        result = self.invokeLambda(json_body)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))
      else:
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"message": "Not found" }
        self.wfile.write(json.dumps(response).encode("utf-8"))
    except Exception as exc:
        self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"message": str(exc) }
        self.wfile.write(json.dumps(response).encode("utf-8"))

def run_pylam():
    server_class = HTTPServer
    port = 9000
    server_address = ('', port)
    
    def handler(*args, **kwargs):
       entryPoint = sys.argv[1]
       pathFromProjectRoot = sys.argv[2] if (len(sys.argv) >= 3) else ""
       fileExtension = sys.argv[3] if (len(sys.argv) >= 4) else ".py"
       config = {
          "entryPoint": entryPoint,
          "pathFromProjectRoot": pathFromProjectRoot,
          "fileExtension": fileExtension
       }
       return PyLamHTTPRequestHandler(*args, config=config, **kwargs)
    
    httpd = server_class(server_address, handler)

    print(f"Server running on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_pylam()
