import guardarDatos
import codigoQR
import logging
import telegram
from telegram import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# token de tu chat de telegram
TELEGRAM_BOT_TOKEN = ''
# chat id
TELEGRAM_CHAT_ID = ''

FRASE_AUTORIZACION = 'Estoy de acuerdo'

PREGUNTAS = ['¿Tiene fiebre?',
             '¿Tiene tos?',
             '¿Siente dolor de cabeza?',
             '¿Tiene malestar general: dolor muscular y/o de articulaciones?',
             '¿Tiene tos y/o estornudos?',
             '¿Tiene catarro?',
             '¿Ha estado en contacto con algun paciente diagnosticado con Covid-19?']

usuarios = {}

bot = telegram.Bot(TELEGRAM_BOT_TOKEN)

KB_OPCIONES = [
    [
        InlineKeyboardButton("Sí", callback_data='1'),
        InlineKeyboardButton("No", callback_data='0'),
    ],
]

KB_TIPO_USUARIO = [
    [
        InlineKeyboardButton("Externo", callback_data='0'),
        InlineKeyboardButton("Personal", callback_data='1'),
    ], [InlineKeyboardButton("Alumno", callback_data='2')]
]

KB_CARRERAS = [
    [
        InlineKeyboardButton("ITI", callback_data='0'),
        InlineKeyboardButton("ITMA", callback_data='1'),
    ], [
        InlineKeyboardButton("ISTI", callback_data='2'),
        InlineKeyboardButton("ITEM", callback_data='3'),
    ], [
        InlineKeyboardButton("LAG", callback_data='4'),
        InlineKeyboardButton("LMI", callback_data='5'),
    ]
]

KB_AREAS = [
    [
        InlineKeyboardButton("Tesoreria", callback_data='0'),
        InlineKeyboardButton("Cafeteria", callback_data='1'),
    ], [
        InlineKeyboardButton("CNT", callback_data='2'),
        InlineKeyboardButton("Otro", callback_data='3'),
    ]
]

KB_PERSONAL = [
    [
        InlineKeyboardButton("Docente", callback_data='0'),
    ], [
        InlineKeyboardButton("Administrativo", callback_data='1'),
    ]
]

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def miembros(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "ingresa tu nombre"
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "Usa /start para recibir un saludo\nUsa /formulario para iniciar el cuestionario de ingreso\nUsa /miembros para saber quienes estan destrás de este bot :D"
    )


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    update.message.reply_markdown_v2(
        fr'Hola {user.mention_markdown_v2()}\! Usa /help para obtener ayuda',
    )


def formulario(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    uid = user.id
    usuarios.setdefault(user.id, [[], []])

    usuarios[uid][0].clear()
    usuarios[uid][1].clear()
    usuarios[uid][1].append(1)
    update.message.reply_text(
        'Escriba "{}" para prometer total responsabilidad y honestidad al responder este formulario'.format(
            FRASE_AUTORIZACION)
    )


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    user = update.effective_user
    uid = user.id

    query = update.callback_query

    query.answer()

    usuarios[uid][0].append(query.data)

    if len(usuarios[uid][0]) == 1 and len(usuarios[uid][1]) == 1:

        # opcion cuando son externos
        if usuarios[uid][0][0] == '0':
            reply_markup = InlineKeyboardMarkup(KB_AREAS)
            query.edit_message_text(
                "Area a visitar", reply_markup=reply_markup)
            usuarios[uid][1].append(1)
        # opcion cuando son personal
        elif usuarios[uid][0][0] == '1':
            reply_markup = InlineKeyboardMarkup(KB_PERSONAL)
            query.edit_message_text(
                "Tipo de personal", reply_markup=reply_markup)
            usuarios[uid][1].append(1)

        # opcion cuando son estudiantes
        elif usuarios[uid][0][0] == '2':
            reply_markup = InlineKeyboardMarkup(KB_CARRERAS)
            query.edit_message_text(
                "Carrera del estudiante", reply_markup=reply_markup)
            usuarios[uid][1].append(1)
    else:
        # se solicita matricula o id
        if usuarios[uid][0][0] != '0' and len(usuarios[uid][1]) < 3:
            query.edit_message_text(
                text=f"Ingrese su matricula o numero de empleado: ")
            usuarios[uid][1].append(1)

        elif len(usuarios[uid][0]) == len(PREGUNTAS)+len(usuarios[uid][1]):
            query.edit_message_text(text=f"Ingrese su nombre completo: ")
        else:
            reply_markup = InlineKeyboardMarkup(KB_OPCIONES)
            query.edit_message_text(
                PREGUNTAS[len(usuarios[uid][0])-len(usuarios[uid][1])], reply_markup=reply_markup)


def answer_command(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    uid = user.id
    try:
        if len(usuarios[uid][0]) == 0 and len(usuarios[uid][1]) == 1:
            respuestaUsuario = update.message.text
            if (respuestaUsuario == FRASE_AUTORIZACION):
                reply_markup = InlineKeyboardMarkup(KB_TIPO_USUARIO)
                update.message.reply_text(
                    '¿Tipo de usuario?', reply_markup=reply_markup)
                return
            else:
                update.message.reply_text(
                    "La frase no se ha ingresado correctamente. Verifique la frase y vuelva a solicitar /formulario"
                )
                return
        if len(usuarios[uid][0]) < 3 and len(usuarios[uid][1]) == 3:
            respuestaUsuario = update.message.text
            usuarios[uid][0].append(respuestaUsuario)
            reply_markup = InlineKeyboardMarkup(KB_OPCIONES)

            update.message.reply_text(
                PREGUNTAS[len(usuarios[uid][0])-len(usuarios[uid]
                                                    [1])], reply_markup=reply_markup
            )
        elif len(usuarios[uid][0]) == len(PREGUNTAS)+len(usuarios[uid][1]):
            nombreUsuario = update.message.text
            usuarios[uid][0].append(nombreUsuario)
            datosUser = guardarDatos.guardarResp(usuarios[uid][0])
            codigoQR.enviarCodigoQR(datosUser, user.id, user.id, bot)
            usuarios.pop(uid)

        else:
            update.message.reply_text(
                "Puedes usar /help para ver las opciones que cuenta el bot"
            )
    except:
        pass


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("formulario", formulario))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("miembros", miembros))
    # Agegue esto para guardar el ID

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, answer_command))

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
