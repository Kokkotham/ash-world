from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='RuleCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(max_length=100, verbose_name='分类名称')),
                ('slug', models.SlugField(max_length=120, unique=True, verbose_name='分类标识')),
                ('chapter_ref', models.CharField(blank=True, default='', max_length=50, verbose_name='章节号')),
                ('source', models.CharField(blank=True, default='core', max_length=50, verbose_name='来源')),
                ('sort_order', models.IntegerField(default=0, verbose_name='排序')),
                ('metadata', models.JSONField(blank=True, default=dict, verbose_name='扩展数据')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='rules.rulecategory', verbose_name='父分类')),
            ],
            options={
                'verbose_name': '规则分类',
                'verbose_name_plural': '规则分类',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('title', models.CharField(max_length=200, verbose_name='标题')),
                ('slug', models.SlugField(max_length=220, unique=True, verbose_name='规则标识')),
                ('summary', models.TextField(blank=True, default='', verbose_name='摘要')),
                ('content', models.TextField(blank=True, default='', verbose_name='可渲染正文')),
                ('content_blocks', models.JSONField(blank=True, default=list, verbose_name='结构化正文')),
                ('raw_data', models.JSONField(blank=True, default=dict, verbose_name='原始数据')),
                ('rule_type', models.CharField(choices=[('profession', '专修'), ('divine_art', '神术'), ('story_rule', '故事运作'), ('attribute', '属性系统'), ('other', '其他')], default='other', max_length=50, verbose_name='规则类型')),
                ('chapter_ref', models.CharField(blank=True, default='', max_length=50, verbose_name='章节号')),
                ('source', models.CharField(blank=True, default='core', max_length=50, verbose_name='来源')),
                ('version_status', models.CharField(blank=True, default='', max_length=50, verbose_name='版本状态')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('published', '已发布')], default='published', max_length=20, verbose_name='发布状态')),
                ('sort_order', models.IntegerField(default=0, verbose_name='排序')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rules', to='rules.rulecategory', verbose_name='分类')),
            ],
            options={
                'verbose_name': '规则条目',
                'verbose_name_plural': '规则条目',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='rule',
            index=models.Index(fields=['rule_type', 'status'], name='rules_rule_rule_ty_0ca4df_idx'),
        ),
        migrations.AddIndex(
            model_name='rule',
            index=models.Index(fields=['slug'], name='rules_rule_slug_c9c44e_idx'),
        ),
    ]
