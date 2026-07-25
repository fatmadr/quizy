from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from backend.database.connection import SessionLocal
from backend.models import (
    Document,
    Question,
    QuestionOption,
    Quiz,
    QuizAttempt,
    StudentAnswer,
    User,
)


# ==================================================
# USER <-> DOCUMENT
# ==================================================

def test_user_documents_relationship() -> None:
    print("\n=== USER -> DOCUMENTS ===")

    with SessionLocal() as session:
        statement = (
            select(User)
            .options(selectinload(User.documents))
            .order_by(User.user_id)
        )

        users = session.scalars(statement).all()

        if not users:
            print("No users found.")
            return

        for user in users:
            print(
                f"\nUser: {user.first_name} {user.last_name}"
            )

            if not user.documents:
                print("- No uploaded documents.")
                continue

            for document in user.documents:
                print(f"- Document: {document.title}")


def test_document_teacher_relationship() -> None:
    print("\n=== DOCUMENT -> TEACHER ===")

    with SessionLocal() as session:
        statement = (
            select(Document)
            .options(selectinload(Document.teacher))
            .order_by(Document.document_id)
        )

        documents = session.scalars(statement).all()

        if not documents:
            print("No documents found.")
            return

        for document in documents:
            print(f"\nDocument: {document.title}")
            print(
                f"- Teacher: "
                f"{document.teacher.first_name} "
                f"{document.teacher.last_name}"
            )


# ==================================================
# DOCUMENT <-> QUIZ
# ==================================================

def test_document_quizzes_relationship() -> None:
    print("\n=== DOCUMENT -> QUIZZES ===")

    with SessionLocal() as session:
        statement = (
            select(Document)
            .options(selectinload(Document.quizzes))
            .order_by(Document.document_id)
        )

        documents = session.scalars(statement).all()

        if not documents:
            print("No documents found.")
            return

        for document in documents:
            print(f"\nDocument: {document.title}")

            if not document.quizzes:
                print("- No quizzes generated.")
                continue

            for quiz in document.quizzes:
                print(f"- Quiz: {quiz.title}")


def test_quiz_document_relationship() -> None:
    print("\n=== QUIZ -> DOCUMENT ===")

    with SessionLocal() as session:
        statement = (
            select(Quiz)
            .options(selectinload(Quiz.document))
            .order_by(Quiz.quiz_id)
        )

        quizzes = session.scalars(statement).all()

        if not quizzes:
            print("No quizzes found.")
            return

        for quiz in quizzes:
            print(f"\nQuiz: {quiz.title}")
            print(f"- Source document: {quiz.document.title}")


# ==================================================
# QUIZ <-> QUESTION
# ==================================================

def test_quiz_questions_relationship() -> None:
    print("\n=== QUIZ -> QUESTIONS ===")

    with SessionLocal() as session:
        statement = (
            select(Quiz)
            .options(selectinload(Quiz.questions))
            .order_by(Quiz.quiz_id)
        )

        quizzes = session.scalars(statement).all()

        if not quizzes:
            print("No quizzes found.")
            return

        for quiz in quizzes:
            print(f"\nQuiz: {quiz.title}")

            if not quiz.questions:
                print("- No questions found.")
                continue

            for question in quiz.questions:
                print(
                    f"- {question.position}. "
                    f"{question.question_text}"
                )


def test_question_quiz_relationship() -> None:
    print("\n=== QUESTION -> QUIZ ===")

    with SessionLocal() as session:
        statement = (
            select(Question)
            .options(selectinload(Question.quiz))
            .order_by(Question.question_id)
        )

        questions = session.scalars(statement).all()

        if not questions:
            print("No questions found.")
            return

        for question in questions:
            print(f"\nQuestion: {question.question_text}")
            print(f"- Quiz: {question.quiz.title}")


# ==================================================
# QUESTION <-> QUESTION OPTION
# ==================================================

