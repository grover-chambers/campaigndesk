import json
from pathlib import Path

class LocationLoader:
    """Load Kenyan location data from local JSON files"""
    
    def __init__(self):
        self.counties = []  # List of county names
        self.data = {}  # county -> {constituency: [wards]}
        self.load_data()
    
    def load_data(self):
        """Load location data from JSON file"""
        # Try multiple possible file paths
        possible_paths = [
            Path(__file__).parent / 'kenyan_locations_clean.json',
            Path(__file__).parent / 'kenyan_locations_raw.json',
            Path(__file__).parent / 'api_response_sample.json',
        ]
        
        for data_path in possible_paths:
            if data_path.exists():
                print(f"📂 Loading from {data_path.name}")
                with open(data_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    self.process_data(raw_data)
                    return
        
        # If no file exists, create default data
        print("⚠️ No data file found, creating default data...")
        self.create_default_data()
    
    def process_data(self, raw_data):
        """Process raw API data into clean structure"""
        self.data = {}
        
        for county_name, constituencies in raw_data.items():
            # Skip if it's not a string (avoid numbers)
            if not isinstance(county_name, str):
                continue
            
            # Clean county name
            county_name = county_name.strip()
            
            self.data[county_name] = {}
            
            if isinstance(constituencies, dict):
                for const_name, wards in constituencies.items():
                    if isinstance(const_name, str):
                        self.data[county_name][const_name] = wards if isinstance(wards, list) else []
            elif isinstance(constituencies, list):
                # Handle case where constituencies is a list
                for const_item in constituencies:
                    if isinstance(const_item, dict):
                        for const_name, wards in const_item.items():
                            self.data[county_name][const_name] = wards if isinstance(wards, list) else []
        
        self.counties = sorted(list(self.data.keys()))
        print(f"✅ Loaded {len(self.counties)} counties")
        if self.counties:
            print(f"   Sample counties: {self.counties[:5]}")
    
    def create_default_data(self):
        """Create default data for major counties"""
        self.data = {
            "Nairobi": {
                "Westlands": ["Westlands", "Kilimani", "Kileleshwa", "Lavington", "Highridge", "Parklands"],
                "Kasarani": ["Kasarani", "Clay City", "Mwiki", "Kahawa West", "Kahawa", "Zimmerman"],
                "Langata": ["Langata", "Karen", "Ngong Road", "South C", "South B", "Madaraka"],
                "Embakasi Central": ["Kayole North", "Kayole South", "Komarock", "Matopeni", "Embakasi"],
                "Roysambu": ["Kahawa", "Zimmerman", "Roysambu", "Githurai 44", "Githurai 45"],
                "Dagoretti North": ["Kilimani", "Kileleshwa", "Kangemi", "Riruta", "Uthiru"],
                "Dagoretti South": ["Ngando", "Waithaka", "Mutuini", "Riruta Satellite"],
                "Kibra": ["Laini Saba", "Lindi", "Makina", "Woodley", "Sarangombe"],
                "Ruaraka": ["Baba Dogo", "Utalii", "Mathare North", "Korogocho"],
                "Embakasi South": ["Imara Daima", "Pipeline", "Mihang'o", "Umoja I", "Umoja II"],
                "Embakasi North": ["Dandora I", "Dandora II", "Dandora III", "Dandora IV", "Dandora V"],
                "Embakasi East": ["Upper Savanna", "Lower Savanna", "Ruai", "Kamulu"],
                "Embakasi West": ["Umoja I", "Umoja II", "Mwihoko", "Waithaka"],
                "Makadara": ["Makongeni", "Maringo", "Hamza", "Harambee", "Viwandani"],
                "Kamukunji": ["Pumwani", "Eastleigh North", "Eastleigh South", "Airbase", "California"],
                "Starehe": ["Nairobi Central", "Ngara", "Pangani", "Ziwani", "Landimawe"],
                "Mathare": ["Mathare", "Mabatini", "Huruma", "Kiamaiko"]
            },
            "Mombasa": {
                "Changamwe": ["Port Reitz", "Kipevu", "Airport", "Changamwe", "Chaani"],
                "Jomvu": ["Jomvu Kuu", "Miritini", "Mikindani"],
                "Kisauni": ["Mkomani", "Bamburi", "Mtopanga", "Magogoni", "Shanzu"],
                "Nyali": ["Frere Town", "Ziwa La Ng'ombe", "Mkomani", "Kongowea", "Kadzandani"],
                "Likoni": ["Mtongwe", "Shika adabu", "Bofu", "Likoni", "Timbwani"],
                "Mvita": ["Mji wa Kale", "Tudor", "Majengo", "Tononoka", "Ganjoni"]
            },
            "Kisumu": {
                "Kisumu East": ["Kondele", "Manyatta", "Migosi", "Kolwa", "Kajulu"],
                "Kisumu West": ["Riat", "Maseno", "Kombewa", "Kibos", "Koru"],
                "Kisumu Central": ["Railways", "Migosi", "Shaurimoyo", "Market", "Nyalenda"],
                "Seme": ["East Seme", "Central Seme", "West Seme", "Kombewa", "Kadenge"],
                "Nyando": ["Ahero", "Miwani", "Koguta", "Rogo", "Kakola"],
                "Muhoroni": ["Chemelil", "Muhoroni", "Koru", "Ombeyi", "Kipsamoite"],
                "Nyakach": ["North Nyakach", "South Nyakach", "West Nyakach", "Central Nyakach", "East Nyakach"]
            },
            "Kiambu": {
                "Kiambaa": ["Tetu", "Ndenderu", "Muchatha", "Kihara", "Githurai"],
                "Kiambu Town": ["Kiambu", "Tinganga", "Riabai", "Karuri", "Gatunguru"],
                "Gatundu South": ["Kiamwangi", "Ndarugu", "Ngenda", "Gituamba", "Kiganjo"],
                "Gatundu North": ["Githobokoni", "Chania", "Karuri", "Mang'u", "Gituamba"],
                "Juja": ["Murera", "Theta", "Juja", "Witeithie", "Kalimoni"],
                "Thika Town": ["Township", "Kamenu", "Hospital", "Ngoingwa", "Gatuanyaga"],
                "Ruiru": ["Gitothua", "Kahawa Wendani", "Kahawa Sukari", "Mwiki", "Ruiru"],
                "Kabete": ["Kabete", "Kinoo", "Gitaru", "Karura", "Muthiga"],
                "Kikuyu": ["Kikuyu", "Karai", "Sigona", "Nderi", "Gikuni"]
            }
        }
        self.counties = sorted(list(self.data.keys()))
        print(f"✅ Created default data with {len(self.counties)} counties")
        print(f"   Counties: {self.counties}")
    
    def get_all_counties(self):
        """Return list of all county names"""
        return self.counties
    
    def get_constituencies(self, county):
        """Return constituencies for a given county"""
        if county in self.data:
            return list(self.data[county].keys())
        return []
    
    def get_wards(self, county, constituency):
        """Return wards for a given constituency"""
        if county in self.data:
            if constituency in self.data[county]:
                return self.data[county][constituency]
        return []
    
    def search_county(self, query):
        """Search for counties by name"""
        query_lower = query.lower()
        return [c for c in self.counties if query_lower in c.lower()]

# Create a singleton instance
location_loader = LocationLoader()

# Export convenience functions
def get_all_counties():
    return location_loader.get_all_counties()

def get_constituencies_for_county(county):
    return location_loader.get_constituencies(county)

def get_wards_for_constituency(county, constituency):
    return location_loader.get_wards(county, constituency)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Testing Location Loader")
    print("="*50)
    
    counties = get_all_counties()
    print(f"\n📊 Total counties: {len(counties)}")
    print(f"All counties: {counties}")
    
    if counties:
        test_county = counties[0]
        print(f"\n📍 Testing county: {test_county}")
        
        constituencies = get_constituencies_for_county(test_county)
        print(f"Constituencies ({len(constituencies)}): {constituencies[:5]}")
        
        if constituencies:
            test_const = constituencies[0]
            wards = get_wards_for_constituency(test_county, test_const)
            print(f"Wards in {test_const}: {wards[:5]}")
    
    print("\n✅ Location loader is ready!")
