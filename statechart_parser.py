def find_key(data, target_key):
    """Recursively find all values of a specified key in a nested JSON."""
    if isinstance(data, list):
        for item in data:
            yield from find_key(item, target_key)
    elif isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                yield value
            else:
                yield from find_key(value, target_key)


def extract_transitions(regions_data, allowed_state_names, allowed_triggers):
    state_names = {}
    transitions_info = []

    for region in regions_data:
        # Extract the state names
        for vertex in region.get("vertices", []):
            vertex_type = vertex["_type"]
            vertex_name = vertex.get(
                "name", ""
            ).upper()  # Normalize the name to uppercase
            if vertex_type == "UMLState" and vertex_name in allowed_state_names:
                state_names[vertex["_id"]] = vertex_name
            elif vertex_type in ["UMLPseudostate", "UMLFinalState"]:
                kind = vertex.get("kind", "Final").upper()
                if kind == "INITIAL":
                    kind = "Initial"  # Normalize "initial" state
                state_names[vertex["_id"]] = kind

        # Extract the transitions
        for transition in region.get("transitions", []):
            source_id = transition["source"]["$ref"]
            target_id = transition["target"]["$ref"]

            # Check if the source and target states are in the allowed names
            source_name = state_names.get(source_id)
            target_name = state_names.get(target_id)
            if source_name and target_name:
                triggers = transition.get("triggers", [])
                trigger_name = triggers[0]["name"] if triggers else None

                if trigger_name in allowed_triggers or trigger_name is None:
                    transition_entry = {
                        "state": source_name,
                        "target": target_name,
                        "guard": transition.get("guard", ""),
                        "trigger": trigger_name if trigger_name else "",
                    }
                    transitions_info.append(transition_entry)

    return transitions_info


if __name__ == "main":
    pass
