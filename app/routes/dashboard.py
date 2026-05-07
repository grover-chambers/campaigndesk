from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from app.extensions import db
from app.models import Campaign, Member, Bulletin, Event, Task, ActivityLog
from datetime import datetime, timezone
import json, random

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def utc_now():
    return datetime.now(timezone.utc)

# ── Auth guard ────────────────────────────────────────────────
def get_current_member():
    mid = session.get('member_id')
    if not mid:
        return None
    return Member.query.get(mid)

def require_login():
    m = get_current_member()
    if not m or not m.is_active:
        session.clear()
        return None, redirect(url_for('public.landing'))
    c = Campaign.query.get(m.campaign_id)
    if not c:
        session.clear()
        return None, redirect(url_for('public.landing'))
    return (m, c), None

def party_css(campaign):
    colors = campaign.get_colors()
    p = colors.get('primary', '#e8a838')
    s = colors.get('secondary', '#1e2a3a')
    def to_rgb(h):
        h = h.lstrip('#')
        return ','.join(str(int(h[i:i+2],16)) for i in (0,2,4))
    return {'primary': p, 'secondary': s,
            'primary_rgb': to_rgb(p), 'secondary_rgb': to_rgb(s)}

# ── Overview ──────────────────────────────────────────────────
@dashboard_bp.route('/')
@dashboard_bp.route('/overview')
def overview():
    result, err = require_login()
    if err: return err
    member, campaign = result

    colors = party_css(campaign)
    total_members  = Member.query.filter_by(campaign_id=campaign.id, is_active=True).count()
    total_bulletins= Bulletin.query.filter_by(campaign_id=campaign.id).count()
    total_events   = Event.query.filter_by(campaign_id=campaign.id).count()
    open_tasks     = Task.query.filter_by(campaign_id=campaign.id, status='pending').count()
    overdue_tasks  = Task.query.filter(
        Task.campaign_id==campaign.id,
        Task.status=='pending',
        Task.due_date < datetime.utcnow()
    ).count()

    recent_bulletins = Bulletin.query.filter_by(campaign_id=campaign.id)\
                        .order_by(Bulletin.created_at.desc()).limit(3).all()
    upcoming_events  = Event.query.filter(
        Event.campaign_id==campaign.id,
        Event.event_date >= datetime.utcnow(),
        Event.status=='scheduled'
    ).order_by(Event.event_date).limit(3).all()
    recent_tasks = Task.query.filter_by(campaign_id=campaign.id, status='pending')\
                    .order_by(Task.due_date).limit(5).all()
    activities = ActivityLog.query.filter_by(campaign_id=campaign.id)\
                    .order_by(ActivityLog.created_at.desc()).limit(8).all()

    return render_template('dashboard/overview.html',
        member=member, campaign=campaign, colors=colors,
        total_members=total_members, total_bulletins=total_bulletins,
        total_events=total_events, open_tasks=open_tasks, overdue_tasks=overdue_tasks,
        recent_bulletins=recent_bulletins, upcoming_events=upcoming_events,
        recent_tasks=recent_tasks, activities=activities,
        now=datetime.utcnow()
    )

# ── Bulletin board ────────────────────────────────────────────
@dashboard_bp.route('/bulletins')
def bulletins():
    result, err = require_login()
    if err: return err
    member, campaign = result
    tag_filter = request.args.get('tag', 'all')
    q = Bulletin.query.filter_by(campaign_id=campaign.id)
    if tag_filter != 'all':
        q = q.filter_by(tag=tag_filter)
    all_bulletins = q.order_by(Bulletin.created_at.desc()).all()
    return render_template('dashboard/bulletins.html',
        member=member, campaign=campaign, colors=party_css(campaign),
        bulletins=all_bulletins, tag_filter=tag_filter
    )

@dashboard_bp.route('/bulletins/create', methods=['POST'])
def create_bulletin():
    result, err = require_login()
    if err: return err
    member, campaign = result
    b = Bulletin(
        campaign_id=campaign.id,
        title=request.form['title'],
        content=request.form['content'],
        tag=request.form.get('tag','update'),
        is_public=('is_public' in request.form),
        author_id=member.id,
        published_at=utc_now()
    )
    db.session.add(b)
    _log(campaign.id, member.id, 'bulletin_posted', f'Posted bulletin: {b.title}')
    db.session.commit()
    flash('Bulletin posted.', 'success')
    return redirect(url_for('dashboard.bulletins'))

