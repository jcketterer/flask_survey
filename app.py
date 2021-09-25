from flask import (
    Flask,
    request,
    render_template,
    redirect,
    flash,
    session,
    make_response,
)
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys


app = Flask(__name__)

app.config["SECRET_KEY"] = "dejaentendu"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

current_survey_key = "current_survey"
responses_key = "responses"


@app.route("/")
def show_beginning_of_survey():
    """renders page to choose a survey"""

    return render_template("survey-choice.html", surveys=surveys)


@app.route("/", methods=["POST"])
def choose_survey():
    """Returns survey to choose from"""
    survey_id = request.form["survey_code"]

    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("already-finished.html")

    survey = surveys[survey_id]
    session[current_survey_key] = survey_id

    return render_template("start-survey.html", survey=survey)


@app.route("/begin", methods=["POST"])
def survey_questions():
    """Clear the session of all responses."""
    session[responses_key] = []

    return redirect("/questions/0")


@app.route("/answer", methods=["POST"])
def handle_questions():
    """Saving Responses and navigating to next question."""
    choice = request.form["answer"]
    text = request.form.get("text", "")

    print(choice, text)

    # adding below responses to list in session storage
    responses = session[responses_key]
    responses.append({"choice": choice, "text": text})

    # adding the below responses to the session storage
    session[responses_key] = responses
    survey_code = session[current_survey_key]
    survey = surveys[survey_code]

    if len(responses) == len(survey.questions):
        return redirect("/end")

    else:
        return redirect(f"/questions/{len(responses)}")


@app.route("/questions/<int:qid>")
def show_questions(qid):
    """show question"""

    responses = session.get(responses_key)
    survey_code = session[current_survey_key]
    survey = surveys[survey_code]

    if responses is None:
        return redirect("/")

    if len(responses) == len(survey.questions):
        return redirect("/end")

    if len(responses) != qid:
        # stops the user from completing survey out of order
        flash(f"Invalid question ID: {qid}")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]
    return render_template("question.html", question_num=qid, question=question)


@app.route("/end")
def end():

    survey_id = session[current_survey_key]
    survey = surveys[survey_id]
    responses = session[responses_key]

    html = render_template("end.html", survey=survey, responses=responses)

    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response
