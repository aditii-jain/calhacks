import os
from vapi import Vapi
from dotenv import load_dotenv

load_dotenv()

# Initialize the Vapi client
try:
    client = Vapi(token=os.getenv("VAPI_API_KEY"))
    print("Successfully connected to Vapi client")
        
except Exception as error:
    print(f"Error connecting to Vapi client: {error}")
    print("Please check your VAPI_API_KEY in the .env file")
    raise error

def make_outbound_call(customer_phone_number: str, assistant_id: str, phone_number_id: str, variable_values: dict = None) -> dict:
    """
    Make an outbound call using Vapi assistant
    
    Args:
        customer_phone_number (str): The phone number to call (E.164 format, e.g. +1234567890)
        assistant_id (str): Your Vapi assistant ID
        phone_number_id (str): Your Vapi phone number ID
        variable_values (dict): Optional variables to pass to the assistant
    
    Returns:
        dict: Call response object
    """
    try:
        # Create the call parameters
        call_params = {
            "assistant_id": assistant_id,
            "phone_number_id": phone_number_id,
            "customer": {
                "number": customer_phone_number
            }
        }
        
        # Add variable values if provided
        if variable_values:
            call_params["assistant_overrides"] = {
                "variable_values": variable_values
            }
        
        # Create the call
        call = client.calls.create(**call_params)
        
        print(f"Outbound call initiated: {call.id}")
        return call
        
    except Exception as error:
        print(f"Error making outbound call: {error}")
        raise error

def list_assistants():
    """List all available assistants."""
    try:
        assistants = client.assistants.list()
        print("Available assistants:")
        for assistant in assistants:
            print(f"ID: {assistant.id}, Name: {assistant.name if hasattr(assistant, 'name') else 'No name'}")
        return assistants
    except Exception as error:
        print(f"Error listing assistants: {error}")
        raise error

def list_phone_numbers():
    """List all available phone numbers."""
    try:
        phone_numbers = client.phone_numbers.list()
        print("Available phone numbers:")
        for phone in phone_numbers:
            print(f"ID: {phone.id}, Number: {phone.number}")
        return phone_numbers
    except Exception as error:
        print(f"Error listing phone numbers: {error}")
        raise error

if __name__ == "__main__":
    print("Vapi Voice Agent Client Ready")
    print("Use make_outbound_call() to initiate calls with assistants")