@dashboard_bp.route('/bulletins/<int:bid>/delete', methods=['POST'])
def delete_bulletin(bid):
    result, err = require_login()
    if err: return err
    member, campaign = result
    b = Bulletin.query.filter_by(id=bid, campaign_id=campaign.id).first_or_404()
    db.session.delete(b)
    db.session.commit()
    flash('Bulletin deleted.', 'success')
    return redirect(url_for('dashboard.bulletins'))

@dashboard_bp.route('/bulletins/<int:bid>/toggle-public', methods=['POST'])
def toggle_bulletin_public(bid):
    result, err = require_login()
    if err: return err
    member, campaign = result
    b = Bulletin.query.filter_by(id=bid, campaign_id=campaign.id).first_or_404()
    b.is_public = not b.is_public
    db.session.commit()
    return redirect(url_for('dashboard.bulletins'))

# ── Members / Supporters ──────────────────────────────────────
@dashboard_bp.route('/members')
def members():
    result, err = require_login()
    if err: return err
    member, campaign = result
    ward_filter = request.args.get('ward','')
    role_filter = request.args.get('role','')
    search      = request.args.get('q','')
    q = Member.query.filter_by(campaign_id=campaign.id, is_active=True)
    if ward_filter: q = q.filter(Member.ward==ward_filter)
    if role_filter: q = q.filter(Member.role==role_filter)
    if search: q = q.filter(Member.name.ilike(f'%{search}%'))
    all_members = q.order_by(Member.name).all()

    # Ward summary
    from sqlalchemy import func
    from sqlalchemy import func as sqlfunc
    ward_counts = db.session.query(Member.ward, sqlfunc.count(Member.id))        .filter_by(campaign_id=campaign.id, is_active=True)        .group_by(Member.ward).all()
    wards = [w for w,_ in ward_counts if w]

    return render_template('dashboard/members.html',
        member=member, campaign=campaign, colors=party_css(campaign),
        all_members=all_members, ward_counts=ward_counts, wards=wards,
        ward_filter=ward_filter, role_filter=role_filter, search=search,
        total=len(all_members)
    )

@dashboard_bp.route('/members/add', methods=['POST'])
def add_member():
    result, err = require_login()
    if err: return err
    member, campaign = result
    code = str(random.randint(100000,999999))
    m = Member(
        campaign_id=campaign.id,
        name=request.form['name'],
        phone=request.form['phone'],
        ward=request.form.get('ward','') or None,
        village=request.form.get('village','') or None,
        role=request.form.get('role','supporter'),
        member_type=request.form.get('member_type','supporter'),
        notes=request.form.get('notes','') or None,
        access_code=code,
        is_active=True
    )
    db.session.add(m)
    _log(campaign.id, member.id, 'member_added', f'Added supporter: {m.name}')
    db.session.commit()
    flash(f'Supporter added. Access code: {code}', 'success')
    return redirect(url_for('dashboard.members'))

@dashboard_bp.route('/members/<int:mid>/deactivate', methods=['POST'])
def deactivate_member(mid):
    result, err = require_login()
    if err: return err
    member, campaign = result
    m = Member.query.filter_by(id=mid, campaign_id=campaign.id).first_or_404()
    m.is_active = False
    db.session.commit()
    flash(f'{m.name} deactivated.', 'success')
    return redirect(url_for('dashboard.members'))

# ── Events ────────────────────────────────────────────────────
@dashboard_bp.route('/events')
def events():
    result, err = require_login()
    if err: return err
    member, campaign = result
    upcoming = Event.query.filter(
        Event.campaign_id==campaign.id,
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date).all()
    past = Event.query.filter(
        Event.campaign_id==campaign.id,
        Event.event_date < datetime.utcnow()
    ).order_by(Event.event_date.desc()).limit(10).all()
    return render_template('dashboard/events.html',
        member=member, campaign=campaign, colors=party_css(campaign),
        upcoming=upcoming, past=past, now=datetime.utcnow()
    )

