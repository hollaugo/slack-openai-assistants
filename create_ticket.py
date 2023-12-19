import os
import uuid
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Slack Bolt App with the bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def create_ticket(client, subject, from_user, type_of_question, description):
    """
    Create a ticket and post it to a Slack channel using Slack Bolt with a fun and engaging format.

    :param client: Instance of the Slack Bolt app.
    :param subject: Subject of the ticket.
    :param from_user: Slack user ID of the person creating the ticket.
    :param type_of_question: Type of question or issue.
    :param description: Detailed description of the issue.
    :return: Simplified response indicating the outcome of the Slack API call.
    """
    # Generate a unique ticket ID
    ticket_id = str(uuid.uuid4())

    # Create a stylized message to post to Slack
    message = (
        f":ticket: *Ticket ID*: {ticket_id}\n"
        f":bulb: *Subject*: _{subject}_\n"
        f":bust_in_silhouette: *From*: <@{from_user}>\n"
        f":question: *Type*: {type_of_question}\n"
        f":memo: *Description*: ```{description}```\n"
        f":rocket: *Status*: `New`"
    )

    try:
        # Use the Bolt client to post the message
        response = client.chat_postMessage(
            channel="C06A0J5FW8K",
            text=message,
            mrkdwn=True
        )
        # Simplify the response
        if response.get("ok"):
            return {"message": "Ticket created successfully", "ticket_id": ticket_id}
        else:
            return {"error": "Failed to create ticket"}
    except Exception as e:
        # Handle exceptions
        return {"error": str(e)}



# Example usage (Uncomment and replace placeholders with actual values)
#create_ticket(app.client, "Shift Change", "U05K6HV02UE", "Shift Management", "I may not be abel to attend work tomorrow, how do i reschedule my shift", "C06A0J5FW8K")
