from flask import redirect, render_template
from app import create_app


app = create_app()


if __name__ == '__main__': 
    app.run(debug=True)
