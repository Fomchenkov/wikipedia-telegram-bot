#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import time

import wikipedia
import telebot
from telebot import types

import config


class Wikipedia:
	"""
	Wikipedia functions collection
	"""
	@staticmethod
	def get_random_page(lang="ru"):
		"""
		Get random Wikipedia page
		"""
		while True:
			try:
				wikipedia.set_lang(lang)
				res = wikipedia.random(pages=1)
				return wikipedia.page(res)
			except wikipedia.exceptions.DisambiguationError:
				continue

	@staticmethod
	def find_page(title, lang="ru"):
		"""
		Find Wikipedia page
		"""
		wikipedia.set_lang(lang)
		results = wikipedia.search(title)
		for res in results:
			try:
				yield wikipedia.page(res)
			except wikipedia.exceptions.DisambiguationError:
				continue


def generate_main_markup():
	"""
	Generate start markup
	"""
	markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
	markup.add(types.KeyboardButton("🔎 Поиск статей"))
	markup.add(types.KeyboardButton("👀 Случайная статья"))
	return markup


bot = telebot.TeleBot(config.BOT_TOKEN)

ready_to_find = []


@bot.message_handler(commands=['start'])
def start_command(message):
	uid = message.from_user.id
	cid = message.chat.id
	text = "Привет! Я бот. Я создан для взаимодействия с Википедией."
	markup = generate_main_markup()
	return bot.send_message(cid, text, reply_markup=markup)


@bot.message_handler(commands=['author'])
def author_command(message):
	text = "Бот разработан в Kronver.\nРазработчик: @fomchenkov_v"
	return bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def text_handler(message):
	uid = message.from_user.id
	cid = message.chat.id

	bot.send_chat_action(cid, 'typing')

	# Handle find article request
	if uid in ready_to_find:
		sended = False
		for page in Wikipedia.find_page(message.text):
			text = page.title + "\n" + page.url 
			bot.send_message(cid, text)
			sended = True
		if not sended:
			text = "Нет найденых статей."
			bot.send_message(cid, text)
		ready_to_find.remove(uid)
		return

	# Handle keyboard buttons
	if message.text == "🔎 Поиск статей":
		text = "Введите ключевое слово для поиска статьи"
		ready_to_find.append(uid)
		return bot.send_message(cid, text)
	elif message.text == "👀 Случайная статья":
		page = Wikipedia.get_random_page()
		text = page.title + "\n" + page.url 
		return bot.send_message(cid, text)


def main():
	while True:
		try:
			bot.polling(none_stop=True)
		except KeyboardInterrupt as e:
			break
		except Exception as e:
			time.sleep(30)


if __name__ == '__main__':
	main()
