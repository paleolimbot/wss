

import json
import random

MAX_ITERATIONS = 10000


def order_choices(choices):
    """Orders the choices used consistently every time"""
    order = ["Yes", "No", "Always", "Frequently", "Occasionally", "Sometimes", "Never", "Above Compliance",
             "Meets Compliance", "Less than Compliance"]
    return list(sorted(choices, key=lambda choice: order.index(choice) if choice in order else len(order)))


def get_choices(obj):
    """Gets the (ordered) choices from all the dictionaries in the (question) object"""
    choices = set()
    for value in obj.values():
        if isinstance(value, dict) and "question" not in value:
            for key in value:
                choices.add(key)
    return order_choices(choices)


def get_dependent_questions(obj):
    """Get (direct) dependent questions of an object so they may be iterated through"""
    if not isinstance(obj, dict):
        return {}
    questions = {}
    for value in obj.values():
        if isinstance(value, dict):
            for choice, question in value.items():
                if isinstance(question, dict) and "question" in question:
                    if choice not in questions:
                        questions[choice] = []
                    questions[choice].append(question)
    return questions


def get_independent_questions(obj):
    """Get (direct) child questions of an object so they may be iterated through. Could
    be either a list of a value or the value itself"""
    questions = []
    if isinstance(obj, dict):
        for value in obj.values():
            if isinstance(value, list):
                for question in value:
                    if isinstance(question, dict) and "question" in question:
                        questions.append(question)
            elif isinstance(value, dict) and "question" in value:
                questions.append(value)
    elif isinstance(obj, list):
        for value in obj:
            if isinstance(value, dict) and "question" in value:
                questions.append(value)
    return questions


def add_ids(obj, questions=None):
    """Recursively walks through questions and generates unique IDs for each, making sure
    key orders remain consistent (for ID stability)"""
    if questions is None:
        questions = []
    if isinstance(obj, dict):
        if "question" in obj:
            obj["_id"] = len(questions)
            questions.append(len(questions))
            choices = get_choices(obj)
            for key in sorted(obj.keys()):
                if isinstance(obj[key], dict):
                    for choice in choices:
                        if choice in obj[key]:
                            add_ids(obj[key][choice], questions)
                else:
                    add_ids(obj[key], questions)
        else:
            for key in sorted(obj.keys()):
                add_ids(obj[key], questions)
    elif isinstance(obj, list):
        for value in obj:
            add_ids(value, questions)


def add_dependency(obj, dependency, dependencies, follow_lists):
    """drill down to add a single dependency and keep track of which objects use those dependencies
     (used in add_dependencies()). Parent/child relations follow dependencies in questions, where dependency
     relations require question/subquestion answering. These are used for different purposes in the flat
     version of the survey. Passing follow_lists=False will result in a dependency relation, True will
     result in a parent/child one."""
    if isinstance(obj, dict) and "question" in obj:
        depkey = "parents" if follow_lists else "dependencies"
        if depkey not in obj:
            obj[depkey] = []
        obj[depkey].append(dependency)
        dependencies.append(obj["_id"])
    if isinstance(obj, dict):
        for value in obj.values():
            add_dependency(value, dependency, dependencies, follow_lists)
    elif isinstance(obj, list) and follow_lists:
        for value in obj:
            add_dependency(value, dependency, dependencies, follow_lists)


def add_next_question(obj, next_id=None):
    # avoid re-adding next_question (happens with lax dependent/independent question rules)
    if isinstance(obj, dict) and "next_question" in obj:
        return
    dependent_questions = get_dependent_questions(obj)
    independent_questions = get_independent_questions(obj)

    # go through independent questions first
    for j in range(len(independent_questions)):
        if j == len(independent_questions)-1:
            # if last question, pass to parent next_id
            add_next_question(independent_questions[j], next_id)
        else:
            # use the next question's id
            add_next_question(independent_questions[j], independent_questions[j+1]["_id"])

    # assess dependents
    if isinstance(obj, dict) and "question" in obj:
        next_id = independent_questions[0]["_id"] if independent_questions else next_id
        next_questions = {}
        for choice in get_choices(obj):
            if choice in dependent_questions:
                # there is a sub question. use the first as the next question and recursively add next question to that
                # using next_id as the next question
                next_questions[choice] = dependent_questions[choice][0]["_id"]
                depquests = dependent_questions[choice]
                for i in range(len(depquests)):
                    if i == (len(depquests)-1):
                        # last question, use next_id for recursion
                        add_next_question(depquests[i], next_id)
                    else:
                        # use next question id for this choice for recursion
                        add_next_question(depquests[i], depquests[i+1]["_id"])
            else:
                # this is an endpoint. use next_id for this choice
                next_questions[choice] = next_id

        obj["next_question"] = next_questions

    # recursively pass on to non-questions
    if isinstance(obj, dict):
        for value in obj.values():
            if not isinstance(value, dict) or "question" not in value:
                add_next_question(value, next_id)
    elif isinstance(obj, list):
        for value in obj:
            if not isinstance(value, dict) or "question" not in value:
                add_next_question(value, next_id)


