from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommendations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recommendation',
            name='reason',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
