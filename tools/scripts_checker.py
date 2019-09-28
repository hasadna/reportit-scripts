import os
from pathlib import Path
import glob
import yaml


SWITCH_ARGS = {
    "src/user/script.yaml":
    [
        "_is_working_time",
        "offender",
        "offender_organization_category",
    ],
    "src/agent/script.yaml":
    [
        "_add_task",
        "_complaint_type",
        "_files_counter",
        "_numOfTasks",
        "_offender_org_category",
        "_only_email",
        "_track",
        "complaint_type",
        "offender",
        "offender_details",
        "offender_organization"
    ]
}

WAIT_VARIABLES = {
    "src/user/script.yaml":
    [
        "_add_more_data",
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
        "offender",
        "offender_details",
        "offender_organization",
        "offender_organization_category",
        "offender_organization_details",
        "offender_person_details",
        "phone",
        "whatsapp"
    ],
    "src/agent/script.yaml":
    [
        "_acceptance_discrimination",
        "_add_task",
        "_details_to_add_to_description",
        "_education_ministry_send",
        "_mahash",
        "_municipal_education_send",
        "_police_arrest",
        "_police_court",
        "_police_has_lawyer",
        "_police_more_details",
        "_police_witness_details",
        "_track",
        "_witness_details",
        "complaint_type",
        "event_location",
        "file1description",
        "file2description",
        "file3description",
        "file4description",
        "file5description",
        "housing_land_type",
        "offender_organization",
        "offender_organization_details",
        "offender_person_details"
    ]
}


DO_VARIABLES = {
    "src/user/script.yaml":
    [
        "_agent_link",
        "_is_working_time",
        "event_description",
    ],
    "src/agent/script.yaml":
    [
        "_complaint_type",
        "_files_counter",
        "_numOfTasks",
        "_offender_org_category",
        "_only_email",
        "complaint_type",
        "event_description",
        "offender",
        "offender_organization",
    ]
}


DO_PARAMS = {
    "src/user/script.yaml":
    [
        # TODO: Check if "" is ok
        "",
        "_file1",
        "_file2",
        "_file3",
        "_file4",
        "_file5",
        "context",
        "record",
        "uploader"
    ],
    "src/agent/script.yaml":
    [
        # TODO: Check if "None" is ok
        None,
        "check_if_municipal_activity",
        "contact_acadeimc_org",
        "contact_education_ministry",
        "contact_education_ministry_ultra_ortodox",
        "contact_health_ministry_zero_racism",
        "contact_justice_ministry_application_commitee",
        "contact_minhal_legal_advisor",
        "contact_municipal_education_department",
        "contact_municipality_activity",
        "contact_ultra_orthodox_edu_inst",
        "education_ministry",
        "education_ministry_unltra_orthodox",
        "findGuardCompany",
        "guard_company_policy_complaint",
        "health_ministry_accessiblity",
        "health_ministry_contacts",
        "health_ministry_public_inquiries",
        "health_non_racism",
        "housing_acceptance_verify_method",
        "housing_check_land_status",
        "justice_ministry_admission_committee",
        "justice_ministry_anti_racism_unit",
        "justice_ministry_ask_assistance",
        "justice_ministry_legal_assistance",
        "mahash",
        "minhal",
        "municipal_activity_communication_log",
        "municipal_education_list",
        "police_security_department",
        "realtors_registrar",
        "record",
        "request_extra_communication_methods",
        "send_anonymously_to_mahash",
        "send_health_centers_antiracism_officers",
        "send_justice_ministry_realtors_registrar",
        "send_to_health_ministry_accessiblity",
        "send_to_health_ministry_accessiblity_anonymously",
        "send_to_health_ministry_public_inqueries_anonymously",
        "send_to_health_ministry_public_inquiries",
        "send_to_mahash",
        "settlement_committee",
        "share_anonymously_with_justice_ministry",
        "share_full_details_with_justice_ministry",
        "update_user",
        "uploader"
    ]
}


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


