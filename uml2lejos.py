# This is the main file to generate Java code from UML state charts.

# Run command python uml2lejos.py <path_to_statechart_JSON_file> <path_for_output_java_code>

import json
import re
import subprocess
import sys

from statechart_parser import find_key, extract_transitions
from java_switch_code import generate_java_switch_case
from java_file_formatter import create_java_file, format_java_code


# Allowed state names and triggers
allowed_state_names = [
    "Initial",
    "IDLE",
    "FORWARD",
    "BACKWARD",
    "ROTATE_LEFT",
    "ROTATE_RIGHT",
    "Final",
]
allowed_triggers = [
    "buttonPress",
    "distance",
    "timer",
    "color",
    None,
]  # Include None for transitions without triggers


# Check if a path to the JSON file is provided as a command line argument
if len(sys.argv) < 3:
    print(
        "Usage: python script.py <path_to_statechart_JSON_file> <path_for_output_java_code>"
    )
    sys.exit(1)

# Get the path to the JSON file from the command line arguments
json_file_path = sys.argv[1]
# print("first arg", json_file_path)

# Open and read the JSON data from the file
with open(json_file_path, "r") as file:
    data = json.load(file)

# Find all regions in the JSON data
regions = list(find_key(data, "regions"))

# Assuming we want to process only the first regions entry found
# if regions:
# Extract transitions from the first regions entry found
transitions_info = extract_transitions(
    regions[0], allowed_state_names, allowed_triggers
)
# state_data = json.dumps(transitions_info, indent=4)
state_data = transitions_info
# print("JSON DATA", state_data)


# Generate the Java switch-case code
java_switch_case_code = generate_java_switch_case(transitions_info)
# print(java_switch_case_code)


# Define the static header part of the Java code in a JSON structure
java_code_template = {
    "header": """package mdse.rover;

import lejos.hardware.Button;
import lejos.hardware.motor.Motor;
import lejos.hardware.port.MotorPort;
import lejos.hardware.port.SensorPort;
import lejos.hardware.sensor.EV3ColorSensor;
import lejos.hardware.sensor.EV3UltrasonicSensor;
import lejos.hardware.motor.EV3LargeRegulatedMotor;
import lejos.robotics.Color;
import lejos.robotics.RegulatedMotor;
import lejos.robotics.SampleProvider;
import lejos.utility.Delay;

public class Rover {

    private static RegulatedMotor leftMotor = new EV3LargeRegulatedMotor(MotorPort.B);
    private static RegulatedMotor rightMotor = new EV3LargeRegulatedMotor(MotorPort.C);
    private static EV3ColorSensor colorSensor = new EV3ColorSensor(SensorPort.S3);
    private static EV3UltrasonicSensor ultrasonicSensor = new EV3UltrasonicSensor(SensorPort.S1);

    private static volatile RobotState currentState = RobotState.IDLE;
    private static volatile float distance = 0;
    private static volatile int colorId = -1;
        
    public static void main(String[] args) {   
    // Sensor Threads
    Thread colorThread = new Thread(new ColorSensorTask());
    Thread distanceThread = new Thread(new DistanceSensorTask());

    colorThread.start();
    distanceThread.start();
        
    while (true) {
    """,
    "body": """
        {{case_switch_statements}}
    """,
    "footer": """
}
}

  private static void forward() {
    leftMotor.forward();
    rightMotor.forward();
  }

  private static void backward() {
    leftMotor.backward();
    rightMotor.backward();
  }

  private static void rotate_left() {
    int degrees = 180;
    leftMotor.rotate(-degrees, true);
    rightMotor.rotate(degrees);
  }

  private static void rotate_right() {
    int degrees = 180;
    leftMotor.rotate(degrees, true);
    rightMotor.rotate(-degrees);
  }

  private static void stopMotors() {
    leftMotor.stop(true);
    rightMotor.stop();
  }


  private static class ColorSensorTask implements Runnable {
    public void run() {
      SampleProvider colorProvider = colorSensor.getColorIDMode();
      float[] colorSample = new float[colorProvider.sampleSize()];
      while (true) {
        colorProvider.fetchSample(colorSample, 0);
        colorId = (int) colorSample[0];
        // Optional delay for sensor reading
        try {
          Thread.sleep(50); // Poll every 50 milli-second
        } catch (InterruptedException e) {
          // Handle interruption in sleep
        }
      }
    }
  }

  private static class DistanceSensorTask implements Runnable {
    public void run() {
      SampleProvider distanceProvider = ultrasonicSensor.getDistanceMode();
      float[] distanceSample = new float[distanceProvider.sampleSize()];
      while (true) {
        distanceProvider.fetchSample(distanceSample, 0);
        distance = distanceSample[0];
        // Optional delay for sensor reading
      }
    }
  }

  private enum RobotState {
    IDLE, FORWARD, BACKWARD, ROTATE_RIGHT, ROTATE_LEFT, FINAL
  }
}
""",
}


# Assuming switch_case_code contains the generated switch case statements as a string
java_code_template["body"] = java_code_template["body"].replace(
    "{{case_switch_statements}}", java_switch_case_code
)

# To see the complete interpolated Java code
complete_java_code = (
    java_code_template["header"]
    + "\n"
    + java_code_template["body"]
    + "\n"
    + java_code_template["footer"]
)

# print(complete_java_code)

# Write the Java code to a file
java_file = sys.argv[2]

create_java_file(complete_java_code, java_file)

format_java_code(java_file)
