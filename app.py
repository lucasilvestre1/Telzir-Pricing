from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, DecimalField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from .seeds.seeds import run_seeds
from .models.ddd_cities import Cities
from .models.plans import Plans
from .models.price import Price
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
    return None


application = create_app()


@application.errorhandler(404)
def not_found(e):
    return render_template('404.html')


@application.route('/quotes')
def quotes():
    all_quotes = Price.query.order_by(Price.create_date.desc()).all()
    return render_template('quotes.html', quotes=all_quotes, price=Price)


@application.route('/', methods=['GET', 'POST'])
def pricing():
    form = PricingForm()
    price = None
    if form.validate_on_submit():
        price_obj = Price()
        new_price = price_obj.pricing_quotation(
            origin_city_id=Cities.query.filter_by(name=str(form.origin_city.data))[0],
            destiny_city_id=Cities.query.filter_by(name=str(form.destiny_city.data))[0],
            minutes=form.minutes.data,
            plan_id=Plans.query.filter_by(name=str(form.plan.data))[0],
        )
        new_price = Price.query.get(new_price.id)
        # https://stackoverflow.com/questions/68584469/represent-foreign-key-as-value-from-another-column-in-the-foreign-table
        if new_price:
            form = PricingForm()
            price = new_price
            flash('Calculado Com Sucesso!')

        # TODO: list_view - query all result in price and display as table
    return render_template('pricing.html', form=form, price=price)


def possible_cities():
    return Cities.query


def possible_plans():
    return Plans.query

# TODO: Mover Form para outro .py


class PricingForm(FlaskForm):
    origin_city = QuerySelectField(
        'De qual cidade irá fazer a ligação?', validators=[DataRequired()], query_factory=possible_cities)
    destiny_city = QuerySelectField(
        'Para qual cidade deseja ligar?', validators=[DataRequired()], query_factory=possible_cities)
    minutes = IntegerField('Quantos minutos de duração', validators=[DataRequired()])
    plan = QuerySelectField('Escolha um plano', validators=[DataRequired()], query_factory=possible_plans)
    submit = SubmitField("Calcular")
    normal_price = DecimalField('Preço normal')
    falemais_price = DecimalField('Com o FaleMais')
