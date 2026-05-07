from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, Response
from app.extensions import db
from app.models import Campaign, Member, User, Subscription
from datetime import datetime, timedelta
import bcrypt

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def require_admin():
    uid = session.get('admin_id')
    if not uid:
        return None, redirect(url_for('admin.login'))
    u = User.query.filter_by(id=uid, is_superadmin=True, is_active=True).first()
    if not u:
        session.clear()
        return None, redirect(url_for('admin.login'))
    return u, None

# ── Login ─────────────────────────────────────────────────────
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_id'):
        return redirect(url_for('admin.overview'))
    error = None
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        pw    = request.form.get('password','').encode()
        user  = User.query.filter_by(email=email, is_superadmin=True, is_active=True).first()
        if not user or not bcrypt.checkpw(pw, user.password_hash.encode()):
            error = 'Invalid credentials.'
        else:
            session['admin_id'] = user.id
            return redirect(url_for('admin.overview'))
    return render_template('admin/login.html', error=error)

@admin_bp.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin.login'))

# ── Overview ──────────────────────────────────────────────────
@admin_bp.route('/')
@admin_bp.route('')
def overview():
    user, err = require_admin()
    if err: return err
    total_campaigns  = Campaign.query.count()
    active_campaigns = Campaign.query.filter_by(is_active=True).count()
    total_members    = Member.query.filter_by(is_active=True).count()
    trial_campaigns  = Subscription.query.filter_by(status='trial').count()
    overdue          = Subscription.query.filter_by(status='overdue').count()
    recent = Campaign.query.order_by(Campaign.created_at.desc()).limit(8).all()
    expiring = []
    for s in Subscription.query.filter_by(status='trial').all():
        if s.trial_ends and s.trial_ends <= datetime.utcnow() + timedelta(days=7):
            expiring.append(s)
    from sqlalchemy import func, extract
    now = datetime.utcnow()
    revenue = db.session.query(func.sum(Subscription.amount_paid)).filter(
        extract('month', Subscription.last_paid) == now.month,
        extract('year',  Subscription.last_paid) == now.year
    ).scalar() or 0
    return render_template('admin/overview.html',
        admin=user, total_campaigns=total_campaigns, active_campaigns=active_campaigns,
        total_members=total_members, trial_campaigns=trial_campaigns, overdue=overdue,
        recent=recent, expiring=expiring, revenue=revenue, now=now)

# ── Campaigns ─────────────────────────────────────────────────
@admin_bp.route('/campaigns')
def campaigns():
    user, err = require_admin()
    if err: return err
    q = request.args.get('q','')
    query = Campaign.query
    if q:
        query = query.filter(Campaign.candidate_name.ilike(f'%{q}%'))
    all_campaigns = query.order_by(Campaign.created_at.desc()).all()
    return render_template('admin/campaigns.html', admin=user, campaigns=all_campaigns, q=q)

@admin_bp.route('/campaigns/create', methods=['GET','POST'])
def create_campaign():
    user, err = require_admin()
    if err: return err
    if request.method == 'POST':
        import json, random, uuid
        party = request.form.get('party','Independent')
        party_colors = {
            'ODM':{'primary':'#006633','secondary':'#FF6600'},
            'UDA':{'primary':'#F5A623','secondary':'#000000'},
            'Jubilee':{'primary':'#D71920','secondary':'#FBB03B'},
            'ANC':{'primary':'#00A651','secondary':'#FFFFFF'},
            'Wiper':{'primary':'#8B0000','secondary':'#FFD700'},
            'KANU':{'primary':'#000000','secondary':'#FF0000'},
            'Independent':{'primary':'#1e2a3a','secondary':'#e8a838'},
        }
        colors = party_colors.get(party, party_colors['Independent'])
        slug = request.form['candidate_name'].lower().replace(' ','-').replace("'","") + '-' + uuid.uuid4().hex[:4]
        c = Campaign(
            slug=slug, candidate_name=request.form['candidate_name'],
            party=party, seat_level=request.form['seat_level'],
            county=request.form['county'],
            constituency=request.form.get('constituency',''),
            ward=request.form.get('ward',''),
            constituency_code=request.form.get('constituency_code',''),
            slogan=request.form.get('slogan',''),
            bio=request.form.get('bio',''),
            colors=json.dumps(colors), is_active=True
        )
        db.session.add(c)
        db.session.flush()
        code = str(random.randint(100000,999999))
        sec = Member(campaign_id=c.id, name=request.form['secretary_name'],
            phone=request.form['secretary_phone'], role='secretary',
            member_type='official', access_code=code, is_active=True)
        db.session.add(sec)
        trial_days = int(request.form.get('trial_days',30))
        sub = Subscription(campaign_id=c.id, tier=request.form.get('tier','starter'),
            status='trial', trial_ends=datetime.utcnow()+timedelta(days=trial_days),
            next_due=datetime.utcnow()+timedelta(days=trial_days))
        db.session.add(sub)
        db.session.commit()
        flash(f'Campaign created. Secretary access code: {code}', 'success')
        return redirect(url_for('admin.campaigns'))
    return render_template('admin/create_campaign.html', admin=user)

