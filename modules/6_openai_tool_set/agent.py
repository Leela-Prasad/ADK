from google.adk.agents import LlmAgent
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

from dotenv import load_dotenv
load_dotenv()

openapi_spec_string ="""
{
  "openapi": "3.0.0",
  "info": {
    "title": "HTTPBin API",
    "version": "1.0.0",
    "description": "A simple API for testing HTTP operations"
  },
  "servers": [
    {
      "url": "https://httpbin.org"
    }
  ],
  "paths": {
    "/get": {
      "get": {
        "operationId": "test_get_request",
        "summary": "Test a GET request",
        "description": "Returns the query parameters sent in the request. Use this to test GET requests.",
        "parameters": [
          {
            "name": "message",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string"
            },
            "description": "A test message to echo back"
          }
        ],
        "responses": {
          "200": {
            "description": "Successful response with echoed parameters"
          }
        }
      }
    },
    "/post": {
      "post": {
        "operationId": "test_post_request",
        "summary": "Test a POST request",
        "description": "Accepts and echoes back POST data. Use this to test POST requests.",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "name": {
                    "type": "string",
                    "description": "A name to include in the POST body"
                  },
                  "message": {
                    "type": "string",
                    "description": "A message to include in the POST body"
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successful response with echoed POST data"
          }
        }
      }
    },
    "/ip": {
      "get": {
        "operationId": "get_ip_address",
        "summary": "Get origin IP",
        "description": "Returns the caller's IP address.",
        "responses": {
          "200": {
            "description": "The origin IP address"
          }
        }
      }
    },
    "/user-agent": {
      "get": {
        "operationId": "get_user_agent",
        "summary": "Get User-Agent",
        "description": "Returns the User-Agent header of the request.",
        "responses": {
          "200": {
            "description": "The User-Agent string"
          }
        }
      }
    }
  }
}
"""

# Create OpenAPIToolset
httpbin_toolset = OpenAPIToolset(
    spec_str=openapi_spec_string,
    spec_str_type="json"
)

root_agent = LlmAgent(
    name="api_agent",
    model="openai/gpt-4o-mini",
    tools=[httpbin_toolset],
    description="An agent that interacts with REST APIs using OpenAPI-generated tools.",
    instruction="""You are an API testing assistant
    You have access to tools generated from an OpenAPI specification for httpbin.org
    Use the available tools to fulfill user requests:
    - test_get_request: Send a GET request with query parameters
    - test_post_request: send a POST request with JSON body
    - get_ip_address: Get the Origin IP address
    - get_user_agent: Get the User-Agent string
    when making requests, clearly explain what you are doing and show the results.
    """
)
