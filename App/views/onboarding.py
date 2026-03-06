from flask import Blueprint, render_template, request

onboarding_views = Blueprint('onboarding_views', __name__, template_folder='../templates')


@onboarding_views.route('/onboarding', methods=['GET'])
def onboarding_overview():
    return render_template('onboarding/overview.html')


@onboarding_views.route('/onboarding/step-1', methods=['GET'])
def onboarding_step_1():
    return render_template('onboarding/step_1.html')


@onboarding_views.route('/onboarding/step-2', methods=['GET'])
def onboarding_step_2():
    return render_template('onboarding/step_2.html', params=request.args)


@onboarding_views.route('/onboarding/step-3', methods=['GET'])
def onboarding_step_3():
    return render_template('onboarding/step_3.html', params=request.args)


@onboarding_views.route('/onboarding/step-4', methods=['GET'])
def onboarding_step_4():
    return render_template('onboarding/step_4.html', params=request.args)


@onboarding_views.route('/onboarding/step-5', methods=['GET'])
def onboarding_step_5():
    return render_template('onboarding/step_5.html', params=request.args)


@onboarding_views.route('/onboarding/step-6', methods=['GET'])
def onboarding_step_6():
    return render_template('onboarding/step_6.html', params=request.args)
