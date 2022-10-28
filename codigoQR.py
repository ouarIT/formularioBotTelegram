import qrcode
from os import remove

def crearImagenQR(textoQR, nombreArchivo):
    #Se crea el codigo qr
    try:
        img = qrcode.make(textoQR)
        img.save("{}.png".format(nombreArchivo))
        return "{}.png".format(nombreArchivo)
        
    except:
        pass

def enviarCodigoQR(textoQR, nombreArchivo, usuarioid, bot):
    PHOTO_PATH = crearImagenQR(textoQR, nombreArchivo)
    
    try:
        bot.send_photo(chat_id = usuarioid, photo=open(PHOTO_PATH, 'rb'))
        
    except:
        pass
    
    remove(PHOTO_PATH)