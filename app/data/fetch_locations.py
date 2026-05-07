import json
import requests
from pathlib import Path

# API endpoint
API_URL = "https://kenyaareadata.vercel.app/api/areas"
API_KEY = "keyPub1569gsvndc123kg9sjhg"

def fetch_all_locations():
    """Fetch all counties, constituencies, and wards from the API"""
    try:
        # Fetch all data
        response = requests.get(f"{API_URL}?apiKey={API_KEY}")
        response.raise_for_status()
        data = response.json()
        
        # Structure the data
        locations = {}
        
        for county, constituencies in data.items():
            locations[county] = {
                'constituencies': {}
            }
            
            for constituency, wards in constituencies.items():
                locations[county]['constituencies'][constituency] = wards
        
        # Save to JSON file
        output_path = Path(__file__).parent / 'kenyan_locations.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(locations, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Data saved to {output_path}")
        print(f"📊 Total counties: {len(locations)}")
        
        total_constituencies = sum(len(v['constituencies']) for v in locations.values())
        total_wards = sum(
            len(wards) 
            for county_data in locations.values() 
            for wards in county_data['constituencies'].values()
        )
        print(f"📊 Total constituencies: {total_constituencies}")
        print(f"📊 Total wards: {total_wards}")
        
        return locations
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def load_locations():
    """Load locations from JSON file"""
    json_path = Path(__file__).parent / 'kenyan_locations.json'
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

if __name__ == '__main__':
    fetch_all_locations()
