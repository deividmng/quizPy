# Generated by Django 5.1.5 on 2025-02-03 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_alter_project_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='category',
            field=models.CharField(choices=[('JavaScript Level 1', 'JavaScript Level 1'), ('JavaScript Level 2', 'JavaScript Level 2'), ('JavaScript Level 3', 'JavaScript Level 3'), ('Python Level 1', 'Python Level 1'), ('Python Level 2', 'Python Level 2'), ('Python Level 3', 'Python Level 3'), ('SQL Level 1', 'SQL Level 1'), ('SQL Level 2', 'SQL Level 2'), ('SQL Level 3', 'SQL Level 3'), ('Git Level 1', 'Git Level 1'), ('Git Level 2', 'Git Level 2'), ('Git Level 3', 'Git Level 3'), ('Randon', 'Randon')], default='JavaScript', help_text='Select the category for this question.', max_length=50),
        ),
    ]
