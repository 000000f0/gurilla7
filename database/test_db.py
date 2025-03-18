from db_manager import DatabaseManager
import json
from pprint import pprint

def test_database():
    # Initialize database with test client
    db = DatabaseManager("test_client")
    
    print("1. Testing Client Management")
    print("-" * 50)
    campaign_params = {
        "iteration_count": 3,
        "search_depth": 2,
        "lead_quantity": 10
    }
    
    success = db.create_client(
        telegram_handle="@test_user",
        email="test@example.com",
        industry="Technology",
        location="Silicon Valley",
        campaign_parameters=campaign_params
    )
    print(f"Client created: {success}")
    
    client = db.get_client("@test_user")
    print(f"Client data: {json.dumps(client, indent=2)}\n")
    
    print("2. Testing Industry Data")
    print("-" * 50)
    # Add multiple industry data entries
    industries = [
        {
            "source": "https://example.com/tech-trends-1",
            "content": "AI and automation are key trends in 2025",
            "pain_points": "Difficulty in finding skilled AI developers"
        },
        {
            "source": "https://example.com/tech-trends-2",
            "content": "Cloud computing adoption accelerates",
            "pain_points": "Security concerns in cloud migration"
        }
    ]
    
    for ind in industries:
        industry_id = db.add_industry_data(**ind)
        print(f"Industry data added with ID: {industry_id}")
    
    print("\nSearching industry data for 'AI':")
    ai_results = db.search_industry_data("AI")
    pprint(ai_results)
    
    print("\n3. Testing Lead Management")
    print("-" * 50)
    # Add multiple leads
    leads = [
        {
            "company_name": "Tech Corp",
            "website": "https://techcorp.com",
            "contact_info": "contact@techcorp.com",
            "details": "Growing tech company"
        },
        {
            "company_name": "Cloud Solutions Inc",
            "website": "https://cloudsolutions.com",
            "contact_info": "info@cloudsolutions.com",
            "details": "Cloud security provider"
        }
    ]
    
    lead_ids = []
    for lead in leads:
        lead_id = db.add_lead(**lead)
        lead_ids.append(lead_id)
        print(f"Lead added with ID: {lead_id}")
    
    # Update a lead
    update_success = db.update_lead(lead_ids[0], {
        "contact_info": "new.contact@techcorp.com",
        "details": "Updated company details"
    })
    print(f"Lead update success: {update_success}")
    
    print("\n4. Testing Solutions Management")
    print("-" * 50)
    # Add solutions for leads
    for lead_id in lead_ids:
        solution_id = db.add_solution(
            lead_id=lead_id,
            solution_text=f"Custom solution for lead {lead_id}"
        )
        print(f"Solution added for lead {lead_id} with ID: {solution_id}")
        
        # Update solution status
        status_update = db.update_solution_status(solution_id, "reviewed")
        print(f"Solution {solution_id} status update: {status_update}")
    
    print("\n5. Testing Outreach Management")
    print("-" * 50)
    # Log outreach attempts
    for lead_id in lead_ids:
        outreach_id = db.log_outreach(
            lead_id=lead_id,
            message_sent=f"Initial contact message for lead {lead_id}"
        )
        print(f"Outreach logged for lead {lead_id} with ID: {outreach_id}")
        
        # Update some with responses
        if lead_id == lead_ids[0]:
            response_updated = db.update_outreach_response(
                outreach_id=outreach_id,
                response="Interested in learning more"
            )
            print(f"Outreach response updated: {response_updated}")
    
    print("\nPending responses:")
    pending = db.get_pending_responses()
    pprint(pending)
    
    print("\n6. Testing Analytics")
    print("-" * 50)
    print("\nCampaign Stats:")
    stats = db.get_campaign_stats()
    pprint(stats)
    
    print("\nFull Campaign Export:")
    campaign_data = db.export_campaign_data()
    print(f"Export successful: {bool(campaign_data)}")
    print(f"Number of leads exported: {len(campaign_data['leads'])}")
    print(f"Number of solutions exported: {len(campaign_data['solutions'])}")

if __name__ == "__main__":
    test_database()
