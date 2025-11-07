# Generated migration

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def copy_teacher_from_group(apps, schema_editor):
    """Copy teacher from group to student"""
    Student = apps.get_model('iqcoin_app', 'Student')
    for student in Student.objects.all():
        if student.group:
            student.teacher = student.group.teacher
            student.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('iqcoin_app', '0005_student_is_hidden'),
    ]

    operations = [
        # Step 1: Add teacher field to Student (nullable at first)
        migrations.AddField(
            model_name='student',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to=settings.AUTH_USER_MODEL),
        ),
        # Step 2: Copy data from group.teacher to teacher
        migrations.RunPython(copy_teacher_from_group, reverse_code=migrations.RunPython.noop),
        # Step 3: Make teacher field non-nullable
        migrations.AlterField(
            model_name='student',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to=settings.AUTH_USER_MODEL),
        ),
        # Step 4: Remove group field
        migrations.RemoveField(
            model_name='student',
            name='group',
        ),
        # Step 5: Delete Class model
        migrations.DeleteModel(
            name='Class',
        ),
    ]
