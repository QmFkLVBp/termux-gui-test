from termuxgui import Activity, Button, View

with Activity() as a:
    # Створюємо кнопку
    btn = Button(a, "Привіт, світ!")
    # Показуємо вікно
    a.run()
