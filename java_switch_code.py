def generate_java_switch_case(transitions_info):
    java_code = "switch (currentState) {\n"

    # Group transitions by source state
    transitions_by_state = {}
    for transition in transitions_info:
        source_state = transition["state"]
        if source_state not in transitions_by_state:
            transitions_by_state[source_state] = []
        transitions_by_state[source_state].append(transition)

    # Process each state
    for state, transitions in transitions_by_state.items():
        if state == "Initial":  # Skip 'Initial' state
            continue

        java_code += f"    case {state}:\n"
        java_code += f'      System.out.println("{state}");\n'

        # Add the basic code for the state based on state name
        if state == "IDLE" or state == "FINAL":
            java_code += "      stopMotors();\n"
        else:
            function_name = state.lower()  # Convert state name to lowercase
            java_code += (
                f"      {function_name}();\n"  # Call the function based on state name
            )

        # Process transitions from this state
        for t in transitions:
            target = t["target"]
            trigger = t["trigger"]

            if trigger:
                condition_str = ""
                if "buttonPress" in trigger:
                    button = t["guard"].split("==")[1].strip()
                    condition_str = f"Button.{button}.isDown()"
                elif "color" in trigger:
                    color_condition = t["guard"].split("==")[1].strip()
                    condition_str = f"colorId == {color_condition}"
                elif "distance" in trigger:
                    distance_condition = t["guard"]
                    condition_str = distance_condition
                elif "timer" in trigger:
                    delay_time = t["guard"].split("==")[1].strip()
                    condition_str = f"Delay.msDelay({delay_time})"

                java_code += f"      if ({condition_str}) {{\n"
                java_code += f'        System.out.println("GOING {target}");\n'
                java_code += f"        currentState = RobotState.{target};\n"
                java_code += "      }\n"
            else:
                # Direct transition without a trigger
                java_code += f'        System.out.println("GOING {target}");\n'
                java_code += f"      currentState = RobotState.{target};\n"

        java_code += "      break;\n"

    java_code += "    case FINAL:\n"
    java_code += '      System.out.println("FINAL");\n'
    java_code += "      stopMotors();\n"
    java_code += "      System.exit(0);\n      break;\n"

    java_code += "}"

    return java_code


if __name__ == "__main__":
    pass
