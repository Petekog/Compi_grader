import re
import zipfile
import os
import git
from shutil import rmtree
from shutil import copytree
import csv
import sys
import subprocess
from subprocess import PIPE

git_repo_global = "https://www.cs.bgu.ac.il/~comp211/compiler"
main_folder = os.getcwd()

test_format_global = main_folder + "/" + "grader.ml_format"

test_format_global_scheme = main_folder + "/" + "grader_scheme.ml_format"
test_global_scheme =  main_folder + "/" + "grader_scheme.sh"


workspace_dir = main_folder + "/" + "workspace/"
compiler_dir = workspace_dir + "/" + "compiler"
unpatched_compiler_dir = main_folder + "/" + "compiler_template"
case_template_dir = main_folder + "/" + "cases_template"
tests_dir = workspace_dir + "/" + "cases/"
cases_zip_file = main_folder + "/" + "cases.zip"

test_timeout_global = 160

global_cases_point_file = "tests_points.csv"
global_cases_points_dict = None

def test_one_case_scheme(input_file):
    global test_global_scheme,test_format_global_scheme

    case_number = input_file.replace(".in", "")

    print("\tcase{}... (scheme test)".format(case_number) ,end="")
    sys.stdout.flush()
    case_path = os.path.join(tests_dir, input_file)
    with open(case_path, 'r') as in_file:
        input_str = in_file.read().strip()

    out_file_path = case_path[:-2] + 'out'
    with open(out_file_path, 'r') as out_file:
        expected_output = out_file.read().strip()

    with open(test_format_global_scheme, 'r') as in_file:
        test_format = in_file.read()

    test_string = test_format.format(input_str)

    with open(case_path.replace(".in", ".test"), 'w') as test_file:
        test_file.write(test_string)
    try:
        proc = subprocess.run(["ocaml", "-stdin"], cwd=compiler_dir, input=test_string, encoding="ascii", stdout=PIPE,
                              stderr=PIPE,
                              timeout=test_timeout_global)

        output = proc.stdout
    except subprocess.CalledProcessError as e:
        output = e.output.decode("utf-8").strip("\n")
    except subprocess.TimeoutExpired:
        output = "Timeout after {} seconds".format(test_timeout_global)

    with open(tests_dir + "scheme_{}.scm".format(case_number), "w") as scheme_test_file:
        scheme_test_file.write(output)

    with open(test_global_scheme, 'r') as in_file:
        test_format = in_file.read()

    test_string = test_format.format(case_num=case_number,output=expected_output)#.split("&&&&")

    test_script = "test_script{}".format(case_number)


    result_file = "res_{}".format(case_number)

    with open(tests_dir + test_script, 'w') as test_script_file:
        test_script_file.write(test_string)

    os.system("chmod 777 {}".format(tests_dir + test_script))
    output = "#F"
    try:

        os.chdir(tests_dir)
        proc = subprocess.run(["./" + test_script],cwd= tests_dir,encoding="ascii", stdout=PIPE,
                              stderr=PIPE,shell=True,
                              timeout=test_timeout_global)

        try:
            with open(result_file,"r") as f:
                output = f.read()
        except:
            output = "#F"

        print(output)

    except subprocess.CalledProcessError as e:
        output = e.output.decode("utf-8").strip("\n")
    except subprocess.TimeoutExpired:
        output = "Timeout after {} seconds".format(test_timeout_global)
    os.chdir(main_folder)

    return output


def test_one_case(input_file):
    case_number = input_file.replace(".in", "")
    print("\tcase{}...".format(case_number), end="")
    sys.stdout.flush()
    case_path = os.path.join(tests_dir, input_file)
    with open(case_path, 'r') as in_file:
        input_str = in_file.read().strip()

    out_file_path = case_path[:-2] + 'out'
    with open(out_file_path, 'r') as out_file:
        expected_output = out_file.read().strip()

    with open(test_format_global, 'r') as in_file:
        test_format = in_file.read()

    test_string = test_format.format(input_str, expected_output)

    with open(case_path.replace(".in", ".test"), 'w') as test_file:
        test_file.write(test_string)
    try:
        proc = subprocess.run(["ocaml", "-stdin"], cwd=compiler_dir, input=test_string, encoding="ascii", stdout=PIPE,
                              stderr=PIPE,
                              timeout=test_timeout_global)

        output = proc.stdout
    except subprocess.CalledProcessError as e:
        output = e.output.decode("utf-8").strip("\n")
    except subprocess.TimeoutExpired:
        output = "Timeout after {} seconds".format(test_timeout_global)
    return output