def test_question_options_relationship() -> None:
    print("\n=== QUESTION -> OPTIONS ===")

    with SessionLocal() as session:
        statement = (
            select(Question)
            .options(selectinload(Question.options))
            .order_by(Question.question_id)
        )

        questions = session.scalars(statement).all()

        if not questions:
            print("No questions found.")
            return

        for question in questions:
            print(
                f"\nQuestion {question.position}: "
                f"{question.question_text}"
            )

            if question.question_type == "open":
                print("- Open question: no options required.")
                continue

            if not question.options:
                print("- No options found.")
                continue

            for option in question.options:
                correctness = (
                    "correct"
                    if option.is_correct
                    else "incorrect"
                )

                print(
                    f"- {option.position}. "
                    f"{option.option_text} "
                    f"({correctness})"
                )


def test_option_question_relationship() -> None:
    print("\n=== OPTION -> QUESTION ===")

    with SessionLocal() as session:
        statement = (
            select(QuestionOption)
            .options(selectinload(QuestionOption.question))
            .order_by(
                QuestionOption.question_id,
                QuestionOption.position,
            )
        )

        options = session.scalars(statement).all()

        if not options:
            print("No question options found.")
            return

        for option in options:
            print(f"\nOption: {option.option_text}")
            print(
                f"- Question: "
                f"{option.question.question_text}"
            )


# ==================================================
# QUIZ <-> QUIZ ATTEMPT
# ==================================================

def test_quiz_attempts_relationship() -> None:
    print("\n=== QUIZ -> ATTEMPTS ===")

    with SessionLocal() as session:
        statement = (
            select(Quiz)
            .options(selectinload(Quiz.attempts))
            .order_by(Quiz.quiz_id)
        )

        quizzes = session.scalars(statement).all()

        if not quizzes:
            print("No quizzes found.")
            return

        for quiz in quizzes:
            print(f"\nQuiz: {quiz.title}")

            if not quiz.attempts:
                print("- No attempts found.")
                continue

            for attempt in quiz.attempts:
                print(
                    f"- Attempt {attempt.attempt_number}: "
                    f"student ID {attempt.student_id}, "
                    f"status {attempt.status}"
                )


# ==================================================
# USER <-> QUIZ ATTEMPT
# ==================================================

def test_user_attempts_relationship() -> None:
    print("\n=== USER -> QUIZ ATTEMPTS ===")

    with SessionLocal() as session:
        statement = (
            select(User)
            .options(selectinload(User.quiz_attempts))
            .order_by(User.user_id)
        )

        users = session.scalars(statement).all()

        if not users:
            print("No users found.")
            return

        for user in users:
            print(
                f"\nUser: {user.first_name} {user.last_name}"
            )

            if not user.quiz_attempts:
                print("- No quiz attempts found.")
                continue

            for attempt in user.quiz_attempts:
                print(
                    f"- Quiz ID: {attempt.quiz_id}, "
                    f"attempt: {attempt.attempt_number}, "
                    f"status: {attempt.status}"
                )


def test_attempt_parent_relationships() -> None:
    print("\n=== ATTEMPT -> QUIZ AND STUDENT ===")

    with SessionLocal() as session:
        statement = (
            select(QuizAttempt)
            .options(
                selectinload(QuizAttempt.quiz),
                selectinload(QuizAttempt.student),
            )
            .order_by(QuizAttempt.attempt_id)
        )

        attempts = session.scalars(statement).all()

        if not attempts:
            print("No quiz attempts found.")
            return

        for attempt in attempts:
            print(f"\nAttempt ID: {attempt.attempt_id}")
            print(f"- Quiz: {attempt.quiz.title}")
            print(
                f"- Student: "
                f"{attempt.student.first_name} "
                f"{attempt.student.last_name}"
            )
            print(
                f"- Attempt number: "
                f"{attempt.attempt_number}"
            )
            print(f"- Status: {attempt.status}")


# ==================================================
# QUIZ ATTEMPT <-> STUDENT ANSWER
# ==================================================

def test_attempt_answers_relationship() -> None:
    print("\n=== QUIZ ATTEMPT -> ANSWERS ===")

    with SessionLocal() as session:
        statement = (
            select(QuizAttempt)
            .options(selectinload(QuizAttempt.answers))
            .order_by(QuizAttempt.attempt_id)
        )

        attempts = session.scalars(statement).all()

        if not attempts:
            print("No quiz attempts found.")
            return

        for attempt in attempts:
            print(f"\nAttempt ID: {attempt.attempt_id}")

            if not attempt.answers:
                print("- No student answers found.")
                continue

            for answer in attempt.answers:
                print(
                    f"- Question ID: {answer.question_id}, "
                    f"points awarded: "
                    f"{answer.points_awarded}"
                )


