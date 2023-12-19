import os
import json
import openai
from time import sleep
from dotenv import load_dotenv
import io  # Import for in-memory file handling

# Import the create_ticket function from your script
from create_ticket import create_ticket, app

# Load your OpenAI API key from the .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def execute_function(function_name, arguments, from_user):
    """
    Execute a function based on the function name and provided arguments.
    """
    if function_name == 'create_ticket':
        subject = arguments.get("subject")
        type_of_question = arguments.get("type_of_question")
        description = arguments.get("description")
        return create_ticket(app.client, subject, from_user, type_of_question, description)
    else:
        return "Function not recognized"

def process_thread_with_assistant(user_query, assistant_id, model="gpt-4-1106-preview", from_user=None):
    """
    Process a thread with an assistant and handle the response which includes text and images.

    :param user_query: The user's query.
    :param assistant_id: The ID of the assistant to be used.
    :param model: The model version of the assistant.
    :param from_user: The user ID from whom the query originated.
    :return: A dictionary containing text responses and in-memory file objects.
    """
    response_texts = []  # List to store text responses
    response_files = []  # List to store file IDs
    in_memory_files = []  # List to store in-memory file objects

    try:
        print("Creating a thread for the user query...")
        thread = openai.Client().beta.threads.create()
        print(f"Thread created with ID: {thread.id}")

        print("Adding the user query as a message to the thread...")
        openai.Client().beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_query
        )
        print("User query added to the thread.")

        print("Creating a run to process the thread with the assistant...")
        run = openai.Client().beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
            model=model
        )
        print(f"Run created with ID: {run.id}")

        while True:
            print("Checking the status of the run...")
            run_status = openai.Client().beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(f"Current status of the run: {run_status.status}")

            if run_status.status == "requires_action":
                print("Run requires action. Executing specified function...")
                tool_call = run_status.required_action.submit_tool_outputs.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                function_output = execute_function(function_name, arguments, from_user)
                function_output_str = json.dumps(function_output)

                print("Submitting tool outputs...")
                openai.Client().beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": tool_call.id,
                        "output": function_output_str
                    }]
                )
                print("Tool outputs submitted.")

            elif run_status.status in ["completed", "failed", "cancelled"]:
                print("Fetching messages added by the assistant...")
                messages = openai.Client().beta.threads.messages.list(thread_id=thread.id)
                for message in messages.data:
                    if message.role == "assistant":
                        for content in message.content:
                            if content.type == "text":
                                response_texts.append(content.text.value)
                            elif content.type == "image_file":
                                file_id = content.image_file.file_id
                                response_files.append(file_id)

                print("Messages fetched. Retrieving content for each file ID...")
                for file_id in response_files:
                    try:
                        print(f"Retrieving content for file ID: {file_id}")
                        # Retrieve file content from OpenAI API
                        file_response = openai.Client().files.content(file_id)
                        if hasattr(file_response, 'content'):
                            # If the response has a 'content' attribute, use it as binary content
                            file_content = file_response.content
                        else:
                            # Otherwise, use the response directly
                            file_content = file_response

                        in_memory_file = io.BytesIO(file_content)
                        in_memory_files.append(in_memory_file)
                        print(f"In-memory file object created for file ID: {file_id}")
                    except Exception as e:
                        print(f"Failed to retrieve content for file ID: {file_id}. Error: {e}")

                break
            sleep(1)

        return {"text": response_texts, "in_memory_files": in_memory_files}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"text": [], "in_memory_files": []}

# Example usage
#user_query = "Show me a sample pie chart"
#assistant_id = "asst_P3bdvDVwLXQ49vK2AVjZNCd6"
#from_user_id = "U052337J8QH"
#response = process_thread_with_assistant(user_query, assistant_id, from_user=from_user_id)
#print("Final response:", response)
