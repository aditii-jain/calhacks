import re

def analyze_transcript(transcript):
    """
    Analyze a conversation transcript to determine user's decisions about:
    1. Emergency contact notifications
    2. Shelter directions
    3. Shelter location mentioned
    """
    
    # Convert transcript to lowercase for easier analysis
    transcript_lower = transcript.lower() if transcript else ""
    
    # Initialize results
    analysis = {
        "wants_emergency_contacts": None,  # True/False/None
        "wants_shelter_directions": None,  # True/False/None
        "emergency_contacts_confidence": 0,
        "shelter_directions_confidence": 0,
        "shelter_location": None,  # Extracted shelter name/location
        "key_phrases": []
    }
    
    # Keywords for emergency contact notification
    emergency_contact_yes = [
        "yes.*notify.*contact", "notify.*emergency.*contact", "call.*emergency.*contact",
        "contact.*family", "text.*family", "call.*family", "notify.*family",
        "yes.*contact", "please.*contact", "alert.*contact"
    ]
    
    emergency_contact_no = [
        "no.*contact", "don't.*contact", "not.*contact", "no.*notify",
        "don't.*notify", "skip.*contact", "no.*family", "don't.*family"
    ]
    
    # Keywords for shelter directions
    shelter_directions_yes = [
        "yes.*direction", "send.*direction", "need.*direction", "want.*direction",
        "text.*direction", "yes.*location", "send.*location", "how.*get.*there",
        "directions.*shelter", "where.*shelter"
    ]
    
    shelter_directions_no = [
        "no.*direction", "don't.*need.*direction", "know.*way", "have.*directions",
        "no.*location", "don't.*send", "not.*need.*direction"
    ]
    
    # Extract shelter location patterns
    shelter_patterns = [
        r"shelter (?:is )?at ([^.]+)",
        r"nearest shelter (?:is )?(?:at )?([^.]+)",
        r"go to ([^.]+(?:center|school|park|hall|building|facility))",
        r"([^.]+(?:recreation center|community center|civic center|park|school|hall))",
        r"located at ([^.]+)",
        r"address (?:is )?([^.]+)"
    ]
    
    # Analyze emergency contact intent
    emergency_yes_matches = sum(1 for pattern in emergency_contact_yes if re.search(pattern, transcript_lower))
    emergency_no_matches = sum(1 for pattern in emergency_contact_no if re.search(pattern, transcript_lower))
    
    if emergency_yes_matches > emergency_no_matches:
        analysis["wants_emergency_contacts"] = True
        analysis["emergency_contacts_confidence"] = min(emergency_yes_matches * 25, 100)
        analysis["key_phrases"].append("User wants emergency contacts notified")
    elif emergency_no_matches > emergency_yes_matches:
        analysis["wants_emergency_contacts"] = False
        analysis["emergency_contacts_confidence"] = min(emergency_no_matches * 25, 100)
        analysis["key_phrases"].append("User declined emergency contact notification")
    
    # Analyze shelter directions intent
    shelter_yes_matches = sum(1 for pattern in shelter_directions_yes if re.search(pattern, transcript_lower))
    shelter_no_matches = sum(1 for pattern in shelter_directions_no if re.search(pattern, transcript_lower))
    
    if shelter_yes_matches > shelter_no_matches:
        analysis["wants_shelter_directions"] = True
        analysis["shelter_directions_confidence"] = min(shelter_yes_matches * 25, 100)
        analysis["key_phrases"].append("User wants shelter directions")
    elif shelter_no_matches > shelter_yes_matches:
        analysis["wants_shelter_directions"] = False
        analysis["shelter_directions_confidence"] = min(shelter_no_matches * 25, 100)
        analysis["key_phrases"].append("User declined shelter directions")
    
    # Extract shelter location
    for pattern in shelter_patterns:
        match = re.search(pattern, transcript_lower)
        if match:
            shelter_location = match.group(1).strip()
            # Clean up common artifacts
            shelter_location = re.sub(r'\s+', ' ', shelter_location)  # Multiple spaces
            shelter_location = shelter_location.replace(',', ', ')  # Fix comma spacing
            analysis["shelter_location"] = shelter_location.title()  # Capitalize properly
            analysis["key_phrases"].append(f"Shelter mentioned: {analysis['shelter_location']}")
            break
    
    return analysis

def get_google_maps_pin(shelter_location):
    """
    Generate a Google Maps pin URL for the shelter location.
    
    Args:
        shelter_location (str): The shelter name/location
        
    Returns:
        str: Google Maps URL with pin, or None if no location
    """
    if not shelter_location:
        return None
    
    # Encode the location for URL
    import urllib.parse
    encoded_location = urllib.parse.quote_plus(shelter_location)
    
    # Generate Google Maps URL with pin
    maps_url = f"https://maps.google.com/maps?q={encoded_location}&t=m&z=15"
    
    return maps_url