@dashboard_bp.route('/events/create', methods=['POST'])
def create_event():
    result, err = require_login()
    if err: return err
    member, campaign = result
    raw_date = request.form['event_date']
    try:
        dt = datetime.fromisoformat(raw_date)
    except:
        dt = datetime.strptime(raw_date, '%Y-%m-%dT%H:%M')
    e = Event(
        campaign_id=campaign.id,
        title=request.form['title'],
        description=request.form.get('description',''),
        event_date=dt,
        location=request.form.get('location',''),
        venue=request.form.get('venue',''),
        ward=request.form.get('ward',''),
        is_public=('is_public' in request.form),
        status='scheduled',
        created_by=member.id
    )
    db.session.add(e)
    _log(campaign.id, member.id, 'event_created', f'Scheduled event: {e.title}')
    db.session.commit()
    flash('Event scheduled.', 'success')
    return redirect(url_for('dashboard.events'))

@dashboard_bp.route('/events/<int:eid>/complete', methods=['POST'])
def complete_event(eid):
    result, err = require_login()
    if err: return err
    member, campaign = result
    e = Event.query.filter_by(id=eid, campaign_id=campaign.id).first_or_404()
    e.status = 'completed'
    db.session.commit()
    flash('Event marked complete.', 'success')
    return redirect(url_for('dashboard.events'))

@dashboard_bp.route('/events/<int:eid>/cancel', methods=['POST'])
def cancel_event(eid):
    result, err = require_login()
    if err: return err
    member, campaign = result
    e = Event.query.filter_by(id=eid, campaign_id=campaign.id).first_or_404()
    e.status = 'cancelled'
    db.session.commit()
    flash('Event cancelled.', 'success')
    return redirect(url_for('dashboard.events'))

@dashboard_bp.route('/events/<int:eid>/toggle-public', methods=['POST'])
def toggle_event_public(eid):
    result, err = require_login()
    if err: return err
    member, campaign = result
    e = Event.query.filter_by(id=eid, campaign_id=campaign.id).first_or_404()
    e.is_public = not e.is_public
    db.session.commit()
    return redirect(url_for('dashboard.events'))

# ── Tasks ─────────────────────────────────────────────────────
@dashboard_bp.route('/tasks')
def tasks():
    result, err = require_login()
    if err: return err
    member, campaign = result
    status_filter = request.args.get('status','all')
    q = Task.query.filter_by(campaign_id=campaign.id)
    if status_filter != 'all':
        q = q.filter_by(status=status_filter)
    all_tasks = q.order_by(Task.due_date).all()
    return render_template('dashboard/tasks.html',
        member=member, campaign=campaign, colors=party_css(campaign),
        all_tasks=all_tasks, status_filter=status_filter, now=datetime.utcnow()
    )

@dashboard_bp.route('/tasks/create', methods=['POST'])
def create_task():
    result, err = require_login()
    if err: return err
    member, campaign = result
    raw = request.form.get('due_date','')
    due = None
    if raw:
        try: due = datetime.fromisoformat(raw)
        except: pass
    t = Task(
        campaign_id=campaign.id,
        title=request.form['title'],
        description=request.form.get('description',''),
        assigned_to=member.id,
        assigned_by=member.id,
        priority=request.form.get('priority','medium'),
        status='pending',
        due_date=due
    )
    db.session.add(t)
    _log(campaign.id, member.id, 'task_created', f'Created task: {t.title}')
    db.session.commit()
    flash('Task created.', 'success')
    return redirect(url_for('dashboard.tasks'))

@dashboard_bp.route('/tasks/<int:tid>/complete', methods=['POST'])
def complete_task(tid):
    result, err = require_login()
    if err: return err
    member, campaign = result
    t = Task.query.filter_by(id=tid, campaign_id=campaign.id).first_or_404()
    t.status = 'completed'
    t.completed_at = utc_now()
    db.session.commit()
    flash('Task marked complete.', 'success')
    return redirect(url_for('dashboard.tasks'))

