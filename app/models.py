from app import db
from datetime import datetime

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(50), nullable=False)  # "我" 或 "爱人"
    period_type = db.Column(db.String(10), nullable=False, default='monthly')  # 'monthly' 或 'annual'
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Income {self.id}: {self.category} - {self.amount}>'

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payer = db.Column(db.String(50), nullable=False)  # "我" 或 "爱人"
    period_type = db.Column(db.String(10), nullable=False, default='monthly')  # 'monthly' 或 'annual'
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Expense {self.id}: {self.category} - {self.amount}>'

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 银行存款、基金、股票、房产等
    amount = db.Column(db.Float, nullable=False)
    owner = db.Column(db.String(50), nullable=False)  # "我" 或 "爱人" 或 "共同"
    update_date = db.Column(db.Date, nullable=False)
    period_type = db.Column(db.String(10), nullable=False, default='monthly')  # 'monthly' 或 'annual'
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Asset {self.id}: {self.name} - {self.amount}>'

class Liability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 房贷、车贷、信用卡欠款等
    amount = db.Column(db.Float, nullable=False)
    owner = db.Column(db.String(50), nullable=False)  # "我" 或 "爱人" 或 "共同"
    update_date = db.Column(db.Date, nullable=False)
    period_type = db.Column(db.String(10), nullable=False, default='monthly')  # 'monthly' 或 'annual'
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Liability {self.id}: {self.name} - {self.amount}>'
