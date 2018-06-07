from django.db import models


class MoscowPythonMeetup(models.Model):

	class Meta:
		verbose_name_plural = "MoscowPython Митапы"

	def __str__(self):
		return f'MoscowPython Meetup № {self.meetup_number}'

	meetup_number = models.IntegerField(
		verbose_name='Номер митапа',
		help_text='Введите номер митапа'
	)

	meetup_day = models.IntegerField(
		verbose_name='День Митапа',
		help_text='День месяца, в который будет митап'
	)

	months_list = [
		('Января', 'Январь'),
		('Февраля', 'Февраль'),
		('Марта', 'Март'),
		('Апреля', 'Апрель'),
		('Мая', 'Май'),
		('Июня', 'Июнь'),
		('Июля', 'Июль'),
		('Августа', 'Август'),
		('Сентября', 'Сентябрь'),
		('Октября', 'Октябрь'),
		('Ноября', 'Ноябрь'),
		('Декабря', 'Декабрь')
	]

	meetup_month = models.TextField(
		choices=months_list,
		default='Январь',
		verbose_name='Месяц Митапа',
		help_text='Месяц, в котором будет проходить митап'
	)

	meetup_time = models.TimeField(
		blank=True,
		auto_now=True,
		verbose_name='Время Митапа',
		help_text='Время начала митапа'
	)

	meetup_link = models.URLField(
		verbose_name='Ссылка на митап',
		default='http://www.moscowpython.ru',
		help_text='Ссылка по стандарту, можно менять'
	)


class LearnPythonCourse(models.Model):
	class Meta:
		verbose_name_plural = "LearnPython Наборы"

	def __str__(self):
		return f'LearnPython Набор № {self.course_index}'

	course_index = models.IntegerField(
		verbose_name='Набор №',
		help_text='Порядковый номер набора'
	)

	course_start_date = models.DateField(
		verbose_name='Дата начала курса',
		help_text='Дата первого занятия'
	)

	course_end_date = models.DateField(
		verbose_name='Дата окончания курса',
		help_text='Дата последнего занятия',
	)

	end_registration_date = models.DateTimeField(
		verbose_name='Дата закрытия регистрации',
		help_text='Во сколько закрывается регистрация?',
		default=None,

	)


class LearnPythonCoursePrices(models.Model):
	class Meta:
		verbose_name_plural = 'LearnPython Цены на курсы'

	def __str__(self):
		return f'Интервал {self.price_range} на {self.course_type}'

	price_range = models.IntegerField(
		verbose_name='Название временного отрезка',
		help_text='Мустанг / Гепард / Панда и вот это все',
		default=None
	)

	course_type = [
		('Online', 'Online'),
		('Offline', 'Offline')
	]

	course_type = models.TextField(
		choices=course_type,
		verbose_name='Тип курса',
		help_text='Выберите тип курса'
	)

	price_range_end_date = models.DateField(
		verbose_name='Дата окончания интервала',
		help_text='Когда истекает данное предложение'
	)

	price_range_price = models.IntegerField(
		verbose_name='Цена',
		help_text='Сколько стоит курс в этот период'
	)


class Courators(models.Model):
	class Meta:
		verbose_name_plural = 'LearnPython Кураторы'

	def __str__(self):
		return f'Куратор {self.curator_name}'

	curator_name = models.CharField(
		max_length=50,
		verbose_name='Имя и фамилия куратора',
		help_text='Сначало имя, потом фамилия'
	)

	curator_bio = models.TextField(
		verbose_name='Биография куратора',
		help_text='Где и кем работает, что программирует'
	)

	curator_motto = models.CharField(
		max_length=150,
		verbose_name='Девиз куратора',
		help_text='Через тернии к звездам или что-нибудь такое'
	)

	curator_photo = models.ImageField(
		help_text='Фотография куратора',
		verbose_name='Фото куратора'
	)

	courator_status = models.BooleanField(
		verbose_name="Куратор для ближайшего набора?",
		help_text='Куратор работает в текущем наборе?',
		default=True
	)

	courator_github = models.URLField(
		blank=True,
		help_text='Ссылка на гит-хаб куратора',
		verbose_name='GitHub куратора'
	)

	courator_social_network = models.URLField(
		blank=True,
		help_text='Если есть, ссылка на соцсеточку',
		verbose_name='Соцсеточка куратора'
	)


class Feedback(models.Model):
	class Meta:
		verbose_name_plural = "LearnPython Отзывы"

	def __str__(self):
		return f'Отзыв участника {self.feedback_author}'

	feedback_author = models.CharField(
		verbose_name='Автор отзыва',
		help_text='Кто автор отзыва?',
		max_length=50,
		null=True
	)

	feedback_author_link = models.URLField(
		verbose_name='Ссылка на автора',
		help_text='Есть ли ссылка на соцсеточки автора?',
		blank=True,
		null=True
	)

	feedback_author_position = models.CharField(
		verbose_name='Должность выпускника',
		help_text='Кем работает автор?',
		max_length=50,
		null=True
	)

	feedback_author_photo = models.ImageField(
		verbose_name='Фотография автора',
		help_text='Прикрепите фото автора отзыва',
		null=True
	)

	feedback_text = models.TextField(
		verbose_name='Текст отзыва',
		help_text='А сюда пишем отзыв автора',
		null=True
	)


class GraduateStories(models.Model):
	class Meta:
		verbose_name_plural = 'Learn Python Истории учеников'

	def __str__(self):
		return f'История участника {self.story_author}'

	story_author = models.CharField(
		verbose_name='Автор истории',
		help_text='Как зовут автора истории?',
		max_length=50,
		null=True
	)

	story_author_photo = models.ImageField(
		verbose_name='Фотография автора',
		help_text='Прикрепите фото автора истории',
		null=True
	)

	story_author_position = models.CharField(
		verbose_name='Должность выпускника',
		help_text= 'Кто теперь выпускник',
		max_length=50,
		null=True
	)

	story_author_background = models.CharField(
		verbose_name='В прошлом автор был:',
		help_text='Прим. "В прошлом: терапевт"',
		max_length=150
	)

	story_text = models.TextField(
		verbose_name='История пользователя',
		help_text='Что хотел бы автор рассказать',
		default=None
	)


class GraduateProjects(models.Model):
	class Meta:
		verbose_name_plural = 'LearnPython Проекты Учеников'

	def __str__(self):
		return f'Проект "{self.project_name}"'

	project_name = models.CharField(
		max_length=150,
		help_text='Название проекта',
		default=None
	)

	project_image = models.ImageField(
		help_text="Пример интерфейса проекта",
		default=None
	)