@dashboard_bp.route('/tasks/<int:tid>/delete', methods=['POST'])
def delete_task(tid):
    result, err = require_login()
    if err: return err
    member, campaign = result
    t = Task.query.filter_by(id=tid, campaign_id=campaign.id).first_or_404()
    db.session.delete(t)
    db.session.commit()
    flash('Task deleted.', 'success')
    return redirect(url_for('dashboard.tasks'))

# ── Manifesto ─────────────────────────────────────────────────
@dashboard_bp.route('/manifesto')
def manifesto():
    result, err = require_login()
    if err: return err
    member, campaign = result
    return render_template('dashboard/manifesto.html',
        member=member, campaign=campaign, colors=party_css(campaign)
    )

@dashboard_bp.route('/manifesto/save', methods=['POST'])
def save_manifesto():
    result, err = require_login()
    if err: return err
    member, campaign = result
    campaign.manifesto = request.form.get('manifesto','')
    db.session.commit()
    flash('Manifesto saved.', 'success')
    return redirect(url_for('dashboard.manifesto'))

# ── Settings ──────────────────────────────────────────────────
@dashboard_bp.route('/settings')
def settings():
    result, err = require_login()
    if err: return err
    member, campaign = result
    return render_template('dashboard/settings.html',
        member=member, campaign=campaign, colors=party_css(campaign)
    )

@dashboard_bp.route('/settings/save', methods=['POST'])
def save_settings():
    result, err = require_login()
    if err: return err
    member, campaign = result
    campaign.slogan     = request.form.get('slogan', campaign.slogan)
    campaign.bio        = request.form.get('bio', campaign.bio)
    campaign.candidate_photo = request.form.get('photo_url', campaign.candidate_photo)
    db.session.commit()
    flash('Campaign profile updated.', 'success')
    return redirect(url_for('dashboard.settings'))

# ── Logout ────────────────────────────────────────────────────
@dashboard_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('public.landing'))

# ── Keep existing JSON API routes for backwards compat ────────
@dashboard_bp.route('/member')
def member_dashboard():
    return redirect(url_for('dashboard.overview'))

@dashboard_bp.route('/api/stats')
def api_stats():
    result, err = require_login()
    if err: return jsonify({'error':'not logged in'}),401
    member, campaign = result
    return jsonify({
        'total_members':   Member.query.filter_by(campaign_id=campaign.id, is_active=True).count(),
        'total_bulletins': Bulletin.query.filter_by(campaign_id=campaign.id).count(),
        'upcoming_events': Event.query.filter(Event.campaign_id==campaign.id,Event.event_date>=utc_now()).count(),
        'pending_tasks':   Task.query.filter_by(campaign_id=campaign.id,status='pending').count()
    })

# ── Helper ────────────────────────────────────────────────────
def _log(campaign_id, member_id, action_type, description):
    log = ActivityLog(
        campaign_id=campaign_id,
        member_id=member_id,
        action_type=action_type,
        description=description
    )
    db.session.add(log)


# ── Ward map API ──────────────────────────────────────────────
@dashboard_bp.route('/api/ward-stats')
def ward_stats():
    result, err = require_login()
    if err: return jsonify({'error':'not logged in'}), 401
    member, campaign = result
    from sqlalchemy import func as sqlfunc
    supporter_counts = dict(
        db.session.query(Member.ward, sqlfunc.count(Member.id))
        .filter(Member.campaign_id==campaign.id, Member.is_active==True, Member.ward!=None)
        .group_by(Member.ward).all()
    )
    event_counts = dict(
        db.session.query(Event.ward, sqlfunc.count(Event.id))
        .filter(Event.campaign_id==campaign.id, Event.ward!=None)
        .group_by(Event.ward).all()
    )
    all_wards = set(list(supporter_counts.keys()) + list(event_counts.keys()))
    stats = []
    for w in all_wards:
        if not w: continue
        s = supporter_counts.get(w, 0)
        e = event_counts.get(w, 0)
        score = s + (e * 3)
        if score >= 50: heat = 'hot'
        elif score >= 20: heat = 'active'
        elif score >= 5: heat = 'warm'
        else: heat = 'cold'
        stats.append({
            'ward': w,
            'ward_upper': w.upper().strip(),
            'supporters': s,
            'events': e,
            'score': score,
            'heat': heat
        })
    stats.sort(key=lambda x: x['score'], reverse=True)
    # Also return GeoJSON ward names for this constituency for reference
    import json, os
    geo_path = os.path.join(current_app.root_path, 'static', 'geo', 'wards.geojson')
    geo_wards = []
    try:
        with open(geo_path) as f:
            geo = json.load(f)
        const_code = campaign.constituency_code
        for feat in geo['features']:
            p = feat['properties']
            if const_code and str(int(float(p.get('CONST_CODE',0)))) == str(const_code):
                geo_wards.append(p.get('COUNTY_A_1','').upper().strip())
    except: pass
    return jsonify({
        'wards': stats,
        'geo_wards': geo_wards,
        'constituency': campaign.constituency,
        'county': campaign.county
    })


