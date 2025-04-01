with open('routes.py', 'r') as file:
    content = file.read()

# Replace all occurrences of the choices line
updated_content = content.replace(
    "form.volunteer_id.choices.insert(0, (0, 'Unassigned'))",
    "form.volunteer_id.choices.insert(0, ('', 'Unassigned'))"
)

# Replace all occurrences of the volunteer_id condition
updated_content = updated_content.replace(
    "volunteer_id = form.volunteer_id.data if form.volunteer_id.data != 0 else None",
    "volunteer_id = form.volunteer_id.data if form.volunteer_id.data else None"
)

with open('routes.py', 'w') as file:
    file.write(updated_content)

print("Routes file updated successfully")
