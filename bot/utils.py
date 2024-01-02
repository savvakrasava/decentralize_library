# bot/utils.py
from telegram import ReplyKeyboardRemove

def hide_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
