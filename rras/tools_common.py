
import json
import sys
import os


def put_json(obj):
    return json.dumps(obj)


def internal_fail(message, status=-1):
    print(put_json({"error": "%s" % message}))
    sys.exit(status)


def get_json(in_data, argument):
    if os.path.isfile(in_data):
        # is file
        with open(in_data, "r") as f:
            try:
                return json.load(f)
            except ValueError:
                internal_fail("Invalid JSON in file '%s'" % in_data)
    else:
        try:
            # is raw json data
            return json.loads(in_data)
        except ValueError:
            if any(char in in_data for char in "{}[]"):
                internal_fail("invalid JSON supplied as argument %s" % argument)
            else:
                internal_fail("file %s does not exist (argument %s)" % (in_data, argument))


def check_output_file(outfile):
    # ensure output file is appropriately formatted (may still throw IO error if not writable)
    outdir = os.path.dirname(outfile) if outfile else None
    if outdir == "":
        outdir = "."
    if outfile not in (None, "") and not os.path.isdir(outdir):
        internal_fail("invalid output file supplied as argument %s" % outfile)


def do_output(output, outfile, do_exit=True):
    # format output
    formatted_output = put_json(output)

    if outfile:
        with open(outfile, "w") as f:
            try:
                f.write(formatted_output)
            except PermissionError:
                internal_fail("Permission denied to open file '%s'" % outfile)
    else:
        print(formatted_output)

    if do_exit:
        sys.exit(0)