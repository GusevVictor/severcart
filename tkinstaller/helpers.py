#!/usr/bin/env python
# -*- coding:utf-8 -*-


def tr(msgid, lang='en'):
    """Простейшая функция по локализации текстовых строк
    """
    ru_lang_dict = {
       'Press any key to exit ...': 'Для выхода нажмите любую клавишу...',
       'Further continuation impossible, Python version 3.4.4 is not equal.' :'Дальнейшее продолжение невозможно, версия Python не равна 3.4.4.',
       'Installing Severcart are not available for the platform.': 'Установка Severcart для данной платформы не предусмотрена.',
       '---Generation of signature key session variable--': '--Генерация ключа подписи сессионной переменной--',
       '-------Installation package dependencies---------': '--------Установка пакетов зависимостей-----------',
       'Installation package dependencies for 64-bit Windows': 'Установка пакетов зависимостей для 64 битной Windows',
       'Installation package dependencies for 32-bit Windows': 'Установка пакетов зависимостей для 32 битной Windows',
       'Installation package dependencies for Linux': 'Установка пакетов зависимостей для Linux',
       'Support for this architecture is not implemented.': 'Поддержка данной архитиктуры не релизована.',
       'Further continuation of the installation is not possible!': 'Дальнейшее продолжение установки невозможно!',
       '--Generation of signature key session variable---': '--Генерация ключа подписи сессионной переменной--',
       '--------------The migration scheme---------------': '-----------------Миграция схемы------------------',
        'During migration, an error occurred.': 'В процессе миграции произошла ошибка.',
        'The scheme was successfully migrated.': 'Схема успешно мигрирована.',
        '-----------------Creating a user-----------------': '--------------Создание пользователя--------------',
        'Enter your username: ': 'Ввведите имя пользователя: ',
        'This user name already exists. Re-enter. ': 'Пользователь с таким именем уже существует. Повторите ввод.',
        'Enter password:   ': 'Введите пароль:   ',
        'Confirm password: ': 'Повторите пароль: ',
        'The user was created successfully.': 'Пользователь успешно создан.',
        'Passwords do not match. Re-enter. ': 'Пароли не совпадают. Повторите ввод.',
        '------------Installation successful--------------': '----------Установка успешно завершена------------',
        'Done.': 'Выполнено.',
    } 

    if lang == 'ru':
        return  ru_lang_dict.get(msgid)
    else:
        return msgid 

"""
-------------------------------------------------


"""