def add_dependencies(obj, next_id=None):
    """Adds dependency information (i.e. the next question ID to show given an answer)"""
    if isinstance(obj, dict):
        if "question" in obj:
            dependents = []
            children = []
            dependent_questions = get_dependent_questions(obj)
            independent_questions = get_independent_questions(obj)

            # iterate through direct dependents
            for choice, questions in dependent_questions.items():
                for question in questions:
                    # add dependencies
                    add_dependency(question, obj["_id"], dependents, follow_lists=False)
                    # add parent/child relations
                    add_dependency(question, obj["_id"], children, follow_lists=True)

            # iterate through direct independents
            for question in independent_questions:
                # dependency relations are not meaningful here, just parent/child
                add_dependency(question, obj["_id"], children, follow_lists=True)

            obj["dependents"] = dependents
            obj["children"] = children
            if "dependencies" not in obj:
                obj["dependencies"] = []
            if "parents" not in obj:
                obj["parents"] = []
        for value in obj.values():
            add_dependencies(value)
    elif isinstance(obj, list):
        for value in obj:
            add_dependencies(value)


def add_recursion_level(obj, level=0):
    if isinstance(obj, dict):
        if "question" in obj:
            obj["level"] = level
            level += 1
        for value in obj.values():
            add_recursion_level(value, level)
    elif isinstance(obj, list):
        for value in obj:
            add_recursion_level(value, level)


def question_list(obj, questions=None):
    """Generates a flat list of questions with relevant information for printing (but not scoring)"""
    if questions is None:
        questions = []
    if isinstance(obj, dict):
        if "question" in obj:
            choices = get_choices(obj)
            qout = {"choices": choices}
            for key in ("_id", "question", "level", "next_question", "answer", "comment",
                        "children", "parents", "dependents", "dependencies", "title"):
                if key in obj:
                    qout[key] = obj[key]
            questions.append(qout)
        for value in obj.values():
            question_list(value, questions)
    elif isinstance(obj, list):
        for value in obj:
            question_list(value, questions)
    return questions


def flatten(survey):
    add_ids(survey)
    add_next_question(survey)
    add_dependencies(survey)
    add_recursion_level(survey)
    flat = question_list(survey)
    return list(sorted(flat, key=lambda x: x["_id"]))


def merge_list(obj1, obj2):
    """Merge two objects together as lists"""
    if not isinstance(obj1, list):
        obj1 = [obj1, ]
    if not isinstance(obj2, list):
        obj2 = [obj2, ]
    return obj1 + obj2


def merge_dicts(d1, d2, key, list_merge):
    if "question" in d2:
        for k, v in d2.items():
            if k in list_merge and k in d1:
                d1[k] = merge_list(d1[k], v)
            else:
                d1[k] = v
        if d1[key] is d2:
            del d1[key]


def has_sub_questions(obj):
    for v in obj.values():
        if isinstance(v, dict) and "question" in v:
            return True


def recursive_merge(obj, list_merge=("question", "answer", "_id", "comment", "message")):
    if isinstance(obj, dict):
        # introducing niter ensures the process never gets stuck in an infinite loop
        niter = 0
        while has_sub_questions(obj):
            if niter > MAX_ITERATIONS:
                raise ValueError("Infinite loop detected in recursive merge operation for obj %s" % obj)
            niter += 1
            for key in list(obj.keys()):
                if isinstance(obj[key], dict):
                    merge_dicts(obj, obj[key], key, list_merge)
                    break
        for k, v in obj.items():
            obj[k] = recursive_merge(v, list_merge)
        return obj
    elif isinstance(obj, list):
        return [recursive_merge(value, list_merge) for value in obj]
    else:
        return obj