# ── WhatsApp page ─────────────────────────────────────────────
@dashboard_bp.route('/whatsapp')
def whatsapp():
    result, err = require_login()
    if err: return err
    member, campaign = result
    import requests as req
    wa_status = {'ready': False, 'hasQR': False, 'phone': None, 'name': None, 'error': None}
    try:
        r = req.get('http://127.0.0.1:3001/status', timeout=2)
        wa_status = r.json()
    except Exception as e:
        wa_status['error'] = 'WhatsApp bridge not running. Start it with: cd whatsapp && node server.js'
    # Get all active members with phones for broadcast
    supporters = Member.query.filter(
        Member.campaign_id==campaign.id,
        Member.is_active==True,
        Member.phone!=None
    ).all()
    wards = list(set([m.ward for m in supporters if m.ward]))
    return render_template('dashboard/whatsapp.html',
        member=member, campaign=campaign, colors=party_css(campaign),
        wa_status=wa_status, supporters=supporters, wards=wards
    )


@dashboard_bp.route('/whatsapp/send', methods=['POST'])
def whatsapp_send():
    result, err = require_login()
    if err: return err
    member, campaign = result
    import requests as req
    message   = request.form.get('message','').strip()
    recipient = request.form.get('recipient','all')
    ward      = request.form.get('ward','')
    if not message:
        flash('Message cannot be empty.', 'error')
        return redirect(url_for('dashboard.whatsapp'))
    # Build phone list
    q = Member.query.filter(Member.campaign_id==campaign.id, Member.is_active==True, Member.phone!=None)
    if recipient == 'ward' and ward:
        q = q.filter(Member.ward==ward)
    elif recipient == 'officials':
        q = q.filter(Member.member_type=='official')
    targets = q.all()
    sent, failed = 0, 0
    for t in targets:
        phone = t.phone.strip().replace(' ','').replace('-','')
        if not phone.startswith('+'): phone = '+254' + phone.lstrip('0')
        wa_id = phone.lstrip('+') + '@c.us'
        try:
            r = req.post('http://127.0.0.1:3001/send-message',
                json={'to': wa_id, 'message': message}, timeout=10)
            if r.json().get('success'): sent += 1
            else: failed += 1
        except: failed += 1
    flash(f'Broadcast sent: {sent} delivered, {failed} failed.', 'success' if sent else 'error')
    return redirect(url_for('dashboard.whatsapp'))


@dashboard_bp.route('/whatsapp/qr')
def whatsapp_qr():
    import requests as req
    try:
        r = req.get('http://127.0.0.1:3001/qr', timeout=3)
        return jsonify(r.json())
    except:
        return jsonify({'error': 'Bridge not running'})


# ── Cloudinary upload signature ───────────────────────────────
@dashboard_bp.route('/api/cloudinary-signature')
def cloudinary_signature():
    result, err = require_login()
    if err: return jsonify({'error':'not logged in'}), 401
    member, campaign = result
    import cloudinary
    import time, hashlib
    cloud_name  = cloudinary.config().cloud_name
    api_key     = cloudinary.config().api_key
    api_secret  = cloudinary.config().api_secret
    timestamp   = int(time.time())
    folder      = f"campaigndesk/{campaign.slug}"
    params_str  = f"folder={folder}&timestamp={timestamp}{api_secret}"
    signature   = hashlib.sha1(params_str.encode()).hexdigest()
    return jsonify({
        'signature': signature,
        'timestamp': timestamp,
        'api_key': api_key,
        'cloud_name': cloud_name,
        'folder': folder
    })