def print_analysis(transcript):
    """Analyze transcript and print formatted results."""
    
    print("\n" + "="*60)
    print("🚨 EMERGENCY CALL TRANSCRIPT ANALYSIS")
    print("="*60)
    
    analysis = analyze_transcript(transcript)
    
    # Format results
    emergency_status = "✅ WANTS" if analysis['wants_emergency_contacts'] else "❌ DECLINED" if analysis['wants_emergency_contacts'] is False else "❓ UNCLEAR"
    shelter_status = "✅ WANTS" if analysis['wants_shelter_directions'] else "❌ DECLINED" if analysis['wants_shelter_directions'] is False else "❓ UNCLEAR"
    
    print(f"\n📊 ANALYSIS RESULTS:")
    print(f"Emergency Contacts: {emergency_status} (confidence: {analysis['emergency_contacts_confidence']}%)")
    print(f"Shelter Directions: {shelter_status} (confidence: {analysis['shelter_directions_confidence']}%)")
    
    # Show shelter location if found
    if analysis['shelter_location']:
        maps_url = get_google_maps_pin(analysis['shelter_location'])
        print(f"📍 Shelter Location: {analysis['shelter_location']}")
        print(f"🗺️  Google Maps: {maps_url}")
    else:
        print(f"📍 Shelter Location: Not specified")
    
    if analysis['key_phrases']:
        print(f"\n🔍 KEY FINDINGS:")
        for phrase in analysis['key_phrases']:
            print(f"• {phrase}")
    
    print(f"\n📋 ACTIONS NEEDED:")
    if analysis['wants_emergency_contacts'] == True:
        print("• 🚨 Notify emergency contacts")
    if analysis['wants_shelter_directions'] == True:
        print("• 📍 Send shelter directions")
        if analysis['shelter_location']:
            print(f"  → Location: {analysis['shelter_location']}")
    if analysis['wants_emergency_contacts'] == False and analysis['wants_shelter_directions'] == False:
        print("• ✅ No actions needed - user declined assistance")
    if analysis['wants_emergency_contacts'] is None and analysis['wants_shelter_directions'] is None:
        print("• ❓ Unclear - may need manual review")
    
    print(f"\n📝 FULL TRANSCRIPT:")
    print(transcript)
    print("="*60)
    
    return analysis

def test_scenarios():
    """Test the analyzer with different scenarios."""
    
    scenarios = [
        {
            "name": "User wants both services",
            "transcript": "AI: Hi! We've detected a wildfire near Los Angeles. I'm here to help — would you like to know where the nearest shelter is? User: Yes, I need shelter information. AI: The nearest shelter is at Griffith Park Recreation Center. Would you like directions? User: Yes, please send directions. AI: Would you like me to notify your emergency contacts? User: Yes, please contact my family."
        },
        {
            "name": "User declines both services", 
            "transcript": "AI: Hi! We've detected a wildfire near Los Angeles. I'm here to help — would you like to know where the nearest shelter is? User: No, I'm okay. AI: Would you like me to notify your emergency contacts? User: No, don't contact anyone."
        },
        {
            "name": "User wants shelter but no contacts",
            "transcript": "AI: Hi! We've detected a wildfire near Los Angeles. I'm here to help — would you like to know where the nearest shelter is? User: Yes, I need shelter info. AI: The nearest shelter is at Griffith Park Recreation Center. Would you like directions? User: Yes, send directions please. AI: Would you like me to notify your emergency contacts? User: No, don't notify anyone."
        },
        {
            "name": "User wants contacts but no directions",
            "transcript": "AI: Hi! We've detected a wildfire near Los Angeles. I'm here to help — would you like to know where the nearest shelter is? User: Yes, tell me about shelters. AI: The nearest shelter is at Griffith Park Recreation Center. Would you like directions? User: No, I know how to get there. AI: Would you like me to notify your emergency contacts? User: Yes, please call my family."
        }
    ]
    
    print("🧪 TESTING TRANSCRIPT ANALYZER")
    print("=" * 50)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Test {i}: {scenario['name']}")
        print_analysis(scenario['transcript'])
        
        if i < len(scenarios):
            input("\nPress Enter to continue to next test...")

if __name__ == "__main__":
    print("🚨 Emergency Call Transcript Analyzer")
    print("Choose an option:")
    print("1. Test with sample scenarios")
    print("2. Analyze custom transcript")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_scenarios()
    elif choice == "2":
        print("\nPaste your transcript below (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        
        transcript = " ".join(lines)
        if transcript.strip():
            print_analysis(transcript)
        else:
            print("❌ No transcript provided")
    else:
        print("❌ Invalid choice") 