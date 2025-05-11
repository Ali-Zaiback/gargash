from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Agent, Customer, Call
from datetime import datetime, UTC
import random
import requests
import json

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def create_data(db: Session):
    """Generates and adds sample data to the database."""
    # Clear existing data
    db.query(Call).delete()
    db.query(Customer).delete()
    db.query(Agent).delete()
    db.commit()

    agents = []
    customers = []
    calls = []

    # Create 10 agents
    for i in range(1, 8):
        agent = Agent(
            name=f"Agent {i}",
            employee_id=f"EMP{i:03d}",
            email=f"agent{i}@example.com",
            phone_number=f"+97154275672{i}",
            specialization=random.choice(["Sales", "Service", "AMG Specialist"])
        )
        agents.append(agent)
        db.add(agent)

    # Create 10 customers
    for i in range(1, 8):
        customer = Customer(
            phone_number=f"+97154275678{i}",
            email=f"customer{i}@example.com",
            name=f"Customer {i}"
        )
        customers.append(customer)
        db.add(customer)

    db.commit() # Commit agents and customers to get their IDs

    # Create 10 calls, linking agents and customers
    sample_transcripts = [
        "Agent: Good morning, thank you for calling Mercedes-Benz. How can I help you today? Customer: Hi, I'm interested in learning more about your SUV range, specifically family-friendly options. Agent: Absolutely! We have several excellent SUVs. Are you looking for something for city driving, or perhaps something capable of light off-roading for weekend trips? Customer: Mostly city, but definitely something for weekend leisure trips, maybe some light desert driving. Safety is top priority, and space for my family of five. Agent: For a family of five with those priorities, I highly recommend the Mercedes-Benz GLE. It offers exceptional safety features, a very spacious interior, and a luxurious feel. It's also well-suited for various driving conditions. Customer: The GLE sounds interesting. Can you tell me about the infotainment system and comfort features? Agent: The GLE features our MBUX infotainment system, which is very intuitive and great for keeping everyone entertained. The seats are incredibly comfortable, even on longer journeys. Customer: That's good to know. What about engine options and fuel efficiency? And pricing? Agent: We have a range of engine options for the GLE, offering a balance of performance and efficiency. Pricing varies based on the model and options, but we can discuss current offers. Would you be available for a showroom visit this Saturday for a private viewing and test drive? Customer: Saturday could work. Agent: Great, I'll follow up via WhatsApp to confirm the details.",
        "Agent: Welcome to Mercedes-Benz. How may I assist you? Customer: Hello, I'm looking for a luxury sedan. Agent: We have several exquisite sedan models. Are you interested in performance, comfort, or a balance of both? Customer: Comfort and luxury are key. Agent: In that case, the C-Class or E-Class might be perfect. The E-Class is known for its exceptional comfort and advanced features. Customer: Tell me more about the E-Class. Agent: The E-Class offers a smooth ride, a beautifully appointed interior, and cutting-edge technology. It's ideal for both daily commutes and long-distance travel. Customer: What are the engine options? Agent: We have various engine options available, including fuel-efficient hybrids. Customer: And pricing? Agent: Pricing starts from [price range]. We can discuss financing options as well. Customer: Thank you, I'll consider it.",
        "Agent: Mercedes-Benz service, how can I help? Customer: Hi, I'm calling about scheduling a service for my A-Class. Agent: Certainly, what year is your A-Class and what type of service are you looking for? Customer: It's a 2022 model, and I need the standard annual service. Agent: Okay, let me check our availability. What dates work best for you? Customer: Sometime next week would be ideal. Agent: We have openings on Tuesday or Thursday. Which day would you prefer? Customer: Thursday works. Agent: Great, we'll book you in for Thursday at [time]. Is there anything else I can assist you with today? Customer: No, that's all. Thank you. Agent: You're welcome. We look forward to seeing you on Thursday.",
        "Agent: Good afternoon, Mercedes-Benz sales. Customer: Hi, I saw an advertisement for the new GLA and wanted to know more. Agent: The new GLA is a fantastic compact SUV, perfect for city life and weekend getaways. What specifically interests you about it? Customer: I like the look and the size seems right for me. Agent: It's very stylish and surprisingly spacious for its class. It also comes with the latest MBUX system and advanced safety features. Customer: What are the color options? Agent: We have a wide range of colors available, from classic black and white to more vibrant options. You can view them on our website or in the showroom. Customer: I might stop by the showroom this week. Agent: We'd be happy to show you around. Let us know when you plan to visit so we can ensure a sales consultant is available.",
        "Agent: Thank you for calling Mercedes-Benz. Customer: I'm interested in a test drive of the new S-Class. Agent: The S-Class is the pinnacle of luxury. We can certainly arrange a test drive for you. Have you visited our showroom before? Customer: Yes, I have. Agent: Excellent. What days and times work best for your test drive? Customer: I'm free on Monday afternoon. Agent: We have an opening at 2 PM on Monday. Does that work for you? Customer: Yes, that's perfect. Agent: Wonderful. We'll have the S-Class ready for you at 2 PM on Monday. We look forward to seeing you.",
        "Agent: Hello, Mercedes-Benz. Customer: I have a question about financing options for a new GLC. Agent: We have various financing options available to suit your needs. Are you looking to lease or finance the vehicle? Customer: I'm considering both. Agent: We can walk you through the details of both options and help you determine which is best for you. What is your budget range? Customer: I'm looking to keep the monthly payments around [amount]. Agent: Okay, based on that, we can explore different loan or lease terms. Would you like to schedule a consultation with our finance department? Customer: Yes, that would be helpful. Agent: Great, what day and time works for you?",
        "Agent: Mercedes-Benz roadside assistance. Customer: Hi, I have a flat tire on my GLE. Agent: I'm sorry to hear that. Can you please provide your location and a description of the issue? Customer: I'm on [road name] near [landmark], and the front passenger tire is flat. Agent: Thank you. We'll dispatch a technician to your location immediately. Please stay in a safe place away from traffic. Customer: Okay, thank you. Agent: You're welcome. Help is on the way.",
        "Agent: Good morning, Mercedes-Benz. Customer: I'm interested in trading in my current car for a new Mercedes. Agent: We can certainly assist you with a trade-in. What is the make, model, and year of your current vehicle? Customer: It's a [make] [model] from [year]. Agent: Thank you. We'll need to appraise your vehicle to determine its trade-in value. Would you like to schedule an appraisal? Customer: Yes, please. Agent: What day and time works best for you to bring your vehicle in?",
        "Agent: Welcome to Mercedes-Benz. Customer: I'm looking for accessories for my C-Class. Agent: We have a wide range of genuine Mercedes-Benz accessories available for the C-Class, from floor mats to roof racks. What type of accessories are you interested in? Customer: I'm looking for all-weather floor mats and a trunk organizer. Agent: We have those in stock. Would you like to come in to see them or would you like to place an order over the phone? Customer: I'll come in to see them. Agent: Great, our parts department is open until [time].",
        "Agent: Thank you for calling Mercedes-Benz. Customer: I have a question about the warranty on my GLC. Agent: I can help you with that. Can you please provide your vehicle's VIN number? Customer: It's [VIN number]. Agent: Thank you. Let me look up your warranty information. [After looking up information] Your vehicle is covered under the standard warranty until [date] or [mileage]. What specifically was your question about the warranty? Customer: I wanted to know if [issue] is covered. Agent: Based on your warranty, [issue] is/is not covered. Would you like to schedule a service appointment to have it looked at? Customer: Yes, please."
    ]

    # Create calls, linking agents and customers
    for transcript in sample_transcripts:
        # Ensure we have enough agents and customers
        if agents and customers:
            agent = random.choice(agents)
            customer = random.choice(customers)

            # Prepare the payload for the API call
            payload = {
                "customer_id": customer.id,
                "agent_id": agent.id,
                "transcript": transcript
            }

            # Fetch call data from the API
            try:
                response = requests.post("http://localhost:8000/calls/", json=payload)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                call_data = response.json()

                # The API returns a Call object, so we don't need to create it manually
                # call = Call(
                #     customer_id=customer.id,
                #     agent_id=agent.id,
                #     transcript=call_data["transcript"],
                #     call_date=datetime.now(UTC),
                #     agent_performance_score=call_data["agent_performance_score"],
                #     customer_interest_score=call_data["customer_interest_score"],
                #     test_drive_readiness=call_data["test_drive_readiness"],
                #     analysis_results=call_data["analysis_results"]
                # )
                call_data["call_date"] = datetime.now(UTC)
                # Ensure call_date is a datetime object
                call_data["call_date"] = datetime.fromisoformat(str(call_data["call_date"]))
                call = Call(**call_data)
                calls.append(call)
                db.add(call)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching call data from API: {e}")
                raise  # Re-raise the exception to stop data generation

    db.commit()

    print(f"Created {len(agents)} agents, {len(customers)} customers, and {len(calls)} calls.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_data(db)
    finally:
        db.close()