@admin_bp.route('/campaigns/<int:cid>/toggle', methods=['POST'])
def toggle_campaign(cid):
    user, err = require_admin()
    if err: return err
    c = Campaign.query.get_or_404(cid)
    c.is_active = not c.is_active
    db.session.commit()
    flash(f'{c.candidate_name} {"activated" if c.is_active else "deactivated"}.','success')
    return redirect(url_for('admin.campaigns'))

@admin_bp.route('/campaigns/<int:cid>/edit', methods=['GET','POST'])
def edit_campaign(cid):
    user, err = require_admin()
    if err: return err
    c = Campaign.query.get_or_404(cid)
    if request.method == 'POST':
        c.candidate_name    = request.form.get('candidate_name', c.candidate_name)
        c.party             = request.form.get('party', c.party)
        c.seat_level        = request.form.get('seat_level', c.seat_level)
        c.county            = request.form.get('county', c.county)
        c.constituency      = request.form.get('constituency', c.constituency)
        c.ward              = request.form.get('ward', c.ward)
        c.constituency_code = request.form.get('constituency_code', c.constituency_code)
        c.slogan            = request.form.get('slogan', c.slogan)
        c.bio               = request.form.get('bio', c.bio)
        db.session.commit()
        flash('Campaign updated.','success')
        return redirect(url_for('admin.campaigns'))
    return render_template('admin/edit_campaign.html', admin=user, campaign=c)

# ── INSPECT (iframe embed — no session swap) ──────────────────
@admin_bp.route('/inspect/<int:cid>')
def inspect(cid):
    """Renders the campaign dashboard INSIDE the admin shell via iframe."""
    user, err = require_admin()
    if err: return err
    c = Campaign.query.get_or_404(cid)
    sec = Member.query.filter_by(campaign_id=c.id, role='secretary', is_active=True).first()
    members_list = Member.query.filter_by(campaign_id=c.id, is_active=True).all()
    
    from app.models import Event, Task, Bulletin, ActivityLog, Document
    events    = Event.query.filter_by(campaign_id=c.id).order_by(Event.event_date.desc()).limit(5).all()
    tasks     = Task.query.filter_by(campaign_id=c.id).order_by(Task.created_at.desc()).limit(5).all()
    bulletins = Bulletin.query.filter_by(campaign_id=c.id).order_by(Bulletin.created_at.desc()).limit(5).all()
    docs      = Document.query.filter_by(campaign_id=c.id).order_by(Document.created_at.desc()).limit(4).all()
    logs      = ActivityLog.query.filter_by(campaign_id=c.id).order_by(ActivityLog.created_at.desc()).limit(10).all()
    
    from sqlalchemy import func
    ward_counts = db.session.query(Member.ward, func.count(Member.id))\
        .filter_by(campaign_id=c.id, is_active=True)\
        .group_by(Member.ward).all()
    
    tasks_done = Task.query.filter_by(campaign_id=c.id, status='completed').count()
    tasks_all  = Task.query.filter_by(campaign_id=c.id).count()
    
    now = datetime.utcnow()
    last_active = db.session.query(func.max(Member.last_login))\
        .filter_by(campaign_id=c.id).scalar()
    days_silent = (now - last_active).days if last_active else None
    
    colors = c.get_colors()
    
    return render_template('admin/inspect.html',
        admin=user, campaign=c, secretary=sec,
        members=members_list, events=events, tasks=tasks,
        bulletins=bulletins, docs=docs, logs=logs,
        ward_counts=ward_counts,
        tasks_done=tasks_done, tasks_all=tasks_all,
        days_silent=days_silent, now=now,
        colors=colors,
    )

