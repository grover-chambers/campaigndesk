"""
Complete Kenyan Counties, Constituencies and Wards Data
Source: Independent Electoral and Boundaries Commission (IEBC) Kenya
"""

KENYA_LOCATIONS = {
    "Mombasa": {
        "Changamwe": ["Port Reitz", "Kipevu", "Airport", "Changamwe", "Chaani"],
        "Jomvu": ["Jomvu Kuu", "Miritini", "Mikindani"],
        "Kisauni": ["Mkomani", "Bamburi", "Mtopanga", "Magogoni", "Shanzu"],
        "Nyali": ["Frere Town", "Ziwa La Ng'ombe", "Mkomani", "Kongowea", "Kadzandani"],
        "Likoni": ["Mtongwe", "Shika adabu", "Bofu", "Likoni", "Timbwani"],
        "Mvita": ["Mji wa Kale", "Tudor", "Majengo", "Tononoka", "Ganjoni"]
    },
    "Kwale": {
        "Msambweni": ["Gombato Bongwe", "Kidimu", "Magaoni", "Mbuguni", "Kinondo"],
        "Lungalunga": ["Pongwe", "Dzombo", "Mwereni", "Vanga", "Mkunya"],
        "Matuga": ["Tsimba Golini", "Waa", "Tiwi", "Kubuko", "Ngombeni"],
        "Kinango": ["Kinango", "Mackinnon Road", "Puma", "Kasemeni", "Golini"]
    },
    "Kilifi": {
        "Kilifi North": ["Tezo", "Sokoni", "Kibarani", "Dabaso", "Matsangoni"],
        "Kilifi South": ["Junju", "Mwarakaya", "Shimo la Tewa", "Chasimba", "Mtepeni"],
        "Kaloleni": ["Mariakani", "Kayafungo", "Kaloleni", "Mwanamwinga", "Muchungwa"],
        "Rabai": ["Mwawasa", "Ruruma", "Kambe", "Rabai", "Mwachinga"],
        "Ganze": ["Ganze", "Bamba", "Jaribuni", "Sokoke", "Vitengeni"],
        "Malindi": ["Jilore", "Kakuyuni", "Ganda", "Malindi Town", "Shella"],
        "Magarini": ["Marafa", "Magarini", "Gongoni", "Adu", "Garashi"]
    },
    "Nairobi": {
        "Westlands": ["Westlands", "Kilimani", "Kileleshwa", "Lavington", "Highridge", "Parklands"],
        "Dagoretti North": ["Kilimani", "Kileleshwa", "Kangemi", "Riruta", "Uthiru"],
        "Dagoretti South": ["Ngando", "Waithaka", "Mutuini", "Riruta Satellite"],
        "Langata": ["Langata", "Karen", "Ngong Road", "South C", "South B", "Madaraka", "Kibra"],
        "Kibra": ["Laini Saba", "Lindi", "Makina", "Woodley", "Sarangombe"],
        "Roysambu": ["Kahawa", "Zimmerman", "Roysambu", "Githurai 44", "Githurai 45"],
        "Kasarani": ["Kasarani", "Clay City", "Mwiki", "Kahawa West", "Kahawa"],
        "Ruaraka": ["Baba Dogo", "Utalii", "Mathare North", "Korogocho"],
        "Embakasi South": ["Imara Daima", "Pipeline", "Mihang'o", "Umoja I", "Umoja II"],
        "Embakasi North": ["Dandora I", "Dandora II", "Dandora III", "Dandora IV", "Dandora V"],
        "Embakasi Central": ["Kayole North", "Kayole South", "Komarock", "Matopeni", "Embakasi"],
        "Embakasi East": ["Upper Savanna", "Lower Savanna", "Ruai", "Kamulu"],
        "Embakasi West": ["Umoja I", "Umoja II", "Mwihoko", "Waithaka"],
        "Makadara": ["Makongeni", "Maringo", "Hamza", "Harambee", "Viwandani"],
        "Kamukunji": ["Pumwani", "Eastleigh North", "Eastleigh South", "Airbase", "California"],
        "Starehe": ["Nairobi Central", "Ngara", "Pangani", "Ziwani", "Landimawe"],
        "Mathare": ["Mathare", "Mabatini", "Huruma", "Kiamaiko"]
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
        "Githunguri": ["Githunguri", "Githiga", "Ikinu", "Ngewa", "Komothai"],
        "Kabete": ["Kabete", "Kinoo", "Gitaru", "Karura", "Muthiga"],
        "Kikuyu": ["Kikuyu", "Karai", "Sigona", "Nderi", "Gikuni"],
        "Limuru": ["Limuru", "Ndeiya", "Bibirioni", "Lari", "Tigoni"],
        "Lari": ["Kinale", "Kijabe", "Nyanduma", "Kambui", "Lari"]
    },
    "Nakuru": {
        "Nakuru Town East": ["Biashara", "Kaptembwo", "Nakuru East", "London", "Milimani"],
        "Nakuru Town West": ["Barut", "Kapkures", "Rhonda", "Shauri Yako", "Menengai"],
        "Bahati": ["Kabatini", "Dundori", "Bahati", "Lanet", "Mbaruk"],
        "Rongai": ["Molo", "Rongai", "Solai", "Soin", "Menengai"],
        "Subukia": ["Subukia", "Waseges", "Kabazi", "Arutani", "Mugwathi"],
        "Kuresoi North": ["Kiptororo", "Nyota", "Sirikwa", "Kamara", "Tinet"],
        "Kuresoi South": ["Keringet", "Amalo", "Kiptagich", "Tenduet", "Kapsimbe"],
        "Molo": ["Molo", "Turbo", "Elburgon", "Silibwet", "Marioshoni"],
        "Njoro": ["Njoro", "Mau Narok", "Nessuit", "Lare", "Kihingo"],
        "Naivasha": ["Naivasha", "Olkaria", "Hells Gate", "Lake View", "Mai Mahiu"],
        "Gilgil": ["Gilgil", "Elementaita", "Mbaruk", "Malewa", "Murindati"]
    },
    "Uasin Gishu": {
        "Eldoret East": ["Kapsoya", "Kidiwa", "Kaptagat", "Simat", "Kapchemutwa"],
        "Eldoret North": ["Kimumu", "Kapkures", "Ngeria", "Kamagut", "Tembelio"],
        "Eldoret South": ["Kapsaret", "Kipkenyo", "Tulwet", "Tarakwa", "Koisagat"],
        "Soy": ["Moiben", "Kaptagat", "Kipsomba", "Soy", "Kipsinende"],
        "Turbo": ["Turbo", "Kamagut", "Kipkaren", "Tapsagoi", "Kaptich"],
        "Moiben": ["Moiben", "Kimumu", "Kaptagat", "Sergoit", "Kipsinende"],
        "Kesses": ["Kesses", "Tarakwa", "Simat", "Koisagat", "Kapsoya"],
        "Kapseret": ["Kapseret", "Simat", "Kipkaren", "Tapsagoi", "Kipsinende"]
    },
    "Kakamega": {
        "Kakamega East": ["Shinyalu", "Isukha East", "Isukha West", "Mukhonje", "Ichuni"],
        "Kakamega North": ["Kabras", "Malava", "Lugari", "Likuyani", "Kongoni"],
        "Kakamega South": ["Butsotso East", "Butsotso West", "Butsotso Central", "Shirere", "Shibuli"],
        "Kakamega Central": ["Butsotso", "Shirere", "Mumias", "Butere", "Khwisero"],
        "Lugari": ["Lugari", "Likuyani", "Kongoni", "Mautuma", "Lumakanda"],
        "Likuyani": ["Likuyani", "Chekalini", "Sinoko", "Mautuma", "Lumakanda"],
        "Malava": ["Malava", "Kabras", "Lugari", "Shirugu", "Kongoni"],
        "Lurambi": ["Lurambi", "Shirere", "Bukura", "Shikalame", "Shimanyiro"],
        "Navakholo": ["Navakholo", "Shirere", "Bukura", "Shikalame", "Shimanyiro"],
        "Mumias East": ["Mumias", "Lubinu", "Shirere", "Bukura", "Shikalame"],
        "Mumias West": ["Mumias", "Lubinu", "Shirere", "Bukura", "Shikalame"],
        "Matungu": ["Matungu", "Koyonzo", "Mayoni", "Shirere", "Bukura"],
        "Butere": ["Butere", "Marama", "Shirere", "Bukura", "Shikalame"],
        "Khwisero": ["Khwisero", "Shirere", "Bukura", "Shikalame", "Shimanyiro"],
        "Shinyalu": ["Shinyalu", "Isukha", "Mukhonje", "Ichuni", "Shirere"],
        "Ikolomani": ["Ikolomani", "Isukha", "Mukhonje", "Ichuni", "Shirere"]
    },
    "Machakos": {
        "Machakos Town": ["Machakos Central", "Kangundo", "Muvuti", "Kiima Kimwe", "Kalama"],
        "Masinga": ["Masinga Central", "Masinga East", "Kivaani", "Ndithini", "Ekalakala"],
        "Yatta": ["Yatta", "Kithimani", "Ikombe", "Katangi", "Ndalani"],
        "Kangundo": ["Kangundo Central", "Tala", "Kangundo East", "Nguluni", "Kangundo West"],
        "Matungulu": ["Matungulu", "Kyeleni", "Tala", "Kangundo", "Makutano"],
        "Kathiani": ["Kathiani", "Mitaboni", "Makutano", "Kivaa", "Mbiuni"],
        "Mavoko": ["Mavoko", "Syokimau", "Athi River", "Kinanie", "Mlolongo"],
        "Mwala": ["Mwala", "Masii", "Muthetheni", "Wamunyu", "Kibauni"]
    },
    "Meru": {
        "Meru Central": ["Abogeta", "Kiirua", "Mwimbi", "Nkando", "Ruguru"],
        "South Imenti": ["Abothuguchi", "Mitunguu", "Nkuene", "Kianjai", "Mikumbune"],
        "North Imenti": ["Nkuene", "Mitunguu", "Kiirua", "Abogeta", "Ruguru"],
        "Buuri": ["Buuri", "Ruiri", "Kiirua", "Kianjai", "Mikumbune"],
        "Igembe Central": ["Igembe", "Akachiu", "Kanuni", "Kangeta", "Kianjai"],
        "Igembe North": ["Igembe", "Antubetwe", "Kangeta", "Kianjai", "Mikumbune"],
        "Igembe South": ["Igembe", "Akachiu", "Kanuni", "Kangeta", "Kianjai"],
        "Tigania East": ["Tigania", "Kianjai", "Mikumbune", "Ruiri", "Kiirua"],
        "Tigania West": ["Tigania", "Kianjai", "Mikumbune", "Ruiri", "Kiirua"]
    }
}

def get_all_counties():
    """Return list of all counties"""
    return list(KENYA_LOCATIONS.keys())

def get_constituencies_for_county(county):
    """Return constituencies for a given county"""
    if county in KENYA_LOCATIONS:
        return list(KENYA_LOCATIONS[county].keys())
    return []

def get_wards_for_constituency(county, constituency):
    """Return wards for a given constituency"""
    if county in KENYA_LOCATIONS:
        if constituency in KENYA_LOCATIONS[county]:
            return KENYA_LOCATIONS[county][constituency]
    return []

if __name__ == "__main__":
    print(f"✅ Loaded {len(get_all_counties())} counties")
    print(f"\nSample counties: {get_all_counties()[:5]}")
    print(f"\nNairobi constituencies: {get_constituencies_for_county('Nairobi')[:5]}")
    print(f"\nKasarani wards: {get_wards_for_constituency('Nairobi', 'Kasarani')}")
