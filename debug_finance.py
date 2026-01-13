from app import create_app, db
from app.models import User, RiderTransaction, Order
from sqlalchemy import func

app = create_app()
with app.app_context():
    riders = User.query.filter_by(role='rider').all()
    print(f"Riders found: {len(riders)}")
    for r in riders:
        balance = db.session.query(func.sum(RiderTransaction.amount)).filter_by(rider_id=r.id).scalar() or 0.0
        active_tasks = r.assigned_orders.filter(Order.status.notin_(['Delivered', 'Cancelled'])).count()
        print(f"Rider: {r.email}, ID: {r.id}, Name: {r.profile.full_name if r.profile else 'N/A'}, Balance: {balance}, Active Tasks: {active_tasks}")
    
    txs = RiderTransaction.query.all()
    print(f"Total Transactions: {len(txs)}")
    for t in txs:
        print(f"TX: ID {t.id}, Rider {t.rider_id}, Amount {t.amount}, Type {t.type}")
