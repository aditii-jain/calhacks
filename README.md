Inspiration
Our whole team is from Los Angeles and the Los Angeles wildfires didn't just burn through our neighborhoods - they burned through our hearts. As we watched our community scramble for information, we witnessed something heartbreaking: while some of us frantically refreshed social media for updates, our grandparents, elderly neighbors, and loved ones with disabilities sat in silence, waiting for someone to tell them if they were safe. Information inequality in crisis isn't just inconvenient - it's deadly. We realized that the people who need disaster information the most are often the last to receive it. Your grandmother doesn't scroll Twitter during a wildfire. Your disabled neighbor might not have access to emergency apps. The elderly couple down the street doesn't know which news sources to trust. While the digitally connected world shares real-time updates, vulnerable populations remain in the dark, sometimes with devastating consequences. Sheltr was born from a simple but urgent belief: every person deserves to know when danger is approaching, regardless of their digital literacy or social media presence.

What it does
Sheltr is an AI-powered guardian that bridges the dangerous gap between digital crisis information and the people who need it most. Our platform continuously monitors social media streams, identifies emerging disasters through advanced multimodal AI analysis, and proactively reaches vulnerable individuals with personalized, life-saving communication. Here's how we protect those who matter most: 🔍 Intelligent Crisis Detection

Real-time analysis of social media feeds using our fine-tuned multimodal AI model
Fusion of text and image data to accurately identify and classify disaster events
Severity scoring and geographic mapping to identify "Red Zones" requiring immediate action
📞 Proactive, Personal Outreach

Automated, empathetic phone calls to registered vulnerable individuals in affected areas
Location-aware text alerts sent to emergency contacts
Human-like conversation that provides guidance, resources, and most importantly—comfort
🎯 Designed for Digital Equity

Specifically built for elderly, disabled, and digitally disconnected populations
Uses familiar communication methods (phone calls, SMS) instead of requiring app downloads
Pre-registered family members can ensure their loved ones are protected
How we built it
The AI Classifier: We fine-tuned a Llama 3 multimodal model using the CrisisMMD dataset—a comprehensive collection of thousands of manually annotated disaster-related social media posts. This specialized training enables our AI to understand the nuanced relationship between crisis imagery and text, accurately identifying disaster types, information quality, and urgency levels.

The Detection Engine: Our system continuously scrapes and analyzes social media feeds, classifying posts across multiple parameters:

Disaster type and severity
Information reliability and usefulness
Geographic relevance and impact zones
Urgency scoring for immediate response
The Response Network: When threat levels reach critical thresholds in any geographic area, Sheltr's automated response system springs into action:

Vapi-powered voice calls deliver personalized, location-specific guidance to registered vulnerable individuals Gemini-generated text alerts notify emergency contacts with status updates and safety confirmations Intelligent routing using MCP that browses the internet ensures the right information about safety shelters reaches the right people at the right time

The Safety Net: Every interaction is designed to provide not just information, but reassurance. Our AI agent doesn't just warn - it guides, comforts, and connects people to resources, ensuring no one faces crisis alone.

Challenges we ran into
Beyond the usual rate limits and depleted API credits, our biggest challenge was supporting a team member who was new to hackathons. None of us had worked with Vapi before, and we had to quickly learn about Smithery to integrate MCP services - all while racing against the clock. The learning curve was steep, but it brought our team closer together.

Accomplishments that we're proud of
Our biggest accomplishment is the clean system architecture we built. We successfully dockerized our entire API on Railway's cloud platform, orchestrated multiple AI models working in harmony, and delivered a polished frontend experience. Most importantly, our API pipeline ensures that vulnerable people receive critical information through both personalized phone calls and SMS alerts—exactly what we set out to achieve.

What we learned
This hackathon pushed us to master new technologies: MCP integration, Gemini API, advanced AI coding tools, and Railway deployment. We also learned that the most impactful solutions often come from addressing overlooked problems with familiar tools.

What's next for Sheltr
Immediate Goals:

Deploy a live Twitter bot for real-time disaster monitoring beyond historical data Add multilingual support to serve diverse communities Integrate with official emergency sources (FEMA, USGS) for enhanced accuracy and validation

Future Vision:

Improve personalization based on user demographics and accessibility needs Build a mobile app for easier family registration and alert customization Launch community outreach programs to connect with vulnerable populations Scale to a production-ready platform deployable in disaster-prone regions worldwide

Our ultimate goal remains unchanged: ensuring that when disaster strikes, no one - regardless of age, ability, or digital access - gets left behind.

https://youtu.be/pezSakegb64
