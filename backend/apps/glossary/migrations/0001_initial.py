from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='GlossaryTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('key', models.SlugField(max_length=120, unique=True, verbose_name='术语标识')),
                ('term', models.CharField(max_length=120, verbose_name='术语名称')),
                ('category', models.CharField(blank=True, default='', max_length=100, verbose_name='分类')),
                ('definition', models.TextField(verbose_name='定义')),
                ('aliases', models.JSONField(blank=True, default=list, verbose_name='别名')),
                ('related_keys', models.JSONField(blank=True, default=list, verbose_name='关联术语')),
            ],
            options={
                'verbose_name': '术语词条',
                'verbose_name_plural': '术语词条',
                'ordering': ['category', 'term'],
            },
        ),
        migrations.AddIndex(
            model_name='glossaryterm',
            index=models.Index(fields=['key'], name='glossary_gl_key_870f3f_idx'),
        ),
        migrations.AddIndex(
            model_name='glossaryterm',
            index=models.Index(fields=['category'], name='glossary_gl_categor_247e39_idx'),
        ),
    ]