# ==================================================
# QUESTION <-> STUDENT ANSWER
# ==================================================

def test_question_answers_relationship() -> None:
    print("\n=== QUESTION -> STUDENT ANSWERS ===")

    with SessionLocal() as session:
        statement = (
            select(Question)
            .options(selectinload(Question.student_answers))
            .order_by(Question.question_id)
        )

        questions = session.scalars(statement).all()

        if not questions:
            print("No questions found.")
            return

        for question in questions:
            print(f"\nQuestion: {question.question_text}")

            if not question.student_answers:
                print("- No student answers found.")
                continue

            for answer in question.student_answers:
                print(
                    f"- Attempt ID: {answer.attempt_id}, "
                    f"correct: {answer.is_correct}"
                )


# ==================================================
# QUESTION OPTION <-> STUDENT ANSWER
# ==================================================

def test_option_answers_relationship() -> None:
    print("\n=== OPTION -> STUDENT ANSWERS ===")

    with SessionLocal() as session:
        statement = (
            select(QuestionOption)
            .options(
                selectinload(
                    QuestionOption.student_answers
                )
            )
            .order_by(
                QuestionOption.question_id,
                QuestionOption.position,
            )
        )

        options = session.scalars(statement).all()

        if not options:
            print("No question options found.")
            return

        for option in options:
            print(f"\nOption: {option.option_text}")
            print(
                f"- Selected "
                f"{len(option.student_answers)} time(s)"
            )


# ==================================================
# STUDENT ANSWER -> RELATED OBJECTS
# ==================================================

def test_answer_parent_relationships() -> None:
    print("\n=== STUDENT ANSWER -> RELATED OBJECTS ===")

    with SessionLocal() as session:
        statement = (
            select(StudentAnswer)
            .options(
                selectinload(StudentAnswer.attempt),
                selectinload(StudentAnswer.question),
                selectinload(
                    StudentAnswer.selected_option
                ),
            )
            .order_by(StudentAnswer.answer_id)
        )

        answers = session.scalars(statement).all()

        if not answers:
            print("No student answers found.")
            return

        for answer in answers:
            print(f"\nAnswer ID: {answer.answer_id}")
            print(
                f"- Attempt ID: "
                f"{answer.attempt.attempt_id}"
            )
            print(
                f"- Question: "
                f"{answer.question.question_text}"
            )

            if answer.selected_option is not None:
                print(
                    f"- Selected option: "
                    f"{answer.selected_option.option_text}"
                )

            elif answer.answer_text is not None:
                print(
                    f"- Written answer: "
                    f"{answer.answer_text}"
                )

            else:
                print("- No answer content found.")

            print(f"- Correct: {answer.is_correct}")
            print(
                f"- Points awarded: "
                f"{answer.points_awarded}"
            )


# ==================================================
# RUN ALL RELATIONSHIP TESTS
# ==================================================

def run_relationship_tests() -> None:
    try:
        test_user_documents_relationship()
        test_document_teacher_relationship()

        test_document_quizzes_relationship()
        test_quiz_document_relationship()

        test_quiz_questions_relationship()
        test_question_quiz_relationship()

        test_question_options_relationship()
        test_option_question_relationship()

        test_quiz_attempts_relationship()
        test_user_attempts_relationship()
        test_attempt_parent_relationships()

        test_attempt_answers_relationship()
        test_question_answers_relationship()
        test_option_answers_relationship()
        test_answer_parent_relationships()

        print("\n================================")
        print("All relationship tests completed!")
        print("================================")

    except SQLAlchemyError as error:
        print("\nA database relationship test failed.")
        print(f"Database error: {error}")
        raise

    except AttributeError as error:
        print("\nA relationship attribute is missing.")
        print(f"Relationship error: {error}")
        raise

    except Exception as error:
        print("\nAn unexpected test error occurred.")
        print(f"Error: {error}")
        raise


if __name__ == "__main__":
    run_relationship_tests()