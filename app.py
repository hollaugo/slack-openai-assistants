import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import threading

# Import the function from assistants.py
from assistants import process_thread_with_assistant

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Listen and handle messages 
@app.message("")
def message_handler(message, say, ack):
    ack()  # Acknowledge the event immediately
    user_query = message['text']
    assistant_id = "asst_P3bdvDVwLXQ49vK2AVjZNCd6"
    from_user = message['user']

    def process_and_respond():
        response = process_thread_with_assistant(user_query, assistant_id, from_user=from_user)
        if response:
            # Check if there are any in-memory files to upload
            if response.get("in_memory_files"):
                for i, in_memory_file in enumerate(response["in_memory_files"]):
                    # Use the corresponding text as the annotation for the file
                    annotation_text = response["text"][i] if i < len(response["text"]) else "Here's the file you requested:"
                    app.client.files_upload(
                        channels=message['channel'],
                        file=in_memory_file,
                        filename="image.png",  # or dynamically set the filename
                        initial_comment=annotation_text,  # Text response as annotation
                        title="Uploaded Image"
                    )
            else:
                # If no files to upload, send text responses normally
                for text in response.get("text", []):
                    say(text, thread_ts=message['ts'])
        else:
            say("Sorry, I couldn't process your request.", thread_ts=message['ts'])

    threading.Thread(target=process_and_respond).start()



# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
