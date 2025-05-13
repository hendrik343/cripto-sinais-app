from datetime import datetime
from sqlalchemy import desc
from sqlalchemy import Column, Integer, String, Float, DateTime, func, and_
from sqlalchemy.ext.declarative import declarative_base

# This will be set by the main app
db = None
Base = declarative_base()

# Function to initialize models with the provided db object
def init_db(db_instance):
    global db
    db = db_instance
    return db

# Admin credentials class for authentication
ADMIN_USER = "admin"
ADMIN_PASS = "vip123"

class CryptoPrice(Base):
    """Model for storing cryptocurrency price data"""
    __tablename__ = 'crypto_price'
    
    id = Column(Integer, primary_key=True)
    coin_id = Column(String(64), nullable=False, index=True)
    symbol = Column(String(16), nullable=False)
    price = Column(Float, nullable=False)
    previous_price = Column(Float, nullable=True)
    percent_change = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    recommendation = Column(String(20), nullable=True)  # "COMPRA" or "VENDA"
    
    @classmethod
    def get_latest_prices(cls):
        """Get the latest price record for each cryptocurrency"""
        if db is None:
            return []
            
        try:
            # Use a subquery to find the maximum timestamp for each coin_id
            subquery = db.session.query(
                cls.coin_id,
                func.max(cls.timestamp).label('max_timestamp')
            ).group_by(cls.coin_id).subquery()
            
            # Join the main table with the subquery to get the latest records
            latest_prices = db.session.query(cls).join(
                subquery,
                and_(
                    cls.coin_id == subquery.c.coin_id,
                    cls.timestamp == subquery.c.max_timestamp
                )
            ).all()
            
            return latest_prices
        except Exception as e:
            print(f"Error getting latest prices: {e}")
            return []
    
    @classmethod
    def get_price_history(cls, coin_id, limit=50):
        """Get price history for a specific cryptocurrency"""
        if db is None:
            return []
            
        try:
            return db.session.query(cls).filter_by(coin_id=coin_id)\
                    .order_by(desc(cls.timestamp))\
                    .limit(limit).all()
        except Exception as e:
            print(f"Error getting price history: {e}")
            return []
    
    @classmethod
    def store_price(cls, coin_id, symbol, price, previous_price=None):
        """Store a new price record"""
        if db is None:
            return None
            
        try:
            # Calculate percent change if previous price is available
            percent_change = None
            if previous_price is not None and previous_price > 0:
                percent_change = ((price - previous_price) / previous_price) * 100
            
            # Create and save new price record
            new_price = cls(
                coin_id=coin_id,
                symbol=symbol,
                price=price,
                previous_price=previous_price,
                percent_change=percent_change
            )
            
            db.session.add(new_price)
            db.session.commit()
            
            return new_price
        except Exception as e:
            print(f"Error storing price: {e}")
            if db.session:
                db.session.rollback()
            return None
    
    def __repr__(self):
        return f"<CryptoPrice {self.symbol} ${self.price} at {self.timestamp}>"


class Payment(Base):
    """Model for storing payment records"""
    __tablename__ = 'payment'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    plan_name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default='completed')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    @classmethod
    def store_payment(cls, email, plan_name, amount, transaction_id=None, status='completed'):
        """Store a new payment record"""
        if db is None:
            return None
            
        try:
            payment = cls(
                email=email,
                plan_name=plan_name,
                amount=amount,
                transaction_id=transaction_id,
                status=status
            )
            
            db.session.add(payment)
            db.session.commit()
            
            return payment
        except Exception as e:
            print(f"Error storing payment: {e}")
            if db.session:
                db.session.rollback()
            return None
    
    @classmethod
    def get_all_payments(cls):
        """Get all payment records ordered by date"""
        if db is None:
            return []
            
        try:
            return db.session.query(cls).order_by(desc(cls.created_at)).all()
        except Exception as e:
            print(f"Error getting payments: {e}")
            return []
    
    def __repr__(self):
        return f"<Payment {self.email} {self.amount}€ for {self.plan_name} at {self.created_at}>"