from app.data.kenyan_locations import KENYA_LOCATIONS, get_all_counties, get_constituencies_for_county, get_wards_for_constituency

# Export the functions for easy access
__all__ = ['KENYA_LOCATIONS', 'get_all_counties', 'get_constituencies_for_county', 'get_wards_for_constituency']

# For backward compatibility
LOCATIONS = KENYA_LOCATIONS

if __name__ == "__main__":
    print(f"✅ Kenyan location data loaded successfully")
    print(f"   Total counties: {len(get_all_counties())}")
    print(f"   Sample: {get_all_counties()[:3]}")