def test_all_cases():
    grade = 0

    notes = ""
    list_of_tests = sorted([f for f in os.listdir(tests_dir) if f.endswith(".in")], key=lambda f: int(f[:f.index(".")]))
    tests_num = len(list_of_tests)
    ids = is_readme_valid()
    if (not ids):
        notes += "\nInvalid readme.txt"
        return [], grade, notes
    #else:
        #notes = "Students id's : {} \n".format(ids)
    failed_cases = ""
    for in_file_path in list_of_tests:
        tested_case = in_file_path.replace(".in", "")
        if global_cases_points_dict[tested_case][1] == "pset!":
            output = test_one_case_scheme(in_file_path)
            true = "#t\n"
        else:
            output = test_one_case(in_file_path)
            true = "true"

        if (output != true):
            failed_cases += "{} ".format(tested_case)

            print("Failed ")
        else:
            print("Passed ")

            grade += global_cases_points_dict[tested_case][0]



        print("done")
    if failed_cases:
        failed_cases = "Failed cases {}".format(failed_cases)
        notes += failed_cases
    return ids, grade, notes


def cases_preprocessing():
    if not os.path.exists(case_template_dir):
        unpack_zip(cases_zip_file, case_template_dir)

    copytree(case_template_dir, tests_dir)


def workspace_preprocessing(patch_file_path):
    if os.path.exists(workspace_dir):
        rmtree(workspace_dir)

    if not os.path.exists(unpatched_compiler_dir):
        ret = os.system("git clone {} '{}'".format(git_repo_global,unpatched_compiler_dir))

    copytree(unpatched_compiler_dir, compiler_dir)
    ret = os.system("cd '{}'; git apply --reject --ignore-whitespace --whitespace=nowarn '{}'".format(compiler_dir,patch_file_path))



def unpack_zip(source, target):
    zip_ref = zipfile.ZipFile(source, 'r')
    zip_ref.extractall(target)
    zip_ref.close()


def is_readme_valid():
    readme_fname = next((f for f in os.listdir(compiler_dir) if f == "readme.txt"), "")
    if (readme_fname == ""):
        return ""
    readme_path = compiler_dir + "/" + readme_fname
    with open(readme_path, 'rb') as readme:
        content = readme.read().decode('ISO-8859-1')
        ids = re.findall(r'\d{7,10}', content)
        if ids is None or ids == []:
            return ""

    return ids


def clean():
    if os.path.exists(workspace_dir):
        rmtree(workspace_dir)

def read_cases_points():
    global global_cases_point_file,global_cases_points_dict
    f = open(global_cases_point_file,"r")
    rows = csv.reader(f)

    next(rows)
    global_cases_points_dict = {}

    sum1 = 0
    cases_num = 0
    for row in list(rows)[:-1]:
        title = row[0]
        tests = row[1].split(",")
        points = int(row[2])

        sum1 += points
        cases_num += len(tests)

        cases_grade = points / len(tests)
        temp_cases = {case:(cases_grade,title) for case in tests}
        global_cases_points_dict.update(temp_cases)

    print("There are {} cases , that sums up to {} points".format(cases_num,sum))
def grade(patch_file_path):
    sub_grade = 0
    notes = ""
    '''If id is not null, then build a workspace to test it in
           Otherwise, test the current workspace '''

    try:
        workspace_preprocessing(patch_file_path)
    except git.exc.GitCommandError as e:

        notes = "Can't run submissions. git apply {} failed with error ({}):\n{}". \
            format(os.path.basename(patch_file_path), e.status, e.stderr)
        return [], sub_grade, notes

    cases_preprocessing()
    ids, sub_grade, sub_notes = test_all_cases()
    notes += sub_notes

    clean()
    return ids, sub_grade, notes


if __name__ == "__main__":
    read_cases_points()
