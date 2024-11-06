для создания функции замены лица испольвазалсь библиотека: AI.ComputerVision.DeepFake<br />
для создния телеграм бота использовались библиотеки: pyTelegramBotAPI, python-telegram, os, json, subprocess, Pillow<br />
инструкция запуска:
1) установить репозиторий как zip и разархивировать
2) открыть TestApp.sln 
3) добавить ссылки (FaceReplace->dlls) *при ошибке нажать ОК, на функционал это не повлияет
4) из FaceReplace->bin->Debug извлечь все файлы в папку, где находится test.py
5) из FaceReplace перенести shape_predictor_68_face_landmarks.dat в папку, где находится test.py
6) открыть CMD, ввести данные команды:
pip install pyTelegramBotAPI
pip install Pillow
7) адаптировать код, под свои данные (токен, айди чата поддержки, айди канала)
8) запустить test.py
