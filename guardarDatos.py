from datetime import *


def guardarResp(respuestas):
    cadena = ""
    archivo = open('personas.csv', 'a')
    delta1 = timedelta(hours=6)
    delta2 = timedelta(hours=4)

    today = datetime.today()-delta1
    vence = datetime.now()-delta2

    d1 = today.strftime("%d/%m/%Y")
    t1 = today.strftime("%H:%M:%S")
    t2 = vence.strftime("%H:%M:%S")

    for x in respuestas:

        cadena = cadena+x+","

    cadena = cadena+d1+","+t1+","+t2+"\n"
    archivo.write(cadena)
    archivo.close()
    return cadena
