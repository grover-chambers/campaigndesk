from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.extensions import db
from app.models import Campaign, Member, Event, Bulletin
from app.data.party_colors import get_party_colors, hex_to_rgb
from datetime import datetime, timezone

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def landing():
    return render_template('public/landing.html')

@public_bp.route('/find-campaign')
def find_campaign():
    q = request.args.get('q', '').strip().lower()
    if len(q) < 2:
        return jsonify([])
    results = Campaign.query.filter(
        Campaign.is_active == True,
        db.or_(
            Campaign.candidate_name.ilike(f'%{q}%'),
            Campaign.constituency.ilike(f'%{q}%'),
        )
    ).limit(6).all()
    return jsonify([{
        'slug': c.slug,
        'candidate': c.candidate_name,
        'constituency': c.constituency,
        'party': c.party,
        'seat_level': c.seat_level,
    } for c in results])

@public_bp.route('/c/<slug>/hub')
def campaign_hub(slug):
    campaign = Campaign.query.filter_by(slug=slug, is_active=True).first_or_404()
    member_count = Member.query.filter_by(campaign_id=campaign.id, is_active=True).count()
    event_count = Event.query.filter_by(campaign_id=campaign.id).count()
    bulletin_count = Bulletin.query.filter_by(campaign_id=campaign.id, is_public=True).count()
    bulletins = Bulletin.query.filter_by(campaign_id=campaign.id, is_public=True)\
                       .order_by(Bulletin.published_at.desc()).limit(10).all()
    
    # Get official party colors
    party_color = get_party_colors(campaign.party)
    rgb = hex_to_rgb(party_color['primary'])
    party_color['primary_rgb'] = f"{rgb[0]}, {rgb[1]}, {rgb[2]}"
    
    return render_template('public/campaign_hub.html',
                         campaign=campaign,
                         party_color=party_color,
                         member_count=member_count,
                         event_count=event_count,
                         bulletin_count=bulletin_count,
                         bulletins=bulletins)

@public_bp.route('/c/<slug>/login')
def candidate_login(slug):
    return campaign_hub(slug)

@public_bp.route('/c/<slug>/board')
def noticeboard(slug):
    return campaign_hub(slug)

# Location API endpoints using local data
@public_bp.route('/api/counties')
def api_counties():
    from app.data.location_loader import get_all_counties
    counties = get_all_counties()
    return jsonify(counties)

@public_bp.route('/api/constituencies')
def api_constituencies():
    from app.data.location_loader import get_constituencies_for_county
    county = request.args.get('county', '')
    if county:
        constituencies = get_constituencies_for_county(county)
        return jsonify(constituencies)
    return jsonify([])

@public_bp.route('/api/wards')
def api_wards():
    from app.data.location_loader import get_wards_for_constituency
    county = request.args.get('county', '')
    constituency = request.args.get('constituency', '')
    if county and constituency:
        wards = get_wards_for_constituency(county, constituency)
        return jsonify(wards)
    return jsonify([])

# Member login API - this is the endpoint the campaign hub calls
@public_bp.route('/api/member/login', methods=['POST'])
def member_login():
    data = request.json
    campaign_slug = data.get('campaign_slug')
    phone = data.get('phone')
    access_code = data.get('access_code')
    
    print(f"Login attempt for campaign: {campaign_slug}, phone: {phone}")
    
    campaign = Campaign.query.filter_by(slug=campaign_slug).first()
    if not campaign:
        print(f"Campaign not found: {campaign_slug}")
        return jsonify({'success': False, 'error': 'Campaign not found'}), 404
    
    member = Member.query.filter_by(
        campaign_id=campaign.id,
        phone=phone,
        access_code=access_code,
        is_active=True
    ).first()
    
    if member:
        member.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Store in session
        session['member_id'] = member.id
        session['member_name'] = member.name
        session['member_role'] = member.role
        session['campaign_slug'] = campaign_slug
        
        print(f"Login successful: {member.name} ({member.role})")
        return jsonify({
            'success': True,
            'name': member.name,
            'role': member.role,
            'redirect': '/dashboard/member'
        })
    
    print(f"Login failed: Invalid credentials for {phone}")
    return jsonify({'success': False, 'error': 'Invalid phone or access code'}), 401

@public_bp.route('/api/locations')
def locations_api():
    """Return full county->constituency->ward tree"""
    import json, os
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'kenyan_locations_clean.json')
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)

@public_bp.route('/api/locations/constituencies/<county>')
def constituencies_api(county):
    import json, os
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'kenyan_locations_clean.json')
    with open(path) as f:
        data = json.load(f)
    county_data = data.get(county, {})
    return jsonify(list(county_data.keys()))

@public_bp.route('/api/locations/wards/<county>/<constituency>')
def wards_api(county, constituency):
    import json, os
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'kenyan_locations_clean.json')
    with open(path) as f:
        data = json.load(f)
    wards = data.get(county, {}).get(constituency, [])
    return jsonify(wards)

@public_bp.route('/api/iebc-codes')
def iebc_codes_api():
    import json, os
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'iebc_codes.json')
    with open(path) as f:
        data = json.load(f)
    return jsonify(data)
