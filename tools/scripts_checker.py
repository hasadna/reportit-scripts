import os
from pathlib import Path
import glob
import yaml

VARIABLES = [
    "_acceptance_discrimination",
    "_add_more_data",
    "_add_task",
    "_details_to_add_to_description",
    "_education_ministry_send",
    "housing_land_type",
    "_police_arrest",
    "_police_court",
    "_police_has_lawyer",
    "_police_more_details",
    "_police_witness_details",
    "_track",
    "_witness_details",
    "complaint_type",
    "email",
    "event_description",
    "event_location",
    "facebook",
    "file1description",
    "file2description",
    "file3description",
    "file4description",
    "file5description",
    "full_name",
    "_mahash",
    "_municipal_education_send",
    "offender",
    "offender_details",
    "offender_organization",
    "offender_organization_category",
    "offender_organization_details",
    "offender_person_details",
    "phone",
    "whatsapp"
]

CMDS = [
    "addMunicipalReaction",
    "addTask",
    "addTextToField",
    "checkOfficeRepresetativeRelevancy",
    "checkOnlyEmail",
    "checkSpecificGuardComplain",
    "combinedEventDescription",
    "combinedPoliceEventDescription",
    "countFiles",
    "createUser",
    "getComplaintType",
    "getGuardCompany",
    "getOffender",
    "getOffenderOrganizationCategory",
    "getTaskCount",
    "isWorkingTime",
    "offenderIsRealEstateCompany",
    "restartConversation",
    "saveUser",
    "selectGovOrgs",
    "selectNGO",
    "showInfoCard",
    "uploader"
]

WAIT_KEYS = {"options", "variable", "long", "placeholder", "validation"}
SHOW_KEYS = {"show", "steps", "value"}
DO_KEYS = {"cmd", "params", "variable"}
SWITCH_KEYS = {"arg", "cases"}
CASES_KEYS = {"match", "steps", "default"}


def check_keys(keys, name, valid_keys):
    for key in keys:
        assert key in valid_keys, "invalid key in " + name + ": " + key


def check_steps(steps):
    switcher = {
        "say": check_say,
        "wait": check_wait,
        "goto": check_goto,
        "do": check_do,
        "switch": check_switch,
    }
    for step in steps:
        assert len(step) == 1, "step length should be 1"
        step_type = list(step.keys())[0]
        step_check = switcher.get(step_type)
        assert step_check, "step type not found: " + step_type
        step_check(step)


def check_snippet(snippet):
    assert len(snippet) == 2, "snippet length should be 2"
    assert "name" in snippet.keys(), "snippet should have name"
    assert "steps" in snippet.keys(), "snippet should have steps"
    steps = snippet["steps"]
    check_steps(steps)


def check_say(say):
    assert say["say"], "say string should not be empty"


def check_wait(wait):
    wait_value = wait["wait"]
    check_keys(wait_value.keys(), "wait", WAIT_KEYS)
    assert not (
        "options" in wait_value and "long" in wait_value), "Cannot set both options and long in wait"
    if "long" in wait_value:
        assert wait_value["long"], "Value of long should be True"
    if "options" in wait_value:
        for show in wait_value["options"]:
            check_keys(show.keys(), "show", SHOW_KEYS)
            assert len(show) != 0, "show should not be empty"
            assert "show" in show, "show should have show"
            if "steps" in show:
                check_steps(show["steps"])
    if "variable" in wait_value:
        assert wait_value["variable"] in VARIABLES, wait_value["variable"] + \
            " not in variables"


def check_goto(goto):
    assert goto["goto"], "goto string should not be empty"


def check_do(do):
    do_value = do["do"]
    check_keys(do_value.keys(), "do", DO_KEYS)
    assert do_value["cmd"] in CMDS, do_value["cmd"] + " should be in CMDS list"


def check_switch(switch):
    switch_value = switch["switch"]
    check_keys(switch_value.keys(), "switch", SWITCH_KEYS)
    switch_value["cases"]
    assert "cases" in switch_value, "switch should define cases"
    cases = switch_value["cases"]
    assert len(cases) != 0, "cases should not be empty"
    for case in cases:
        check_keys(case.keys(), "case", CASES_KEYS)
        if "steps" in case:
            check_steps(case["steps"])


if __name__ == '__main__':
    files = Path().glob('src/*/script.yaml')
    for f_in in files:
        print(f_in)
        scripts = yaml.load(f_in.open(), Loader=yaml.FullLoader)
        assert len(scripts) == 1, "scripts length should be 1"
        script = scripts[0]
        assert len(script) == 3, "script length should be 3"
        assert "description" in script.keys(), "script should have description"
        assert "name" in script.keys(), "script should have name"
        assert "snippets" in script.keys(), "script should have snippets"

        snippets = script["snippets"]
        assert len(snippets) != 0, "snippets should not be empty"
        assert snippets[0]["name"] == "default", "First snippet should be default"
        for snippet in snippets:
            check_snippet(snippet)
