from app import create_app, db
from app.models import Income, Expense, Asset, Liability
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Income': Income, 'Expense': Expense, 'Asset': Asset, 'Liability': Liability}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
