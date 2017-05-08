

# extends rstools to specifically deal with risk assessment
# these specific types of surveys are a list of objects with a 'likelihood' (or a list of them)
# element, and a 'consequence' (or list). each of these objects must have one value and one list
# of objects with a 'name' element to facilitate a spreadsheet-like comparison.

def validate(survey):
    """
    Ensures survey is of a type that can be flattened to a risk assessment report
    :param survey: an object created by json.load*()
    :return: A 2-tuple of form valid, message
    """
    # check that root element is a list/array
    if not isinstance(survey, list):
        return False, "Root element is not a list/array"

    for i in range(len(survey)):
        item = survey[i]
        # check that item is a dict
        if not isinstance(item, dict):
            return False, "Survey item is not an object"

        # check that the node has a 'name', 'likelihood' and a 'consequence' element
        if "name" not in item:
            return False, "Element 'name' missing from survey node"
        if "likelihood" not in item:
            return False, "Element 'likelihood' missing from survey node '%s'" % item["name"]
        if "consequence" not in item:
            return False, "Element 'consequence' missing from survey node '%s'" % item["name"]

        # check that there is either a single consequence (not a list) and a list
        # of likelihoods or vice versa
        consequence = item["consequence"]
        likelihood = item["likelihood"]
        if isinstance(consequence, list) and not isinstance(likelihood, list):
            for j in range(len(consequence)):
                cons = consequence[j]
                context = "root node %s, child node %s" % (i, j)
                valid, message = valid_consequence(cons, context)
                if not valid:
                    return False, message
            valid, message = valid_likelihood(likelihood, "root node %s" % i)
            if not valid:
                return False, message
        elif not isinstance(consequence, list) and isinstance(likelihood, list):
            for j in range(len(likelihood)):
                like = likelihood[j]
                context = "root node %s, child node %s" % (i, j)
                valid, message = valid_likelihood(like, context)
                if not valid:
                    return False, message
            valid, message = valid_consequence(consequence, "root node %s" % i)
            if not valid:
                return False, message
        else:
            return False, "Survey items must contain a list of consequences and a single likelihood or vice-versa"

    return True, None


def valid_likelihood(likelihood, context):
    """A likelihood can either be a value (non list) or a question with a likelihood value"""
    if isinstance(likelihood, list):
        return False, "Likelihood items cannot be of type 'list' at " + context
    elif isinstance(likelihood, dict) and "question" in likelihood:
        if "likelihood" not in likelihood:
            return False, "Likelihood question items must have element 'likelihood' if of type 'dict' at " + context

    return True, None


def valid_consequence(consequence, context):
    """A consequence can either be a value (non list) or a question with a consequence value"""
    if isinstance(consequence, list):
        return False, "Likelihood items cannot be of type 'list' at " + context
    elif isinstance(consequence, dict) and "question" in consequence:
        if "consequence" not in consequence:
            return False, "Consequence question items must have element 'consequence' if of type 'dict' at " + context

    return True, None


def risk_default(likelihood, consequence):
    if likelihood is None or consequence is None:
        return None
    else:
        return likelihood * consequence


def create_report(survey, risk=risk_default):
    records = []

    for root_node in survey:
        likelihood = root_node["likelihood"]
        consequence = root_node["consequence"]
        if isinstance(consequence, list):
            for cons in consequence:
                assert isinstance(cons, dict)
                cons["likelihood"] = likelihood
                cons["likelihood_name"] = root_node["name"]
                if "id" in root_node:
                    cons["likelihood_id"] = root_node["id"]
                try:
                    cons["risk"] = risk(cons["likelihood"], cons["consequence"])
                except Exception as e:
                    cons["risk"] = "Error calculating risk: %s" % e
                records.append(cons)
        elif isinstance(likelihood, list):
            for like in likelihood:
                assert isinstance(like, dict)
                like["consequence"] = consequence
                like["consequence_name"] = root_node["name"]
                if "id" in root_node:
                    like["consequence_id"] = root_node["id"]
                try:
                    like["risk"] = risk(like["likelihood"], like["consequence"])
                except Exception as e:
                    like["risk"] = "Error calculating risk: %s" % e
                records.append(like)
        else:
            raise TypeError("Inconsistent types between likelihood and consequence. "
                            "Did you validate prior to creating the report?")
    return records


if __name__ == "__main__":
    # command line interface
    import argparse
    try:
        from tools_common import internal_fail, get_json, do_output, check_output_file
    except ImportError:
        from .tools_common import internal_fail, get_json, do_output, check_output_file

    parser = argparse.ArgumentParser("Recursive Risk Assessment Survey Tools")
    parser.add_argument("action", help="The action to perform on the survey JSON",
                        choices=("validate", "report", "test"))
    parser.add_argument("input", help="JSON file or escaped JSON to use as survey input")
    parser.add_argument("-o", "--output", help="The output file (missing for STDOUT)")

    args = parser.parse_args()
    action = args.action
    survey = get_json(args.input, "input")
    outfile = args.output

    check_output_file(outfile)

    # get output based on action
    try:
        output = {}
        if action == "validate":
            valid, message = validate(survey)
            output = {"valid": valid, "message": message}
        elif action == "report":
            valid, message = validate(survey)
            if not valid:
                internal_fail("Validation of survey failed (" + message + ")")
            output = create_report(survey)
        elif action == "test":
            pass
        else:
            internal_fail("Unsupported action: %s" % action)

        do_output(output, outfile)

    except Exception as e:
        internal_fail("Error executing action '%s' (%s: %s)" % (action, type(e).__name__, e))
