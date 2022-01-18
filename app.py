from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.widgets import ColorInput
from dotenv import load_dotenv
import os
from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("CSRF_SECRET_KEY")
Bootstrap(app)
client = Client(email=os.environ.get("WYZE_USER"), password=os.environ.get("WYZE_PASSWORD"))


class ColorForm(FlaskForm):
    color = StringField('Color', widget=ColorInput())
    submit = SubmitField('Set Color')


@app.route('/')
def get_lights():  # put application's code here
    message = ''
    try:
        response = client.bulbs.list()
        return render_template('index.html', lights=response, message=message)
    except WyzeApiError as e:
        message = e
    return render_template('index.html', message=message)


@app.route('/on/<mac>/<model>')
def turn_on(mac, model):
    try:
        client.bulbs.turn_on(device_mac=mac, device_model=model)
        return redirect(url_for("bulb_info", mac=mac))
    except WyzeApiError as e:
        return render_template('error.html', error=e)


@app.route('/off/<mac>/<model>')
def turn_off(mac, model):
    try:
        client.bulbs.turn_off(device_mac=mac, device_model=model)
        return redirect(url_for("bulb_info", mac=mac))
    except WyzeApiError as e:
        return render_template('error.html', error=e)


@app.route('/bulb/info/<mac>', methods=['GET', 'POST'])
def bulb_info(mac):
    form = ColorForm()
    message = ''
    try:
        response = client.bulbs.info(device_mac=mac)

        if form.validate_on_submit():
            color = form.color.data
            client.bulbs.set_color(device_mac=response.mac,
                                   device_model=response.product.model,
                                   color=color)
            return redirect(url_for('bulb_info', mac=response.mac))

        return render_template('bulb.html', bulb=response, form=form, message=message)

    except WyzeApiError as e:
        return render_template('error.html', error=e)


if __name__ == '__main__':
    app.run()
