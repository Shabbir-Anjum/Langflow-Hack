import argparse
import json
from argparse import RawTextHelpFormatter
import requests
from typing import Optional
import warnings
import streamlit as st

try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "http://127.0.0.1:7860/api/v1/run"
FLOW_ID = "4f7a88b3-2788-4e71-8906-635221d0e211"
ENDPOINT = "" # You can set a specific endpoint name in the flow settings

# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
  "Prompt-2HiQw": {},
  "ChatInput-N5SyW": {},
  "CustomComponent-Gb1Ai": {},
  "ChatOutput-lM4Pj": {},
  "OpenAIModel-N8iQi": {}
}

def run_flow(message: str,
  endpoint: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  api_key: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if api_key:
        headers = {"x-api-key": api_key}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

def main():
    st.title("Run Flow with Message and Tweaks")

    message = st.text_input("Message", "your message here")
    endpoint = st.text_input("Endpoint", ENDPOINT or FLOW_ID)
    tweaks = st.text_area("Tweaks (JSON)", json.dumps(TWEAKS))
    api_key = st.text_input("API Key", type="password")
    output_type = st.text_input("Output Type", "chat")
    input_type = st.text_input("Input Type", "chat")
    upload_file_path = st.text_input("Upload File Path")
    components = st.text_input("Components")

    if st.button("Run Flow"):
        try:
            tweaks_dict = json.loads(tweaks)
        except json.JSONDecodeError:
            st.error("Invalid tweaks JSON string")
            return

        if upload_file_path:
            if not upload_file:
                st.error("Langflow is not installed. Please install it to use the upload_file function.")
                return
            elif not components:
                st.error("You need to provide the components to upload the file to.")
                return
            tweaks_dict = upload_file(file_path=upload_file_path, host=BASE_API_URL, flow_id=ENDPOINT, components=components, tweaks=tweaks_dict)

        response = run_flow(
            message=message,
            endpoint=endpoint,
            output_type=output_type,
            input_type=input_type,
            tweaks=tweaks_dict,
            api_key=api_key
        )

        st.json(response)

if __name__ == "__main__":
    main()