# ── Impersonate (full session swap for editing) ───────────────
@admin_bp.route('/campaigns/<int:cid>/impersonate')
def impersonate(cid):
    user, err = require_admin()
    if err: return err
    c = Campaign.query.get_or_404(cid)
    sec = Member.query.filter_by(campaign_id=c.id, role='secretary', is_active=True).first()
    if not sec:
        flash('No active secretary found.','error')
        return redirect(url_for('admin.campaigns'))
    session['impersonating_from'] = session['admin_id']
    session['member_id']   = sec.id
    session['campaign_id'] = c.id
    return redirect(url_for('dashboard.overview'))

@admin_bp.route('/exit-impersonation')
def exit_impersonation():
    admin_id = session.get('impersonating_from')
    session.pop('member_id', None)
    session.pop('campaign_id', None)
    session.pop('impersonating_from', None)
    if admin_id:
        session['admin_id'] = admin_id
    return redirect(url_for('admin.campaigns'))

# ── Billing ───────────────────────────────────────────────────
@admin_bp.route('/billing')
def billing():
    user, err = require_admin()
    if err: return err
    subs = Subscription.query.join(Campaign).order_by(Campaign.candidate_name).all()
    return render_template('admin/billing.html', admin=user, subs=subs, now=datetime.utcnow())

@admin_bp.route('/billing/<int:cid>/record-payment', methods=['POST'])
def record_payment(cid):
    user, err = require_admin()
    if err: return err
    sub = Subscription.query.filter_by(campaign_id=cid).first_or_404()
    sub.amount_paid = float(request.form.get('amount',0))
    sub.mpesa_ref   = request.form.get('mpesa_ref','').strip()
    sub.tier        = request.form.get('tier', sub.tier)
    sub.status      = 'active'
    sub.last_paid   = datetime.utcnow()
    sub.next_due    = datetime.utcnow() + timedelta(days=30)
    db.session.commit()
    flash(f'Payment recorded for {sub.campaign.candidate_name}.','success')
    return redirect(url_for('admin.billing'))

@admin_bp.route('/billing/<int:cid>/extend-trial', methods=['POST'])
def extend_trial(cid):
    user, err = require_admin()
    if err: return err
    sub = Subscription.query.filter_by(campaign_id=cid).first_or_404()
    days = int(request.form.get('days',14))
    base = sub.trial_ends if sub.trial_ends and sub.trial_ends > datetime.utcnow() else datetime.utcnow()
    sub.trial_ends = base + timedelta(days=days)
    sub.next_due   = sub.trial_ends
    sub.status     = 'trial'
    db.session.commit()
    flash(f'Trial extended for {sub.campaign.candidate_name}.','success')
    return redirect(url_for('admin.billing'))

