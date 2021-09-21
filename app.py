from logging import debug
from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbar, DebugToolbarExtension
from surveys import satisfaction_survey as survey


app = Flask(__name__)

app.config["SECRET_KEY"] = "dejaentendu"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
debug = DebugToolbarExtension(app)

responses_key = "responses"


@app.route("/")
def show_beginning_of_survey():
    """Renders main survey page"""

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

    responses = session[responses_key]
    responses.append(choice)
    session[responses_key] = responses

    if len(responses) == len(survey.questions):
        return redirect("/end")

    else:
        return redirect(f"/questions/{len(responses)}")


@app.route("/questions/<int:qid>")
def show_questions(qid):
    """show question"""

    responses = session.get(responses_key)

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
    return render_template("end.html")