# ── Ward map page ─────────────────────────────────────────────
@dashboard_bp.route('/map')
def ward_map():
    result, err = require_login()
    if err: return err
    member, campaign = result
    return render_template('dashboard/map.html',
        member=member, campaign=campaign, colors=party_css(campaign)
    )




# ── Document Vault ────────────────────────────────────────────
@dashboard_bp.route('/vault')
def vault():
    result, err = require_login()
    if err: return err
    member, campaign = result
    from app.models import Document
    docs    = Document.query.filter_by(campaign_id=campaign.id)\
                .filter(Document.doc_type.in_(['document','minutes','manifesto']))\
                .order_by(Document.created_at.desc()).all()
    gallery = Document.query.filter_by(campaign_id=campaign.id)\
                .filter(Document.doc_type.in_(['photo','gallery']))\
                .order_by(Document.created_at.desc()).all()
    events_list = Event.query.filter_by(campaign_id=campaign.id)\
                    .order_by(Event.event_date.desc()).limit(20).all()
    return render_template('dashboard/vault.html',
        member=member, campaign=campaign, colors=party_css(campaign),
        docs=docs, gallery=gallery, events_list=events_list,
        cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME',''),
        upload_preset=current_app.config.get('CLOUDINARY_UPLOAD_PRESET','campaigndesk_unsigned'),
    )


@dashboard_bp.route('/vault/save', methods=['POST'])
def vault_save():
    result, err = require_login()
    if err: return err
    member, campaign = result
    from app.models import Document
    doc = Document(
        campaign_id    = campaign.id,
        title          = request.form.get('title','Untitled'),
        doc_type       = request.form.get('doc_type','document'),
        cloudinary_url = request.form.get('cloudinary_url',''),
        cloudinary_id  = request.form.get('cloudinary_id',''),
        thumbnail_url  = request.form.get('thumbnail_url',''),
        caption        = request.form.get('caption',''),
        is_public      = ('is_public' in request.form),
        uploaded_by    = member.id,
        event_id       = request.form.get('event_id') or None,
    )
    db.session.add(doc)
    _log(campaign.id, member.id, 'document_uploaded', f'Uploaded: {doc.title}')
    db.session.commit()
    flash(f'"{doc.title}" saved to vault.', 'success')
    return redirect(url_for('dashboard.vault'))


@dashboard_bp.route('/vault/<int:did>/delete', methods=['POST'])
def vault_delete(did):
    result, err = require_login()
    if err: return err
    member, campaign = result
    from app.models import Document
    doc = Document.query.filter_by(id=did, campaign_id=campaign.id).first_or_404()
    # Delete from Cloudinary
    if doc.cloudinary_id:
        try:
            import cloudinary, cloudinary.uploader
            cloudinary.config(
                cloud_name = current_app.config.get('CLOUDINARY_CLOUD_NAME'),
                api_key    = current_app.config.get('CLOUDINARY_API_KEY'),
                api_secret = current_app.config.get('CLOUDINARY_API_SECRET'),
            )
            cloudinary.uploader.destroy(doc.cloudinary_id,
                resource_type='image' if doc.doc_type in ['photo','gallery'] else 'raw')
        except Exception as e:
            print(f"Cloudinary delete error: {e}")
    db.session.delete(doc)
    db.session.commit()
    flash('File deleted.', 'success')
    return redirect(url_for('dashboard.vault'))


@dashboard_bp.route('/vault/<int:did>/toggle-public', methods=['POST'])
def vault_toggle_public(did):
    result, err = require_login()
    if err: return err
    member, campaign = result
    from app.models import Document
    doc = Document.query.filter_by(id=did, campaign_id=campaign.id).first_or_404()
    doc.is_public = not doc.is_public
    db.session.commit()
    return redirect(url_for('dashboard.vault'))