# ── Intelligence API ──────────────────────────────────────────
@admin_bp.route('/api/intelligence')
def api_intelligence():
    user, err = require_admin()
    if err: return jsonify({'error':'unauthorized'}), 401

    from app.models import Bulletin, Event, Task, ActivityLog, Document, Subscription
    from app.models import WhatsappMessage
    from sqlalchemy import func, extract
    now = datetime.utcnow()

    campaigns = Campaign.query.all()
    scorecards = []
    for c in campaigns:
        members    = Member.query.filter_by(campaign_id=c.id, is_active=True).count()
        events     = Event.query.filter_by(campaign_id=c.id).count()
        tasks_all  = Task.query.filter_by(campaign_id=c.id).count()
        tasks_done = Task.query.filter_by(campaign_id=c.id, status='completed').count()
        bulletins  = Bulletin.query.filter_by(campaign_id=c.id).count()
        docs       = Document.query.filter_by(campaign_id=c.id).count()
        last_active= db.session.query(func.max(Member.last_login)).filter_by(campaign_id=c.id).scalar()
        days_silent= (now - last_active).days if last_active else 999
        recent_logs= ActivityLog.query.filter(
            ActivityLog.campaign_id==c.id,
            ActivityLog.created_at >= now - timedelta(days=7)
        ).count()
        score = 0
        score += min(30, members * 3)
        score += min(20, events * 4)
        score += min(15, bulletins * 3)
        score += min(15, recent_logs * 2)
        score += 10 if days_silent < 3 else (5 if days_silent < 7 else 0)
        score += 10 if tasks_all > 0 and tasks_done/tasks_all > 0.5 else 0
        grade = 'A' if score>=85 else 'B' if score>=70 else 'C' if score>=55 else 'D' if score>=40 else 'F'
        sub = c.subscription
        colors = c.get_colors()
        scorecards.append({
            'id':c.id,'slug':c.slug,'name':c.candidate_name,'party':c.party,
            'seat':c.seat_level,'county':c.county,'constituency':c.constituency,'ward':c.ward or '',
            'primary':colors.get('primary','#e8a838'),'secondary':colors.get('secondary','#1e2a3a'),
            'is_active':c.is_active,'members':members,'events':events,'tasks':tasks_all,
            'tasks_done':tasks_done,'bulletins':bulletins,'docs':docs,
            'recent_logs':recent_logs,'days_silent':days_silent,'score':score,'grade':grade,
            'sub_status':sub.status if sub else 'none','sub_tier':sub.tier if sub else 'none',
            'trial_ends':sub.trial_ends.isoformat() if sub and sub.trial_ends else None,
            'days_to_expiry':(sub.trial_ends-now).days if sub and sub.trial_ends else None,
            'constituency_code':c.constituency_code or '',
        })

    sixty_ago = now - timedelta(days=60)
    logs = ActivityLog.query.filter(ActivityLog.created_at >= sixty_ago).all()
    heatmap = {}
    for log in logs:
        day = log.created_at.strftime('%Y-%m-%d')
        heatmap[day] = heatmap.get(day,0) + 1

    pulse = {}
    for i in range(24):
        label = (now - timedelta(hours=23-i)).strftime('%H:00')
        pulse[label] = 0
    for log in ActivityLog.query.filter(ActivityLog.created_at >= now-timedelta(hours=24)).all():
        label = log.created_at.strftime('%H:00')
        if label in pulse: pulse[label] += 1

    seats = {}
    parties = {}
    county_data = {}
    for c in campaigns:
        seats[c.seat_level] = seats.get(c.seat_level,0)+1
        parties[c.party]    = parties.get(c.party,0)+1
        county = (c.county or '').upper()
        if county:
            if county not in county_data:
                county_data[county] = {'campaigns':[],'seats':{}}
            county_data[county]['campaigns'].append({
                'name':c.candidate_name,'seat':c.seat_level,'party':c.party,
                'primary':c.get_colors().get('primary','#e8a838')
            })
            county_data[county]['seats'][c.seat_level] = county_data[county]['seats'].get(c.seat_level,0)+1

    gantt = []
    for c in campaigns:
        sub = c.subscription
        if not sub: continue
        gantt.append({
            'name':c.candidate_name,'seat':c.seat_level,'status':sub.status,'tier':sub.tier,
            'created':sub.created_at.isoformat(),
            'trial_ends':sub.trial_ends.isoformat() if sub.trial_ends else None,
            'next_due':sub.next_due.isoformat() if sub.next_due else None,
            'amount':sub.amount_paid or 0,
        })

    try:
        wa_sent  = WhatsappMessage.query.filter_by(status='sent').count()
        wa_total = WhatsappMessage.query.count()
    except:
        wa_sent = wa_total = 0

    from app.models import Event as Ev, Task as Tk, Bulletin as Bl, Document as Doc
    return jsonify({
        'scorecards':scorecards,'heatmap':heatmap,'pulse':pulse,
        'seats':seats,'parties':parties,'county_data':county_data,'gantt':gantt,
        'totals':{
            'campaigns':len(campaigns),
            'members':Member.query.filter_by(is_active=True).count(),
            'events':Ev.query.count(),'bulletins':Bl.query.count(),
            'tasks':Tk.query.count(),'docs':Doc.query.count(),
            'wa_sent':wa_sent,'wa_total':wa_total,
        },
        'now':now.isoformat(),
    })

# ── Intelligence page ─────────────────────────────────────────
@admin_bp.route('/insights')
def insights():
    user, err = require_admin()
    if err: return err
    return render_template('admin/insights.html', admin=user)

# ── Settings ──────────────────────────────────────────────────
@admin_bp.route('/settings', methods=['GET','POST'])
def settings():
    user, err = require_admin()
    if err: return err
    if request.method == 'POST':
        new_pw  = request.form.get('new_password','').strip()
        confirm = request.form.get('confirm_password','').strip()
        if new_pw and new_pw == confirm and len(new_pw) >= 8:
            user.password_hash = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
            db.session.commit()
            flash('Password updated.','success')
        elif new_pw:
            flash('Passwords do not match or too short.','error')
    return render_template('admin/settings.html', admin=user)
