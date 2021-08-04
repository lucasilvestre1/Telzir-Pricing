from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from .seeds.seeds import run_seeds
from .models.ddd_cities import Cities
from .models.plans import Plans
from .database import db
from . import settings


def create_app(config_object=settings):
    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)

    with app.app_context():
        db.create_all()
        run_seeds()
        # TODO: Insert seeds here
    return None


application = create_app()


@application.route('/')
def index():
    # conn = get_db_connection()
    # plans = conn.execute('SELECT * FROM plans').fetchall()
    plans = {}
    # conn.close()
    return render_template('index.html', plans=plans)


@application.route('/pricing', methods=['GET', 'POST'])
def pricing():
    form = PricingForm()
    if form.validate_on_submit():
        pass
    return render_template('pricing.html', form=form)


def possible_cities():
    return Cities.query


def possible_plans():
    return Plans.query


class PricingForm(FlaskForm):
    origin_city = QuerySelectField(
        'De qual cidade irá fazer a ligação?', validators=[DataRequired()], query_factory=possible_cities)
    destiny_city = QuerySelectField(
        'Para qual cidade deseja ligar?', validators=[DataRequired()], query_factory=possible_cities)
    minutes = IntegerField('Quantos minutos de duração', validators=[DataRequired()])
    plan = QuerySelectField('Escolha um plano', validators=[DataRequired()], query_factory=possible_plans)
    submit = SubmitField("Calcular")


# def get_db_connection():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# db.init_app(app)


# if __name__ == '__main__':
#     app.run(debug=True)


