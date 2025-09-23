from personal_dashboard import create_app
from personal_dashboard.routes import occasional_update

app = create_app()

if __name__ == "__main__":
    occasional_update(app, first_time=True)
    app.run(threaded=True, port=5001)
