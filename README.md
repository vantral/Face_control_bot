# Телеграм-бот Face Control

Телеграм-бот называется **@blacksquare_bot**.
Бот умеет:
* закрывать рандомное лицо на фотографии
(с помощью нейросети из библиотеки opencv-python) и подписывать
под закрытым лицом (не)смешное слово
* писать на фотографии рандомный текст, сгенерированный марковской цепью, обученной на текстах Агнии Барто
(краулер, собирающий тексты находится в папке *crawlers*)
* писать на фотографии текст, полученный от пользователя
* выдавать рандомное предсказание, сгенерированное марковской цепью,
обученной на текстах гороскопов (краулер, собирающий тексты находится в папке *crawlers*)

В корневой директории находятся:
* файл **README**
* папка *model_data* с файлами нейорсети
* файл **3952.ttf** с шрифтом *Lobster 1.4 Regular*
* файлы **barto.json, list_for_models.json** для обучения марковских цепей.
В первом файле лежит строка с текстам Агнии Барто, во втором -- список
текстов гороскопов
* Служебные файлы **Procfile, requirements.txt, runtime.txt**, необходимые для запуска бота на вебхуках

В репозитории отсутсвует файл **conf.py** с токеном бота.