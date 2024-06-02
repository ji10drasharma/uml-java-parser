import subprocess
import os


# Function to create a Java code file from the template and dynamic content
def create_java_file(java_code, output_file_path):
    # Writing to a Java file

    with open(output_file_path, "w") as java_file:
        java_file.write(java_code)


def format_java_code(file_path):
    # the jar file needs to be in same directory
    google_java_format_jar_path = "google-java-format-1.18.1-all-deps.jar"

    # The command to format the Java file
    format_command = ["java", "-jar", google_java_format_jar_path, "-i", file_path]

    # Execute the command to format the code
    try:
        subprocess.run(format_command, check=True)

        file_name = os.path.basename(file_path)

        print(f"{file_name} has been formatted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while formatting {file_name}:", e)


if __name__ == "__main__":
    pass
