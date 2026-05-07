"""
Official Party Colors from Kenya's Registrar of Political Parties
Source: ORPP Kenya - https://www.orpp.or.ke/
"""

PARTY_COLORS = {
    # Major parties with official colors
    'ODM': {
        'primary': '#FF6600',  # ODM Orange
        'secondary': '#006633',  # ODM Green
        'name': 'Orange Democratic Movement',
        'logo': 'odm.png'
    },
    'UDA': {
        'primary': '#F5A623',  # UDA Yellow/Orange
        'secondary': '#000000',  # Black
        'name': 'United Democratic Alliance',
        'logo': 'uda.png'
    },
    'JUBILEE': {
        'primary': '#D71920',  # Jubilee Red
        'secondary': '#FBB03B',  # Gold/Yellow
        'name': 'Jubilee Party',
        'logo': 'jubilee.png'
    },
    'ANC': {
        'primary': '#00A651',  # ANC Green
        'secondary': '#FFFFFF',  # White
        'name': 'Amani National Congress',
        'logo': 'anc.png'
    },
    'WIPER': {
        'primary': '#8B0000',  # Dark Red
        'secondary': '#FFD700',  # Gold
        'name': 'Wiper Democratic Movement',
        'logo': 'wiper.png'
    },
    'KANU': {
        'primary': '#000000',  # Black
        'secondary': '#FF0000',  # Red
        'name': 'Kenya African National Union',
        'logo': 'kanu.png'
    },
    'FORD-K': {
        'primary': '#0066CC',  # Blue
        'secondary': '#FFFFFF',  # White
        'name': 'Forum for the Restoration of Democracy - Kenya',
        'logo': 'fordk.png'
    },
    'FORD-A': {
        'primary': '#FF6600',  # Orange
        'secondary': '#FFFFFF',  # White
        'name': 'Ford-Asili',
        'logo': 'forda.png'
    },
    'CCM': {
        'primary': '#003399',  # Navy Blue
        'secondary': '#FFCC00',  # Yellow
        'name': 'Chama Cha Uzalendo',
        'logo': 'ccm.png'
    },
    'NARC-K': {
        'primary': '#009900',  # Green
        'secondary': '#FFFFFF',  # White
        'name': 'National Rainbow Coalition - Kenya',
        'logo': 'narck.png'
    },
    'NARC': {
        'primary': '#FF0000',  # Red
        'secondary': '#000000',  # Black
        'name': 'National Rainbow Coalition',
        'logo': 'narc.png'
    },
    'PNU': {
        'primary': '#004080',  # Dark Blue
        'secondary': '#FFD700',  # Gold
        'name': 'Party of National Unity',
        'logo': 'pnu.png'
    },
    'UDP': {
        'primary': '#800080',  # Purple
        'secondary': '#FFFFFF',  # White
        'name': 'United Democratic Party',
        'logo': 'udp.png'
    },
    'MDG': {
        'primary': '#008080',  # Teal
        'secondary': '#FFD700',  # Gold
        'name': 'Maendeleo Chap Chap Party',
        'logo': 'mdg.png'
    },
    'CCU': {
        'primary': '#800000',  # Maroon
        'secondary': '#C0C0C0',  # Silver
        'name': 'Chama Cha Uzalendo',
        'logo': 'ccu.png'
    },
    'DP': {
        'primary': '#2E8B57',  # Sea Green
        'secondary': '#FFFFFF',  # White
        'name': 'Democratic Party',
        'logo': 'dp.png'
    },
    'KUP': {
        'primary': '#FF8C00',  # Dark Orange
        'secondary': '#FFFFFF',  # White
        'name': 'Kenya Union Party',
        'logo': 'kup.png'
    },
    'TSP': {
        'primary': '#1E90FF',  # Dodger Blue
        'secondary': '#FFFFFF',  # White
        'name': 'The Service Party',
        'logo': 'tsp.png'
    },
    'UPIA': {
        'primary': '#9400D3',  # Dark Violet
        'secondary': '#FFFFFF',  # White
        'name': 'United Party of Independent Alliance',
        'logo': 'upia.png'
    },
    
    # Default for independent or unknown parties
    'INDEPENDENT': {
        'primary': '#4A5568',  # Slate Gray
        'secondary': '#718096',  # Light Slate
        'name': 'Independent Candidate',
        'logo': 'independent.png'
    },
    'OTHER': {
        'primary': '#6B7280',  # Gray
        'secondary': '#9CA3AF',  # Light Gray
        'name': 'Other Party',
        'logo': 'other.png'
    }
}

def get_party_colors(party_name):
    """Get official party colors by name"""
    if not party_name:
        return PARTY_COLORS['OTHER']
    
    # Normalize the party name
    normalized = party_name.upper().strip()
    
    # Try direct match
    if normalized in PARTY_COLORS:
        return PARTY_COLORS[normalized]
    
    # Try partial matches for common variations
    for key, colors in PARTY_COLORS.items():
        if key in normalized or normalized in key:
            return colors
    
    # Check common variations
    variations = {
        'ODM': ['ODM', 'ORANGE DEMOCRATIC MOVEMENT', 'ORANGE'],
        'UDA': ['UDA', 'UNITED DEMOCRATIC ALLIANCE'],
        'JUBILEE': ['JUBILEE', 'JUBILEE PARTY', 'JUB'],
        'ANC': ['ANC', 'AMANI NATIONAL CONGRESS', 'AMANI'],
        'WIPER': ['WIPER', 'WIPER DEMOCRATIC MOVEMENT'],
        'KANU': ['KANU', 'KENYA AFRICAN NATIONAL UNION'],
    }
    
    for standard, variants in variations.items():
        if normalized in variants or any(variant in normalized for variant in variants):
            return PARTY_COLORS[standard]
    
    return PARTY_COLORS['OTHER']

def get_all_parties():
    """Get list of all registered parties"""
    return [{
        'code': code,
        'name': colors['name'],
        'primary': colors['primary'],
        'secondary': colors['secondary']
    } for code, colors in PARTY_COLORS.items() if code not in ['INDEPENDENT', 'OTHER']]

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

if __name__ == "__main__":
    # Test ODM colors
    odm = get_party_colors('ODM')
    print(f"ODM Colors: Primary={odm['primary']}, Secondary={odm['secondary']}")
    print(f"RGB: {hex_to_rgb(odm['primary'])}")
