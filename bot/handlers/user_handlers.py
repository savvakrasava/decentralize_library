
def start(update, context):
    update.message.reply_text('Привет! Я библиотечный бот и мазафакер. Введите /help для списка команд.')

def help(update, context):
    update.message.reply_text('/borrow - взять книгу\n/confirm_borrow - подтвердить бронирование\n/addbook - добавить книгу\n/workinghours - узнать рабочие часы офлайн библиотки\n/showcatalog - показать книжный каталог\n/showmybookings - показать мои бронирования\n/read_description - прочитать описание книги')

def working_hours(update, context):
    update.message.reply_text('Библиотека работает для поситителей с 15:00 до 15:30 ежедневно.')
