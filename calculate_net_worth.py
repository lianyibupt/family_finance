from app import db
from app.models import Asset, Liability
from datetime import datetime

def calculate_latest_net_worth():
    # 找出最新的资产和负债更新日期
    latest_asset_date = None
    latest_liability_date = None
    
    for asset in Asset.query.all():
        if latest_asset_date is None or asset.update_date > latest_asset_date:
            latest_asset_date = asset.update_date
    
    for liability in Liability.query.all():
        if latest_liability_date is None or liability.update_date > latest_liability_date:
            latest_liability_date = liability.update_date
    
    # 使用最新的日期作为基准
    latest_date = max(latest_asset_date, latest_liability_date) if latest_asset_date and latest_liability_date else (latest_asset_date or latest_liability_date)
    
    if not latest_date:
        print("没有找到资产或负债数据")
        return 0, 0, 0
    
    # 计算该日期下的总资产和总负债
    total_assets = 0
    total_liabilities = 0
    
    # 对于资产，我们需要找到每个资产类型的最新记录
    asset_names = set()
    asset_latest = {}
    
    for asset in Asset.query.all():
        if asset.name not in asset_latest or asset.update_date > asset_latest[asset.name]['date']:
            asset_latest[asset.name] = {
                'date': asset.update_date,
                'amount': asset.amount
            }
    
    # 计算总资产
    for asset_info in asset_latest.values():
        total_assets += asset_info['amount']
    
    # 对于负债，同样处理
    liability_names = set()
    liability_latest = {}
    
    for liability in Liability.query.all():
        if liability.name not in liability_latest or liability.update_date > liability_latest[liability.name]['date']:
            liability_latest[liability.name] = {
                'date': liability.update_date,
                'amount': liability.amount
            }
    
    # 计算总负债
    for liability_info in liability_latest.values():
        total_liabilities += liability_info['amount']
    
    # 计算净资产
    net_worth = total_assets - total_liabilities
    
    print(f"最新日期: {latest_date}")
    print(f"总资产: {total_assets:.2f}")
    print(f"总负债: {total_liabilities:.2f}")
    print(f"家庭净资产: {net_worth:.2f}")
    
    return total_assets, total_liabilities, net_worth

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        calculate_latest_net_worth()