def evaluate(obj, answers):
    """Uses the answer key to 'take' the survey and collapse back values"""
    if isinstance(obj, dict):
        if "question" in obj:
            answer = answers[obj["_id"]]["answer"] if "answer" in answers[obj["_id"]] else None
            obj["answer"] = answer
            # evaluate keys that depend on the answer. if there is no answer, we have to assume that
            # these are all the sub-dicts in this object and return none for these keys
            if not answer:
                for key in list(obj.keys()):
                    if isinstance(obj[key], dict):
                        obj[key] = None
                    elif isinstance(obj[key], list):
                        obj[key] = [evaluate(v, answers) for v in obj[key]]
            else:
                keys = []
                for key, value in obj.items():
                    if isinstance(value, dict) and answer in value:
                        keys.append(key)
                for key in keys:
                    obj[key] = evaluate(obj[key][answer], answers)
                # evaluate keys that do not depend on the answer
                for key in set(obj.keys()).difference(set(keys)):
                    obj[key] = evaluate(obj[key], answers)
            return obj
        else:
            out = {}
            for key, value in obj.items():
                out[key] = evaluate(value, answers)
            return out
    elif isinstance(obj, list):
        return [evaluate(value, answers) for value in obj]
    else:
        return obj


def shell_ask(question, choices):
    """Generates an answer to a question from shell input"""
    prompt = "\n".join([question, ] +
                       ["[%s] %s" % (i + 1, choice) for i, choice in enumerate(choices)] +
                       ["Enter number: ", ])
    while answer is None:
        try:
            answer = int(input(prompt))
            if 1 <= answer <= len(choices):
                answer = choices[answer-1]
        except ValueError:
            pass
        if answer is None:
            print("Please enter a number corresponding to the correct choice.")

    return answer


def random_choice(question, choices):
    """Generates a random answer to question"""
    return random.choice(choices)


def shell_survey(obj, ask):
    """Turns questions into values"""
    if isinstance(obj, dict):
        if "question" in obj:
            choices = get_choices(obj)
            answer = ask(obj["question"], choices)
            obj["answer"] = answer
            out = {}
            for key, value in obj.items():
                out[key] = shell_survey(value[answer], ask) if isinstance(value, dict) else shell_survey(value, ask)
            return obj
        else:
            out = {}
            for key, value in obj.items():
                out[key] = shell_survey(value, ask)
            return False
    elif isinstance(obj, list):
        return [shell_survey(item, ask) for item in obj]
    else:
        return obj

if __name__ == "__main__":
    # command line interface
    import argparse
    try:
        from tools_common import internal_fail, get_json, do_output, check_output_file
    except ImportError:
        from .tools_common import internal_fail, get_json, do_output, check_output_file

    parser = argparse.ArgumentParser("Recursive Survey Tools")
    parser.add_argument("action", help="The action to perform on the survey JSON",
                        choices=("flatten", "id", "evaluate", "random", "test"))
    parser.add_argument("input", help="JSON file or escaped JSON to use as survey input")
    parser.add_argument("-a", "--answers",
                        help="The JSON file or escaped json to use as answer key for action 'evaluate'")
    parser.add_argument("-o", "--output", help="The output file (missing for STDOUT)")

    args = parser.parse_args()
    action = args.action
    survey = get_json(args.input, "input")
    answers = get_json(args.answers, "answers") if args.answers else None
    outfile = args.output

    # ensure evaluate/answer options are consistent
    if action in "evaluate" and answers is None:
        internal_fail("Option '--answers' is required for action 'evaluate'")
    elif action != "evaluate" and answers is not None:
        internal_fail("Option '--answers' is not required for action '%s'" % action)

    check_output_file(outfile)

    # get output based on action
    try:
        output = {}
        if action == "flatten":
            output = flatten(survey)
        elif action == "id":
            add_ids(survey)
            output = survey
        elif action == "evaluate":
            add_ids(survey)
            output = evaluate(survey, answers)
            output = recursive_merge(output)
        elif action == "random":
            shell_survey(survey, random_choice)
            output = flatten(survey)
        elif action == "survey":
            shell_survey(survey, shell_ask)
            output = survey
        elif action == "test":
            import copy
            # test that ID creation is stable
            print("test that id creation is stable")
            original = copy.deepcopy(survey)
            add_ids(original)
            for i in range(10):
                s = copy.deepcopy(survey)
                add_ids(s)
                if json.dumps(s) != json.dumps(original):
                    raise ValueError("non-stable id creation")
            print("...pass")
            # test that flattening creation is stable
            print("test that flattening creation is stable")
            original = copy.deepcopy(survey)
            original_flat = flatten(original)
            for i in range(10):
                s = copy.deepcopy(survey)
                sf = flatten(s)
                if json.dumps(sf) != json.dumps(original_flat):
                    raise ValueError("non-stable flat survey creation")
                print([q["_id"] for q in sf])
            print("...pass")

        else:
            internal_fail("unsupported action: " % action)

        do_output(output, outfile)

    except Exception as e:
        internal_fail("Error executing action '%s' (%s: %s)" % (action, type(e).__name__, e))

