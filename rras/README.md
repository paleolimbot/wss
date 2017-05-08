
## RRAS: Recursive Risk Assessment Survey Tools

This set of tools (two Python modules/command-line utilities and a PHP Wordpress plugin) is designed to streamline the evaluation of surveys that use tree logic to obtain values, and apply this methodology to risk assessment. Many automated survey systems exist, but none are optimized for a recursive network of questions designed to obtain values. The recursive survey tool (`rstools.py` introduces a Javascript object notation (JSON) syntax for describing recursive surveys, and provide methods by which they can be converted to flat lists that are amenable to rendering. The RRAS tool (`rrastools.py`) restricts the JSON syntax introduced for recursive assessments to facilitate its implmentation in risk assessment. Finally, the Wordpress plugin implements these libraries such that surveys can be implemented on Wordpress-powered websites/web apps.

### Recursive Surveys

A recursive survey is one where some questions depend on answers to previous questions, all of which are answered to obtain a value. Consider computing the probability of falling down the stairs.

* Did you tie your shoes?
    * Yes
      * How much have you had to drink in the last 3 hours?
         * More than 6 beer (**70%**)
         * 1 - 6 beer (**40%**)
         * No beer (**2%**) :-(
         * I can't remember (**99%**)
    * No (**50%**)

This example is obviously contrived, but illustrates the nature of a recursive survey. This network of questions can be encoded in JSON in the following way:

```json
{
  "p_falling": {
    "question": "Did you tie your shoes?",
    "p_falling": {
      "Yes": {
        "question": "How much have you had to drink in the last 3 hours?",
        "p_falling": {
          "More than 6 beer": 70, 
          "1 - 6 beer": 40, 
          "I can't remember": 99}
      },
      "No": 50}
  }
}
```

This, of course, is of no use in collecting user data. For this, we use the `rstools.py` script to **flatten** the survey into a series of questions, with all the necessary information to display the right questions given user input.

```
python3 rstools.py flatten survey.json
```

```json
[
  {
    "choices": ["Yes", "No"],
    "question": "Did you tie your shoes?",
    "dependencies": [],
    "children": [1],
    "_id": 0,
    "parents": [],
    "next_question": {
      "Yes": 1,
      "No": null},
    "dependents": [1],
    "level": 0
  },
  {
    "choices": ["More than 6 beer", "I can't remember", "1 - 6 beer"],
    "question": "How much have you had to drink in the last 3 hours?",
    "dependencies": [0],
    "children": [],
    "_id": 1,
    "parents": [0],
    "next_question": {
      "More than 6 beer": null,
      "1 - 6 beer": null,
      "I can't remember": null
    },
    "dependents": [],
    "level": 1
  }
]
```

This '**flatten**ed' format is more verbose than the original, it contains the information a PHP/Javascript application would need to display the survey and collect user input. The order of the choices is not preserved from the original JSON file. This is likely an easy fix, but currently is not available as the software exists at present. A PHP/Javascript/anything application would then add the answers to the flattened JSON like the following:

```json
[
  {
    "choices": ["Yes", "No"],
    "question": "Did you tie your shoes?",
    "dependencies": [],
    "children": [1],
    "_id": 0,
    "parents": [],
    "next_question": {
      "Yes": 1,
      "No": null},
    "dependents": [1],
    "level": 0,
    "answer": "Yes"
  },
  {
    "choices": ["More than 6 beer", "I can't remember", "1 - 6 beer"],
    "question": "How much have you had to drink in the last 3 hours?",
    "dependencies": [0],
    "children": [],
    "_id": 1,
    "parents": [0],
    "next_question": {
      "More than 6 beer": null,
      "1 - 6 beer": null,
      "I can't remember": null
    },
    "dependents": [],
    "level": 1,
    "answer": "I can't remember"
  }
]
```

The `rstools.py` script can then be used to **evaluate** the original survey object.

```
python3 rstools.py evaluate survey.json --answers survey_flat_answers.json
```

```json
{
  "p_falling": 99,
  "_id": [
    0,
    1
  ],
  "question": [
    "Did you tie your shoes?",
    "How much have you had to drink in the last 3 hours?"
  ],
  "answer": [
    "Yes",
    "I can't remember"
  ]
}
```

The **evaluate** operation places the value obtained from the recursive line of questioning in the key *p_falling*, and keeps a list of the questions and answers for the record. This structure can be placed anywhere in a JSON structure, although for best results the enclosure should be simple (a JSON object or array). Values can be any non-question (an object with a "question" element), although again, for debugging benefit, it's best if this value is simple. **With a recursive line of questioning, the key that contains each 'question' object should be the same**. If this is not the case, the recursive merge that gets performed will not complete, and the result will not be as expected.

### Recursive Risk Assessment Surveys

A Recursive Risk Assessment Survey (RRAS) is a special case of a recursive survey that has a particular format and is amenable to calculating risk based on a *likelihood* and a *consequence*. The RRAS format is an array of objects, each of which contains the elements *name*, *likelihood*, and *consequence*. Either the *likelihood* element or the *consequence* element must contain an array. If this key is the *consequence* key, the objects in this list must have elements *name*, and *consequence*. If this key is the *likelihood* key, the objects in this list must have elements *name* and *likelihood*. Because this structure will be **evaluate**d using recursive survey methodology, each *consequence* and *likelihood* element can be a line of recursive questioning. Using the probability of falling down the stairs as a *likelihood*, the RRAS survey would be encoded as follows:

```json
[
  {
    "name": "Falling down the stairs analysis",
    "likelihood": {
      "question": "Did you tie your shoes?",
      "likelihood": {
        "Yes": {
          "question": "How much have you had to drink in the last 3 hours?",
          "likelihood": {
            "More than 6 beer": 70,
            "1 - 6 beer": 40,
            "I can't remember": 99}
        },
        "No": 50}
    },
    "consequence": [
      {
        "name": "Breaking a bone",
        "consequence": 100
      },
      {
        "name": "Minor bruising",
        "consequence": 50
      },
      {
        "name": "Wounded pride",
        "consequence": 10
      }
    ]
  }
]
```

The severity of the *consequence*s do not contain a line of recursive questioning in this case to save space, but in practice this element will always be a question object. When this structre is **evaluate**d, the first element collapses to a single likelihood value.

```
python3 rstools.py evaluate survey.json --answers survey_flat_answers.json
```

```json
[
  {
    "question": [
      "Did you tie your shoes?",
      "How much have you had to drink in the last 3 hours?"
    ],
    "consequence": [
      {
        "consequence": 100,
        "name": "Breaking a bone"
      },
      {
        "consequence": 50,
        "name": "Minor bruising"
      },
      {
        "consequence": 10,
        "name": "Wounded pride"
      }
    ],
    "_id": [
      0,
      1
    ],
    "likelihood": 99,
    "name": "Falling down the stairs analysis",
    "answer": [
      "Yes",
      "I can't remember"
    ]
  }
]
```

So far we have only used `rstools.py`, but `rrastools.py` contains a few additional tools to facilitate the implementation of the RRAS format. First, JSON can be **validate**d to make sure the structure is correct (most specifically that the **report** command will not fail if it is run on the object).

```
python3 rrastools.py validate survey.json
```

```json
{"message": null, "valid": true}
```

In this case there are no problems with the structure, but if there were then *valid* would be `false`, and a message would appear suggesting the cause of the error.

The second command in `rrastools.py` is **report**, which creates JSON that is amenable to output. This is mostly experimental, but could be modified in future iterations to provide the detail required from risk analysis. The **report** command operates on an **evaluate**d object.

```
python3 rrastools.py report survey_eval.json
```

```json
[
  {
    "consequence": 100,
    "name": "Breaking a bone",
    "likelihood_name": "Falling down the stairs analysis",
    "risk": 9900,
    "likelihood": 99
  },
  {
    "consequence": 50,
    "name": "Minor bruising",
    "likelihood_name": "Falling down the stairs analysis",
    "risk": 4950,
    "likelihood": 99
  },
  {
    "consequence": 10,
    "name": "Wounded pride",
    "likelihood_name": "Falling down the stairs analysis",
    "risk": 990,
    "likelihood": 99
  }
]
```

The implementation of this is ongoing, but will always involve a *likelihood*, a *consequence*, and some function that takes both and computes a *risk*. There is no requirement that these values be numeric, nor that they be a single value. In the future more information about the root node will be included (currently only the child nodes have information preserved about them).

### Using the command line tools

The command line tools were created using the `argparse` module from the Python standard library, and have predictable unix-like usage including a `--help` option. The tools were written in Python 3, and may not work if run from a Python 2 interpreter.

```
>> python3 rstools.py --help
usage: Recursive Survey Tools [-h] [-a ANSWERS] [-o OUTPUT]
                              {flatten,id,evaluate,random,test} input

positional arguments:
  {flatten,id,evaluate,random,test}
                        The action to perform on the survey JSON
  input                 JSON file or escaped JSON to use as survey input

optional arguments:
  -h, --help            show this help message and exit
  -a ANSWERS, --answers ANSWERS
                        The JSON file or escaped json to use as answer key for
                        action 'evaluate'
  -o OUTPUT, --output OUTPUT
                        The output file (missing for STDOUT)


>> python3 rrastools.py --help
usage: Recursive Risk Assessment Survey Tools [-h] [-o OUTPUT]
                                              {validate,report,test} input

positional arguments:
  {validate,report,test}
                        The action to perform on the survey JSON
  input                 JSON file or escaped JSON to use as survey input

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
```

All output from this that is not a usage error is returned in JSON format as a single object containing an *error* element (e.g. `{"valid": false, "message": "Likelihood question items must have element 'likelihood' if of type 'dict' at root node 0"}`. These messages may be a litle cryptic to the user but should give the developer an idea of what the problem is. Usage errors result in a standard unix usage error. These will not return JSON, so care should be taken that these do not occur when not observable (e.g. in a PHP script).

### Using the Wordpress plugin

The Wordpress implementation of the RRAS format is in the form of a Wordpress plugin that can be installed (and activated) on any Wordpress installation where the host has Python (3) installed (the entire `rras` subdirectory must be installed, including the `.py` files). Surveys are added to posts or pages using the `[rras]...[/rras]` shortcode, where `...` is a JSON representation of a valid RRAS object. An example of this plugin in use can be found at [http://wsp.fishandwhistle.net/](http://wsp.fishandwhistle.net/).


