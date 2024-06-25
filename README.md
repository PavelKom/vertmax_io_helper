# vertmax_io_helper

![VIOH_pic1](https://github.com/PavelKom/vertmax_io_helper/assets/24871615/08cb8708-8724-45ca-b6c6-fcc820450c89)

# EN
Script for simplifying debugging of CNC Intermac Vertmax using PLC2.exe
At the first launch, a *json*-config is generated, which pulls in data on the **inputs** (*oem_msd_in.dat.ini*) and **outputs** (*oem_msd_out.dat.ini*) of the CNC, allowing you to add a description and divide them into groups later. Please note that when generating a *json*-config, the current **input**/**output** addresses are also inserted, but they are not taken into account by the script and are only needed to simplify editing the config. An *ini*-config is also generated, which specifies the **paths** to the *oem*-files, the **name** of the current *json*-config (useful for localization), and the **console command** for quickly launching PLC2.exe (written manually)
## Interface:
1. Selection of the displayed group (spindles, carriages, etc.).
2. Input table. Alias, description, current address. Double-clicking on a line enters its address into PLC2.exe.
3. Output table. Similar to the input table.
4. Pointer to the current input slot for PLC2.exe. The **CLEAR** button clears the selected slot.
5. Hiding ports with the address **-1**.
6. Quick launch button for PLC2.exe if it is not running (configured in the *ini*-config).

# RU
Скрипт для упрощения отладки ЧПУ Intermac Vertmax при помощи PLC2.exe
При первом запуске генерируется *json*-конфиг в который подтягиваются данные по **входам** (*oem_msd_in.dat.ini*) и **выходам** (*oem_msd_out.dat.ini*) станка, позволяя в дальнейшем добавить им описание и разбить на группы. Учтите, при генерации *json*-конфига также вставляются текущие адреса **входов**/**выходов**, но они не учитываются скриптом и нужны только для того, чтобы упростить редактирование конфига. Так-же генерируется *ini*-конфиг, в котором указываются **пути** к *oem*-файлам, **имя** текущего *json*-конфига (полезно при локализации) и **консольная команда** для быстрого запуска PLC2.exe (прописывается вручную)
## Интерфейс:
1. Выбор отображаемой группы (шпиндели, каретки и т.д.).
2. Таблица входов. Алиас, описание, текущий адрес. Двойной щелчок по строке вносит её адрес в PLC2.exe.
3. Таблица выходов. Аналогично таблице входов.
4. Указатель на текущий слот ввода для PLC2.exe. Кнопка **CLEAR** очищается выбранный слот.
5. Сокрытие портов с адресом **-1**.
6. Кнопка быстрого запуска PLC2.exe если он не запущен (настраивается в *ini*-конфиге).

# Used libraries | Используемые библиотеки:
* [python-xlib](https://github.com/python-xlib/python-xlib) - Доступ к интерфейсу PLC2.exe, эмуляция нажатия клавиш | Access to PLC2.exe interface, keystroke emulation
* [pygubu](https://github.com/alejandroautalan/pygubu) - Библиотека для парсинга **xml** в **tkinter** интерфейс, созданного при помощи [pygubu-designer](https://github.com/alejandroautalan/pygubu-designer) | Library for parsing **xml** into **tkinter** interface created with [pygubu-designer](https://github.com/alejandroautalan/pygubu-designer)
