# pylam

## What is it?
Try out a Lambda function locally before you upload it to the cloud.

A Python-based implementation of [trylam](https://github.com/tim1e9/trylam).

## How do I use it?

Pylam runs as a small Python module. It can be installed as a development dependency,
so that it adds nothing to the production runtime. 

A typical setup involves doing the following:
1. Add a development dependency to the Lambda Python project:
    ```
    pip install -f requirements-dev.txt
    ```

2. Once installed, start up Pylam as follows:
    ```
    python -m pylam lambda_function.lambda_handler
    ```
   Where `lambda_function.lambda_handler` is the Lambda file name and function name respectively.

   **NOTE:** Two additional optional parameters can be specified:
    - Argument 2: The path to the Lambda entrypoint. This can be useful if the
      function is not in the root directory of the project.
      Do not include leading or trailing slashes (/)
    - Arrgument 3: The file extension. By default `.py` is used. To set to blank,
      pass the string "NONE".

    A full invocation may look like the following:
    ```
    python -m pylam lambda_function.lambda_handler src/lambdas .py
    ```

3. To invoke Pylam, make an HTTP call on port 9000 (the default port). For example:
    ```
    curl --request POST --url http://localhost:9000/ --data '{ "key1": "value1", "key2": [ "item21","item22"]}'
    ```
    **NOTE**: The `--data` will be used as the `event` parameter to the Lambda function.
    
    After running, you should see the results of the invocation on the console. Example:
    ```
    {"statusCode":200,"body":"\"Hello from Lambda!\""}
    ```

4. To Use Visual Studio Code to debug the function:
   Add a launch configuration:
    ```
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Hot dog debug",
                "type": "debugpy",
                "request": "launch",
                "module": "pylam",
                "args": ["lambda_function.lambda_handler", "."],
              "console": "integratedTerminal"
            }  
        ]
    }
    ```
   **NOTE::** The above configuration assumes the Lambda entry point is named `lambda_handler()`
   and the name of the Lambda file is `lambda_function.py`.

   Set a breakpoint in the Lambda handler, and invoke the function via a curl call:
    ```
    curl --request POST --url http://localhost:9000/2015-03-31/functions/function/invocations --data '{ "key1": "value1", "key2": [ "item21","item22"]}'
    ```

## How do I Build/Publish it?

From the root directory:
1. Bump the version number in `pyproject.toml` and `src/pylam/__init__.py`
   Set it to something like 0.9.0
2. Run `python -m build`
3. Run `pip install --force-reinstall dist/pylam-0.9.0-py3-none-any.whl`

## Additional information

This is a Python-based implementation of [trylam](https://github.com/tim1e9/trylam),
so for any questions, please open an issue in that repository.