from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='MLModelMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=50, unique=True)),
                ('metrics', models.JSONField(default=dict)),
                ('feature_importance', models.JSONField(default=list)),
                ('sample_count', models.IntegerField(default=0)),
                ('computed_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'ml_model_metrics'},
        ),
    ]
