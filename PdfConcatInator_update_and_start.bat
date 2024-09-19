@Echo off
chcp 65001 >nul
echo Проверка обновлений и запуск...
net use X: \\srsfemida\1$\reference_clients\PdfConcatInator\ /persistent:no
if %errorlevel% neq 0 (
    echo Ошибка: Не удалось подключить сетевой диск.
) else (
    echo Сетевой диск подключен успешно.
    echo Обновление файлов...
    xcopy X:\ /D /E /Y >nul
    if %errorlevel% neq 0 (
        echo Ошибка: Не удалось скопировать файлы.
    ) else (
        echo Файлы успешно обновлены.
    )
    echo Проверка завершена...
    net use /delete X: /YES
)

echo Запуск PdfConcatInator.exe...
start PdfConcatInator.exe
@exit