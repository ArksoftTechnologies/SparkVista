from app import create_app, db
from app.models import User, Order # Import models for shell context

app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Order': Order}

if __name__ == '__main__':
    app.run(port=5000)