def check_stats(stats, expected_lists):
    for arg in expected_lists["switch.arg"]:
        assert arg in stats["switch.arg"], arg + \
            " from expected list is not in switch.arg stats"
    for variable in expected_lists["wait.variable"]:
        assert variable in stats["wait.variable"], variable + \
            " from expected list is not in wait.variable stats"
    for variable in expected_lists["do.variable"]:
        assert variable in stats["do.variable"], variable + \
            " from expected list is not in do.variable stats"
    for param in expected_lists["do.params"]:
        assert param in stats["do.params"], param + \
            " from expected list is not in do.params stats"

    do_params = []


def check_keys(keys, name, valid_keys):
    for key in keys:
        assert key in valid_keys, "invalid key in " + name + ": " + key


def check_steps(steps, stats, expected_lists):
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
        step_check(step, stats, expected_lists)


def check_snippet(snippet, stats, expected_lists):
    assert len(snippet) == 2, "snippet length should be 2"
    assert "name" in snippet.keys(), "snippet should have name"
    assert "steps" in snippet.keys(), "snippet should have steps"
    steps = snippet["steps"]
    check_steps(steps, stats, expected_lists)


def check_say(say, stats, expected_lists):
    assert say["say"], "say string should not be empty"


def check_wait(wait, stats, expected_lists):
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
                check_steps(show["steps"], stats, expected_lists)
    if "variable" in wait_value:
        assert wait_value["variable"] in expected_lists["wait.variable"], wait_value["variable"] + \
            " not in expected wait.variable list"
        stats["wait.variable"].add(wait_value["variable"])


def check_goto(goto, stats, expected_lists):
    assert goto["goto"], "goto string should not be empty"


def check_do(do, stats, expected_lists):
    do_value = do["do"]
    check_keys(do_value.keys(), "do", DO_KEYS)
    assert do_value["cmd"] in CMDS, do_value["cmd"] + " should be in CMDS list"
    if "variable" in do_value:
        assert do_value["variable"] in expected_lists["do.variable"], do_value["variable"] + \
            " not in do.variable expected list"
        stats["do.variable"].add(do_value["variable"])
    if "params" in do_value:
        for param in do_value["params"]:
            assert param in expected_lists["do.params"], param + \
                " not in expected do.param list"
            stats["do.params"].add(param)


def check_switch(switch, stats, expected_lists):
    switch_value = switch["switch"]
    check_keys(switch_value.keys(), "switch", SWITCH_KEYS)
    assert "arg" in switch_value, "switch should define arg"
    assert switch_value["arg"] in expected_lists["switch.arg"], switch_value["arg"] + \
        " not in expected switch.arg list"
    stats["switch.arg"].add(switch_value["arg"])
    assert "cases" in switch_value, "switch should define cases"
    cases = switch_value["cases"]
    assert len(cases) != 0, "cases should not be empty"

    seen_matches = set()
    dupe_matches = []
    for case in cases:
        check_keys(case.keys(), "case", CASES_KEYS)
        if "match" in case:
            if case["match"] in seen_matches:
                dupe_matches.append(case["match"])
            seen_matches.add(case["match"])
        if "steps" in case:
            check_steps(case["steps"], stats, expected_lists)
    assert len(dupe_matches) == 0, "switch has duplicates: " + \
        str(dupe_matches) + " for case " + str(case)


if __name__ == '__main__':
    files = Path().glob('src/*/script.yaml')
    for f_in in files:
        print(f_in)
        stats = {
            "switch.arg": set(),
            "wait.variable": set(),
            "do.variable": set(),
            "do.params": set()}
        expected_lists = {
            "switch.arg": SWITCH_ARGS[str(f_in)],
            "wait.variable": WAIT_VARIABLES[str(f_in)],
            "do.variable": DO_VARIABLES[str(f_in)],
            "do.params": DO_PARAMS[str(f_in)], }
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
            check_snippet(snippet, stats, expected_lists)
        check_stats(stats, expected_lists)
