from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_organization_remove_customuser_role_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="status",
            field=models.CharField(
                choices=[
                    ("TODO", "To Do"),
                    ("IN_PROGRESS", "In Progress"),
                    ("IN_REVIEW", "In Review"),
                    ("DONE", "Done"),
                ],
                default="TODO",
                max_length=20,
                db_index=True,
            ),
        ),
        migrations.AlterField(
            model_name="ticket",
            name="priority",
            field=models.CharField(
                choices=[
                    ("LOW", "Low"),
                    ("MEDIUM", "Medium"),
                    ("HIGH", "High"),
                    ("URGENT", "Urgent"),
                ],
                default="MEDIUM",
                max_length=20,
                db_index=True,
            ),
        ),
    ]
