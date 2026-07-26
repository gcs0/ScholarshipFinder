from django.db import migrations, models


def normalize_plural_grants(apps, schema_editor):
    Scholarship = apps.get_model("scholarships", "Scholarship")

    for obj in Scholarship.objects.all():
        raw = obj.plural_grants
        if not raw:
            continue

        parts = [line.strip() for line in raw.split("\n") if line.strip()]
        if not parts:
            continue

        first_line = parts[0]
        first_upper = first_line.upper().strip()

        if first_upper.startswith("Y"):
            label = "Yes"
            rest_of_first = first_line[1:].strip()
        elif first_upper.startswith("N"):
            label = "No"
            rest_of_first = first_line[1:].strip()
        else:
            label = "Unknown"
            rest_of_first = first_line

        extra_lines = parts[1:]
        notes_parts = []
        if rest_of_first:
            notes_parts.append(rest_of_first)
        if extra_lines:
            notes_parts.extend(extra_lines)

        notes_text = " ".join(notes_parts) if notes_parts else ""
        if label == "Unknown" and not notes_text:
            notes_text = first_line

        obj.plural_grants = label

        if notes_text:
            note_line = f"[Plural Grants] {notes_text}"
            existing_notes = obj.notes or ""
            if note_line not in existing_notes:
                obj.notes = (
                    existing_notes + "\n" + note_line if existing_notes else note_line
                )

        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("scholarships", "0002_scholarship_notes"),
    ]

    operations = [
        migrations.RunPython(normalize_plural_grants, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="scholarship",
            name="plural_grants",
            field=models.CharField(
                blank=True,
                choices=[("Yes", "Yes"), ("No", "No"), ("Unknown", "Unknown")],
                default="",
                max_length=7,
            ),
        ),
    ]
