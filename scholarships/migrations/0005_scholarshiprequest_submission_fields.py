from django.db import migrations, models


def clear_invalid_requests(apps, schema_editor):
    ScholarshipRequest = apps.get_model("scholarships", "ScholarshipRequest")
    ScholarshipRequest.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("scholarships", "0004_alter_scholarship_plural_grants_and_more"),
    ]

    operations = [
        migrations.RunPython(clear_invalid_requests, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="scholarshiprequest",
            name="scholarship",
        ),
        migrations.AddField(
            model_name="scholarshiprequest",
            name="scholarship_name",
            field=models.CharField(max_length=500),
        ),
        migrations.AddField(
            model_name="scholarshiprequest",
            name="provider",
            field=models.CharField(max_length=500),
        ),
        migrations.AddField(
            model_name="scholarshiprequest",
            name="award_amount",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="scholarshiprequest",
            name="notes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="scholarshiprequest",
            name="created_scholarship",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="created_from_request",
                to="scholarships.scholarship",
            ),
        ),
    ]
