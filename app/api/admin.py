from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.models import User, Order
from app import db
from app.api.utils import admin_required
from sqlalchemy import func

admin_ns = Namespace('admin', description='Admin operations')

@admin_ns.route('/analytics')
class AdminAnalytics(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get system analytics"""
        total_orders = Order.query.count()
        total_users = User.query.count()
        total_revenue = db.session.query(func.sum(Order.total_amount)).filter(Order.status.in_(['Delivered', 'Completed'])).scalar() or 0.0
        
        # Orders by status
        status_counts = db.session.query(Order.status, func.count(Order.status)).group_by(Order.status).all()
        
        total_riders = User.query.filter_by(role='rider').count()
        
        return {
            'total_orders': total_orders,
            'total_users': total_users,
            'total_revenue': total_revenue,
            'total_riders': total_riders,
            'status_breakdown': dict(status_counts)
        }, 200

@admin_ns.route('/users')
class UserList(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """List all users"""
        users = User.query.all()
        return [user.to_dict() for user in users], 200

    @jwt_required()
    @admin_required
    @admin_ns.doc(body=None)
    def post(self):
        """Create a new user (Staff/Rider/Admin/Customer)"""
        from flask import request
        from app.models import UserProfile
        
        data = request.get_json()
        
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 400
            
        new_user = User(
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'customer')
        )
        db.session.add(new_user)
        db.session.flush()
        
        # Create Profile
        profile = UserProfile(
            user_id=new_user.id,
            full_name=data.get('full_name'),
            phone=data.get('phone')
        )
        db.session.add(profile)
        db.session.commit()
        
        return new_user.to_dict(), 201

@admin_ns.route('/items')
class ItemList(Resource):
    def get(self):
        """Get all laundry items"""
        from app.models.items import LaundryItem
        items = LaundryItem.query.all()
        return [item.to_dict() for item in items], 200

    @jwt_required()
    @admin_required
    @admin_ns.doc(body=None) # Skip documentation model for now
    def post(self):
        """Create a new laundry item"""
        from flask import request
        from app.models.items import LaundryItem
        
        try:
            data = request.get_json()
            
            # Safe conversion helper
            def to_float(val):
                if val == "" or val is None: return 0.0
                return float(val)

            new_item = LaundryItem(
                name=data.get('name'),
                category=data.get('category', 'Clothing'),
                price_wash=to_float(data.get('price_wash')),
                price_dryclean=to_float(data.get('price_dryclean')),
                price_iron=to_float(data.get('price_iron'))
            )
            db.session.add(new_item)
            db.session.commit()
            return new_item.to_dict(), 201
        except ValueError:
            return {'message': 'Invalid price format'}, 400
        except Exception as e:
            return {'message': str(e)}, 500

@admin_ns.route('/items/<int:item_id>')
class ItemResource(Resource):
    @jwt_required()
    @admin_required
    def put(self, item_id):
        """Update a laundry item"""
        from flask import request
        from app.models.items import LaundryItem
        
        item = LaundryItem.query.get_or_404(item_id)
        try:
            data = request.get_json()
            
            # Safe conversion helper
            def to_float(val):
                if val == "" or val is None: return 0.0
                return float(val)

            item.name = data.get('name', item.name)
            item.category = data.get('category', item.category)
            item.price_wash = to_float(data.get('price_wash'))
            item.price_dryclean = to_float(data.get('price_dryclean'))
            item.price_iron = to_float(data.get('price_iron'))
            
            db.session.commit()
            return item.to_dict(), 200
        except ValueError:
            return {'message': 'Invalid price format'}, 400
        except Exception as e:
            return {'message': str(e)}, 500

    @jwt_required()
    @admin_required
    def delete(self, item_id):
        """Delete a laundry item"""
        from app.models.items import LaundryItem
        item = LaundryItem.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {'message': 'Item deleted successfully'}, 200
@admin_ns.route('/orders')
class AdminOrderList(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get all orders with optional status filter"""
        orders = Order.query.order_by(Order.created_at.desc()).all()
        # Enhance dict with customer email and rider name
        result = []
        for o in orders:
            d = o.to_dict()
            d['customer_email'] = o.customer.email
            d['customer_name'] = o.customer.profile.full_name if o.customer.profile and o.customer.profile.full_name else o.customer.email.split('@')[0]
            
            if o.rider:
                d['rider_email'] = o.rider.email
                d['rider_name'] = o.rider.profile.full_name if o.rider.profile and o.rider.profile.full_name else o.rider.email.split('@')[0]
            
            result.append(d)
        return result, 200

@admin_ns.route('/orders/<int:id>')
class AdminOrderDetail(Resource):
    @jwt_required()
    @admin_required
    def get(self, id):
        """Get full order details"""
        order = Order.query.get_or_404(id)
        data = order.to_dict()
        data['items'] = [i.to_dict() for i in order.items]
        data['customer'] = order.customer.to_dict()
        data['rider'] = order.rider.to_dict() if order.rider else None
        if order.pickup_address_id:
             from app.models import Address
             addr = Address.query.get(order.pickup_address_id)
             data['pickup_address'] = addr.to_dict() if addr else None
        return data, 200

@admin_ns.route('/orders/<int:id>/assign')
class AdminOrderAssign(Resource):
    @jwt_required()
    @admin_required
    def put(self, id):
        """Assign rider to order"""
        from flask import request
        data = request.get_json()
        rider_id = data.get('rider_id')
        
        order = Order.query.get_or_404(id)
        rider = User.query.get_or_404(rider_id)
        
        if rider.role != 'rider':
            return {'message': 'User is not a rider'}, 400
            
        order.rider_id = rider.id
        order.status = 'Rider Assigned'
        
        # Log
        from app.models import OrderStatusLog
        import datetime
        current_user_id = db.session.query(User.id).filter_by(role='admin').first().id # Simplified for now or get_jwt_identity
        
        db.session.commit()
        return {'message': 'Rider assigned successfully'}, 200

@admin_ns.route('/riders')
class AdminRiderList(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get all available riders"""
        riders = User.query.filter_by(role='rider').all()
        return [r.to_dict() for r in riders], 200
@admin_ns.route('/settings')
class AdminSettings(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get system settings"""
        from app.models.settings import SystemSetting
        
        commission = SystemSetting.get_value('rider_commission_rate', '0.15')
        
        return {
            'rider_commission_rate': float(commission)
        }, 200

    @jwt_required()
    @admin_required
    def put(self):
        """Update system settings"""
        from flask import request
        from app.models.settings import SystemSetting
        
        data = request.get_json()
        
        if 'rider_commission_rate' in data:
            try:
                rate = float(data['rider_commission_rate'])
                if not (0 <= rate <= 1):
                   return {'message': 'Commission rate must be between 0 and 1'}, 400
                
                SystemSetting.set_value('rider_commission_rate', str(rate), description='Global Rider Commission Rate')
            except ValueError:
                return {'message': 'Invalid rate format'}, 400
                
        return {'message': 'Settings updated successfully'}, 200
@admin_ns.route('/finance/riders')
class AdminFinanceRiders(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get rider wallet balances"""
        from app.models.finance import RiderTransaction
        
        riders = User.query.filter_by(role='rider').all()
        result = []
        
        for rider in riders:
            # Calculate balance: Sum of all transaction amounts
            balance = db.session.query(func.sum(RiderTransaction.amount)).filter_by(rider_id=rider.id).scalar() or 0.0
            
            result.append({
                'id': rider.id,
                'email': rider.email,
                'name': rider.profile.full_name if rider.profile and rider.profile.full_name else 'N/A',
                'balance': balance,
                'active_tasks': rider.assigned_orders.filter(Order.status.notin_(['Delivered', 'Cancelled'])).count()
            })
            
        return result, 200

@admin_ns.route('/finance/payout')
class AdminFinancePayout(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Create a payout transaction"""
        from flask import request
        from app.models.finance import RiderTransaction
        
        data = request.get_json()
        rider_id = data.get('rider_id')
        amount = float(data.get('amount', 0))
        note = data.get('note', 'Admin Payout')
        
        if amount <= 0:
            return {'message': 'Amount must be positive'}, 400
            
        # Payout is a debit, so negative amount
        payout_tx = RiderTransaction(
            rider_id=rider_id,
            amount=-amount,
            type='PAYOUT',
            description=note,
            reference_id=f'PAY-{int(func.now().timestamp())}'
        )
        
        db.session.add(payout_tx)
        db.session.commit()
        
        return {'message': 'Payout processed successfully'}, 201

@admin_ns.route('/finance/history/<int:rider_id>')
class AdminFinanceHistory(Resource):
    @jwt_required()
    @admin_required
    def get(self, rider_id):
        """Get transaction history for a rider"""
        from app.models.finance import RiderTransaction
        
        txs = RiderTransaction.query.filter_by(rider_id=rider_id).order_by(RiderTransaction.created_at.desc()).all()
        return [t.to_dict() for t in txs], 200
