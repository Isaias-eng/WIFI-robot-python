import network
import socket
from machine import Pin, PWM
import time

# Configuração dos pinos dos motores
motorEsqFrente = PWM(Pin(15))  # Motor esquerdo frente
motorEsqTras = PWM(Pin(14))    # Motor esquerdo trás
motorDirFrente = PWM(Pin(16))  # Motor direito frente
motorDirTras = PWM(Pin(17))    # Motor direito trás

# Frequência PWM dos motores (ajustar conforme necessário)
motorEsqFrente.freq(1000)
motorEsqTras.freq(1000)
motorDirFrente.freq(1000)
motorDirTras.freq(1000)

# Configuração de velocidade
velocidade = 65535  # Valor máximo de velocidade

# Funções para controle dos motores
def avancar():
    motorEsqFrente.duty_u16(velocidade)
    motorEsqTras.duty_u16(0)
    motorDirFrente.duty_u16(velocidade)
    motorDirTras.duty_u16(0)

def recuar():
    motorEsqFrente.duty_u16(0)
    motorEsqTras.duty_u16(velocidade)
    motorDirFrente.duty_u16(0)
    motorDirTras.duty_u16(velocidade)

def girar_esquerda():
    motorEsqFrente.duty_u16(0)
    motorEsqTras.duty_u16(velocidade)
    motorDirFrente.duty_u16(velocidade)
    motorDirTras.duty_u16(0)

def girar_direita():
    motorEsqFrente.duty_u16(velocidade)
    motorEsqTras.duty_u16(0)
    motorDirFrente.duty_u16(0)
    motorDirTras.duty_u16(velocidade)

def parar():
    motorEsqFrente.duty_u16(0)
    motorEsqTras.duty_u16(0)
    motorDirFrente.duty_u16(0)
    motorDirTras.duty_u16(0)

# Função para configurar a rede Wi-Fi
ssid = 'DELTA_FIBRA_SERGIO CASA'
password = 'sergio1974#'

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
    print('Conectado:', wlan.ifconfig())
    return wlan.ifconfig()[0]

# Função para criar a interface web com melhorias
def criar_website():
    html = """
    <html>
    <head>
        <title>Controle do Carro via Wi-Fi</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                text-align: center;
                padding: 20px;
            }
            h1 {
                color: #333;
            }
            button {
                font-size: 20px;
                padding: 10px 20px;
                margin: 10px;
                cursor: pointer;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                outline: none;
            }
            button:hover {
                background-color: #45a049;
            }
            #speedControl {
                margin-top: 20px;
                width: 80%;
            }
            #speedLabel {
                margin-top: 20px;
                font-size: 18px;
            }
        </style>
        <script>
            function sendCommand(command) {
                fetch("/" + command)
                    .then(response => response.text())
                    .then(data => {
                        console.log(data);  // Apenas para debugar no console
                    });
            }

            function updateSpeedLabel(value) {
                document.getElementById('speedLabel').innerText = "Velocidade: " + value;
                fetch("/set_speed?value=" + value);
            }
        </script>
    </head>
    <body>
        <h1>Controle do Carro</h1>
        <button onclick="sendCommand('avancar')">Avançar</button><br>
        <button onclick="sendCommand('recuar')">Recuar</button><br>
        <button onclick="sendCommand('esquerda')">Girar Esquerda</button><br>
        <button onclick="sendCommand('direita')">Girar Direita</button><br>
        <button onclick="sendCommand('parar')">Parar</button><br>

        <div id="speedControl">
            <input type="range" id="speedRange" min="0" max="65535" value="65535" oninput="updateSpeedLabel(this.value)">
            <p id="speedLabel">Velocidade: 65535</p>
        </div>
    </body>
    </html>
    """
    return html

# Função do servidor web
def iniciar_servidor(ip):
    addr = socket.getaddrinfo(ip, 8080)  # Usando a porta 8080
    s = socket.socket()
    s.bind(addr[0][-1])
    s.listen(1)
    print('Servidor iniciado em:', ip)

    while True:
        cl, addr = s.accept()
        print('Conexão de', addr)
        request = cl.recv(1024)
        request = str(request)
        print('Requisição:', request)

        # Comandos para controlar os motores
        if '/avancar' in request:
            avancar()
            resposta = "Avançando... <a href='/'>Voltar</a>"
        elif '/recuar' in request:
            recuar()
            resposta = "Recuando... <a href='/'>Voltar</a>"
        elif '/esquerda' in request:
            girar_esquerda()
            resposta = "Girando para a esquerda... <a href='/'>Voltar</a>"
        elif '/direita' in request:
            girar_direita()
            resposta = "Girando para a direita... <a href='/'>Voltar</a>"
        elif '/parar' in request:
            parar()
            resposta = "Parando... <a href='/'>Voltar</a>"
        elif '/set_speed' in request:
            global velocidade
            velocidade = int(request.split('=')[1].split(' ')[0])
            resposta = "Velocidade ajustada para " + str(velocidade) + " <a href='/'>Voltar</a>"
        else:
            resposta = criar_website()

        cl.send('HTTP/1.1 200 OK\r\n')
        cl.send('Content-Type: text/html\r\n\r\n')
        cl.send(resposta)
        cl.close()

# Configuração inicial
def setup():
    ip = conectar_wifi()
    iniciar_servidor(ip)

# Rodar o código
setup()

