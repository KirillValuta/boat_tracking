import tkinter as tk


def window_create():
    # создание окна
    window = tk.Tk()

    # создание виджета для вывода текста
    text_widget = tk.Text(window)
    text_widget.pack()
    # запуск главного цикла окна
    window.mainloop()

# # функция для обновления текста
# def update_text(window, text_widget):
#     text_widget.insert(tk.END, "gg")
#     text_widget.insert(tk.END, "Новая информация\n")
#     text_widget.insert(tk.END, "Новая информация\n")
#     text_widget.see(tk.END)  # прокрутка виджета до конца
#     window.after(1000, update_text)  # вызов функции через 1000 миллисекунд
#
# # вызов функции для первоначального добавления текста
# update_text()

