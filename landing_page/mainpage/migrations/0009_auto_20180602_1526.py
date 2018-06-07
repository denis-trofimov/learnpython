# Generated by Django 2.0.5 on 2018-06-02 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainpage', '0008_auto_20180526_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='feedback_author_link',
            field=models.URLField(blank=True, null=True, verbose_name='Ссылка на автора'),
        ),
        migrations.AlterField(
            model_name='learnpythoncourse',
            name='course_end_date',
            field=models.DateField(help_text='Дата последнего занятия', verbose_name='Дата окончания курса'),
        ),
        migrations.AlterField(
            model_name='learnpythoncourse',
            name='course_index',
            field=models.IntegerField(help_text='Порядковый номер набора', verbose_name='Набор №'),
        ),
        migrations.AlterField(
            model_name='learnpythoncourse',
            name='course_start_date',
            field=models.DateField(help_text='Дата первого занятия', verbose_name='Дата начала курса'),
        ),
        migrations.AlterField(
            model_name='learnpythoncourse',
            name='online_gepard_due_date',
            field=models.DateField(help_text='До какого срока эта цена действительна?', verbose_name='"Гепард" (Онлайн) действительна до'),
        ),
        migrations.AlterField(
            model_name='learnpythoncourse',
            name='online_gepard_price',
            field=models.IntegerField(help_text='Сколько стоит Гепард (Онлайн)?', verbose_name='Цена "Гепард" (Онлайн)'),
        ),
        migrations.AlterField(
            model_name='learnpythoncourse',
            name='online_mustang_due_date',
            field=models.DateField(help_text='До какого срока эта цена действительна?', verbose_name='"Мустанг" (Онлайн) действительна до'),
        ),
        migrations.AlterField(
            model_name='learnpythoncourse',
            name='online_mustang_price',
            field=models.IntegerField(help_text='Сколько стоит Мустанг (Онлайн)', verbose_name='Цена "Мустанг" (Онлайн)'),
        ),
        migrations.AlterField(
            model_name='learnpythoncourse',
            name='online_panda_due_date',
            field=models.DateField(help_text='До какого срока эта цена действительна?', verbose_name='"Панда" (Онлайн) действительна до'),
        ),
        migrations.AlterField(
            model_name='learnpythoncourse',
            name='online_panda_price',
            field=models.IntegerField(help_text='Сколько стоит Панда (Онлайн)', verbose_name='Цена "Панда" (Онлайн)'),
        ),
        migrations.AlterField(
            model_name='moscowpythonmeetup',
            name='meetup_day',
            field=models.IntegerField(help_text='День месяца, в который будет митап', verbose_name='День Митапа'),
        ),
        migrations.AlterField(
            model_name='moscowpythonmeetup',
            name='meetup_month',
            field=models.TextField(choices=[('Января', 'Январь'), ('Февраля', 'Февраль'), ('Марта', 'Март'), ('Апреля', 'Апрель'), ('Мая', 'Май'), ('Июня', 'Июнь'), ('Июля', 'Июль'), ('Августа', 'Август'), ('Сентября', 'Сентябрь'), ('Октября', 'Октябрь'), ('Ноября', 'Ноябрь'), ('Декабря', 'Декабрь')], default='Январь', help_text='Месяц, в котором будет проходить митап', verbose_name='Месяц Митапа'),
        ),
        migrations.AlterField(
            model_name='moscowpythonmeetup',
            name='meetup_number',
            field=models.IntegerField(help_text='Введите номер митапа', verbose_name='Номер митапа'),
        ),
        migrations.AlterField(
            model_name='moscowpythonmeetup',
            name='meetup_time',
            field=models.TimeField(auto_now=True, help_text='Время начала митапа', verbose_name='Время Митапа'),
        ),
    ]
