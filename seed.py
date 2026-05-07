from app import create_app
from app.extensions import db
from app.models import User, Campaign

app = create_app('development')

with app.app_context():
    db.create_all()

    # Create first campaign
    campaign = Campaign(
        slug='julius-were',
        name='Julius Were Campaign',
        candidate='Julius Were',
        constituency='Embakasi East',
        party='ODM',
        tier='starter',
        is_active=True,
    )
    db.session.add(campaign)
    db.session.flush()

    # Create superadmin (you)
    superadmin = User(
        email='brayo@squarerootinc.com',
        name='Brian Omondi',
        role='admin',
        is_superadmin=True,
        campaign_id=None,
    )
    superadmin.set_password('admin1234')
    db.session.add(superadmin)

    # Create secretary for julius-were
    secretary = User(
        email='secretary@julius-were.com',
        name='Campaign Secretary',
        role='secretary',
        is_superadmin=False,
        campaign_id=campaign.id,
    )
    secretary.set_password('secretary1234')
    db.session.add(secretary)

    db.session.commit()
    print("Done.")
    print(f"  Campaign: julius-were (id={campaign.id})")
    print(f"  Superadmin: brayo@squarerootinc.com / admin1234")
    print(f"  Secretary: secretary@julius-were.com / secretary1234")
