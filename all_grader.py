import re
import os
import grader

__author__ = 'neowizard'

patch_dir = os.getcwd() + "/patches"


def patches_preprocessing():
    print("Patches preprocessing .... ")

    list_of_zipped_patches = [os.path.join(patch_dir, f) for f in os.listdir(patch_dir) if f.endswith(".zip")]
    for zipped_patch in list_of_zipped_patches:
        try:
            grader.unpack_zip(zipped_patch, patch_dir)
        except Exception as e:
            print("Failed to unzip {} patch . {}".format(zipped_patch, str(e)))
    list_of_patches = [f for f in os.listdir(patch_dir) if f.endswith(".patch")]
    list_of_patches.sort(key=lambda x : int(re.search(r'\d{4,10}', x.split("/")[-1]).group()))

    print("There are {} patches .".format(len(list_of_patches)))
    return list_of_patches


def results_processing_csv(result_list):
    processed_result = []
    for patch_number, sub_grade, comments in result_list:

        comments = "\" {} \"".format(comments.replace("\"", "\"\""))
        processed_result.append(",".join([patch_number, str(sub_grade), comments]))
    return processed_result


def grade_all(list_of_patches):
    grades = []
    count = 0

    grader.read_cases_points()
    for patch in list_of_patches:
        patch_path = os.path.join(patch_dir, patch)

        try:
            patch_number = re.search(r'\d{4,10}', patch).group()
        except AttributeError as e:
            print("Failed to extract submission number from patch file {}".format(patch))
            patch_number = "Unknown"

        count += 1
        print("{} Testing patch {}".format(count, patch))
        ids, sub_grade, comments = grader.grade(patch_path)

        sub_grade = round(sub_grade, 3)
        print("...{} Done. Grade = {}\n".format(ids, sub_grade))
        grades.append((patch_number, sub_grade, comments))

    grades_csv = open("grades.csv", "w")

    grades_csv.write("\n".join(results_processing_csv(grades)))
    grades_csv.close()
    print("done")


if __name__ == "__main__":
    list_of_patches = patches_preprocessing()
    grade_all(list_of_patches)
    print("Grading script succefully finished")