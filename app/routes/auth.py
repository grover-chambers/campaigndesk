from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from app.extensions import db
from app.models import Campaign, Member
import uuid
import random
import json
import traceback
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/signup')
def signup():
    return render_template('auth/signup.html')

@auth_bp.route('/auth/signup/submit', methods=['POST'])
def signup_submit():
    print("\n" + "="*50)
    print("SIGNUP SUBMIT - Processing form")
    print(f"Form data: {dict(request.form)}")
    print("="*50)
    
    try:
        seat_level = request.form.get('seat_level')
        candidate_name = request.form.get('candidate_name')
        party = request.form.get('party')
        constituency = request.form.get('constituency')
        county = request.form.get('county')
        ward = request.form.get('ward', '')
        slogan = request.form.get('slogan', '')
        bio = request.form.get('bio', '')
        manager_name = request.form.get('manager_name')
        manager_phone = request.form.get('manager_phone')
        
        if not all([seat_level, candidate_name, party, county, manager_name, manager_phone]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if seat_level in ['mca', 'mp'] and not constituency:
            return jsonify({'error': 'Constituency is required'}), 400
        
        if seat_level == 'mca' and not ward:
            return jsonify({'error': 'Ward is required for MCA'}), 400
        
        # Generate slug
        slug_base = candidate_name.lower().replace(' ', '-').replace("'", "").replace(".", "")
        slug = f"{slug_base}-{uuid.uuid4().hex[:4]}"
        
        # Party colors
        party_colors = {
            'ODM': {'primary': '#E31E24', 'secondary': '#000000'},
            'UDA': {'primary': '#F5A623', 'secondary': '#000000'},
            'Jubilee': {'primary': '#D71920', 'secondary': '#FBB03B'},
            'ANC': {'primary': '#00A651', 'secondary': '#FFFFFF'},
            'Wiper': {'primary': '#8B0000', 'secondary': '#FFD700'},
            'KANU': {'primary': '#000000', 'secondary': '#FF0000'},
            'Independent': {'primary': '#4A5568', 'secondary': '#718096'},
        }
        colors = party_colors.get(party, {'primary': '#4A5568', 'secondary': '#718096'})
        
        # Create campaign
        campaign = Campaign(
            slug=slug,
            candidate_name=candidate_name,
            party=party,
            seat_level=seat_level,
            county=county,
            constituency=constituency if constituency else county,
            ward=ward if ward else None,
            slogan=slogan,
            bio=bio,
            colors=json.dumps(colors),
            is_active=True
        )
        
        db.session.add(campaign)
        db.session.flush()
        
        # Create secretary
        access_code = str(random.randint(100000, 999999))
        secretary = Member(
            campaign_id=campaign.id,
            name=manager_name,
            phone=manager_phone,
            role='secretary',
            access_code=access_code,
            is_active=True
        )
        
        db.session.add(secretary)
        db.session.commit()
        
        session['new_campaign'] = {
            'slug': campaign.slug,
            'candidate': campaign.candidate_name,
            'phone': secretary.phone,
            'access_code': access_code
        }
        
        return redirect(url_for('auth.signup_success'))
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/signup/success')
def signup_success():
    campaign = session.get('new_campaign')
    if not campaign:
        return redirect(url_for('auth.signup'))
    
    return render_template('auth/signup_success.html', campaign=campaign)

@auth_bp.route('/auth/test')
def test():
    return jsonify({'status': 'Auth blueprint is working!'})


@auth_bp.route('/c/<slug>/login', methods=['GET', 'POST'])
def campaign_login(slug):
    from app.models import Campaign, Member
    campaign = Campaign.query.filter_by(slug=slug, is_active=True).first_or_404()
    colors = campaign.get_colors()

    error = None
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        code  = request.form.get('access_code', '').strip()
        member = Member.query.filter_by(
            campaign_id=campaign.id,
            phone=phone,
            access_code=code,
            is_active=True
        ).first()
        if not member:
            error = 'Invalid phone number or access code.'
        else:
            from datetime import datetime
            member.last_login = datetime.utcnow()
            db.session.commit()
            session['member_id'] = member.id
            session['campaign_id'] = campaign.id
            return redirect(url_for('dashboard.overview'))

    from app.models import Member as M, Event, Document
    member_count  = M.query.filter_by(campaign_id=campaign.id, is_active=True).count()
    meeting_count = Event.query.filter_by(campaign_id=campaign.id).count()
    pub_gallery   = Document.query.filter_by(
        campaign_id=campaign.id, is_public=True
    ).filter(Document.doc_type.in_(['photo','gallery'])).order_by(
        Document.created_at.desc()).limit(6).all()
    pub_docs      = Document.query.filter_by(
        campaign_id=campaign.id, is_public=True
    ).filter(Document.doc_type.in_(['minutes','manifesto','document'])).order_by(
        Document.created_at.desc()).limit(4).all()

    return render_template('auth/login.html',
        campaign=campaign,
        colors=colors,
        member_count=member_count,
        meeting_count=meeting_count,
        pub_gallery=pub_gallery,
        pub_docs=pub_docs,
        error=error
    )
