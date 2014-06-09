Convert
=========

Convert is a command line program for the Raspberry Pi.   
Converts all video format to h264 with a maximum resolution of 1280x720.   
You can configure arbitrarily to "bin\convert.py" file.  
  
Compatibility: WinXP SP1+, Win7(x86,x64), Win8(x86,x64)  


Downloading Convert
---------------------
    
    https://github.com/hitman249/convert/archive/master.zip
	
	or
	
    git clone https://github.com/hitman249/convert.git


Using Convert
---------------

Copy video files to folder "\in\".  
Start "convert.bat" for convert.  
Open the folder "\out\" to take back convert files.  




Russian
---------

Программа для проверки и приведению к стандарту 720p видеофайлов проигрываемых на Raspberry Pi.


Инструкция:  
1) Скопировать видео файлы в папку "in".  
2) Запустить файл convert.bat  
3) Забрать стандартизированные файлы в папке "out".  



Багфикс:  

Версия 0.4
+ Добавлен отладчик
+ Добавлена поддержка кириллицы в путях к программе.
+ Добавлен небольшой фикс для кириллицы в именах файлов.

Версия 0.3
+ Добавлена более тонкая проверка видео файлов.
+ Исправлена ошибка при чтении имён файлов содержащих символы кириллицы.