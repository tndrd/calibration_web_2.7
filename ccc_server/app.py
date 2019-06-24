from flask import Flask, Response, render_template, redirect
from camera import CalibrationCamera
from flask_wtf import FlaskForm
import json
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from config import PORT, DEBUG

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lorem ipsum'

cam_calib = CalibrationCamera()


class InitForm(FlaskForm):
    width_field = StringField("", validators=[DataRequired()])
    height_field = StringField("", validators=[DataRequired()])
    size_field = StringField("", validators=[DataRequired()])
    submit = SubmitField("Start calibration")


@app.route('/', methods=['GET', 'POST'])
def index():
    form = InitForm()
    if form.validate_on_submit():
        width = int(form.width_field.data)
        height = int(form.height_field.data)
        size = int(form.size_field.data)
        cam_calib.start(width, height, size)

        return calibrate_page("new")
    else:
        return render_template('main.html', form=form)


@app.route('/calibration_page')
def calibrate_page(info=None):
    return render_template("catching.html", amount_left=cam_calib.amount_left(), info=info)


@app.route('/check_page')
def check_page():
    if cam_calib.exists():
        return render_template("checking.html")
    else:
        return calibrate_page("not_found")

@app.route('/check_corners')
def check_corners():
    return cam_calib.exists()

@app.route('/add')
def add():
    cam_calib.add_pic()
    return calibrate_page("added")


@app.route('/finish')
def finish():
    ret, error, name = cam_calib.finish()
    data = {"ret" : ret,
            "error" : error,
            "name" : name}
    return json.dumps(data)

@app.route("/preview")
def preview():
    frame = cam_calib.get_preview()
    return Response(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n',
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/final")
def final_page(error, name):
    return render_template("final.html", error=error, name=name)


if __name__ == '__main__':
    if DEBUG:
        app.run(debug=True)
    else:
        app.run(host="192.168.11.1", port=PORT)
