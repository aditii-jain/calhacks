#!/usr/bin/env python3
"""
Test script for emergency contact and SMS functions
"""

import sys
import os

# Add the backend directory to the path
sys.path.append('backend')

# Import the functions we want to test
from voice_agent.trigger_call import get_emergency_contacts, send_sms

def test_get_emergency_contacts():
    """Test the get_emergency_contacts function"""
    print("🧪 Testing get_emergency_contacts function...")
    
    # Test with the phone number from the logs
    test_phone = "+16692209078"
    print(f"🔍 Testing with phone number: {test_phone}")
    
    contacts = get_emergency_contacts(test_phone)
    
    print(f"📋 Result: Found {len(contacts)} emergency contacts")
    for i, contact in enumerate(contacts, 1):
        print(f"   {i}. {contact}")
    
    return contacts

def test_send_sms():
    """Test the send_sms function"""
    print("\n🧪 Testing send_sms function...")
    
    # Test with a simple message
    test_phone = "+16692209078"  # Use the same phone number
    test_message = "🧪 This is a test SMS from the emergency system. Please ignore."
    
    print(f"📱 Sending test SMS to: {test_phone}")
    print(f"📝 Message: {test_message}")
    
    result = send_sms(test_phone, test_message)
    
    print(f"📋 SMS Result: {result}")
    return result

def main():
    """Run all tests"""
    print("🚀 Starting emergency function tests...\n")
    
    # Test 1: Emergency Contacts
    contacts = test_get_emergency_contacts()
    
    # Test 2: SMS (only if we found contacts or want to test anyway)
    sms_result = test_send_sms()
    
    # Test 3: If we found emergency contacts, test sending SMS to them
    if contacts:
        print(f"\n🧪 Testing SMS to emergency contacts...")
        for contact in contacts:
            print(f"📱 Sending test SMS to emergency contact: {contact}")
            contact_result = send_sms(contact, "🚨 This is a test emergency alert. Your contact may need assistance. (This is just a test - please ignore)")
            print(f"📋 Result for {contact}: {contact_result}")
    else:
        print(f"\n⚠️ No emergency contacts found, skipping emergency contact SMS test")
    
    print(f"\n✅ Emergency function tests completed!")

if __name__ == "__main__":
    main() 