import network
import socket
from machine import Pin, PWM
import time

# Configuração dos pinos dos motores (L298N)
motor1_in1 = Pin(15, Pin.OUT)  # IN1 (motor 1)
motor1_in2 = Pin(14, Pin.OUT)  # IN2 (motor 1)
motor2_in3 = Pin(16, Pin.OUT)  # IN3 (motor 2)
motor2_in4 = Pin(17, Pin.OUT)  # IN4 (motor 2)

# Pinos de controle PWM
pwm_motor1 = PWM(Pin(18))  # ENA (controle PWM Motor 1)
pwm_motor2 = PWM(Pin(19))  # ENB (controle PWM Motor 2)

# Frequência do PWM (ajustável)
pwm_motor1.freq(1000)
pwm_motor2.freq(1000)

# Velocidade dos motores (ajustável de 0 a 65535)
velocidade = 65535  # valor máximo para velocidade (100%)

# Configuração do LED indicador de Wi-Fi
led_wifi = Pin(2, Pin.OUT)

# Funções de controle dos motores
def avancar():
    motor1_in1.value(1)
    motor1_in2.value(0)
    motor2_in3.value(1)
    motor2_in4.value(0)
    pwm_motor1.duty_u16(velocidade)  # Ajusta a velocidade do motor 1
    pwm_motor2.duty_u16(velocidade)  # Ajusta a velocidade do motor 2
    print("Ação: Avançando com velocidade:", velocidade)

def recuar():
    motor1_in1.value(0)
    motor1_in2.value(1)
    motor2_in3.value(0)
    motor2_in4.value(1)
    pwm_motor1.duty_u16(velocidade)  # Ajusta a velocidade do motor 1
    pwm_motor2.duty_u16(velocidade)  # Ajusta a velocidade do motor 2
    print("Ação: Recuando com velocidade:", velocidade)

def girar_esquerda():
    motor1_in1.value(0)
    motor1_in2.value(1)
    motor2_in3.value(1)
    motor2_in4.value(0)
    pwm_motor1.duty_u16(velocidade)  # Ajusta a velocidade do motor 1
    pwm_motor2.duty_u16(velocidade)  # Ajusta a velocidade do motor 2
    print("Ação: Girando para a esquerda com velocidade:", velocidade)

def girar_direita():
    motor1_in1.value(1)
    motor1_in2.value(0)
    motor2_in3.value(0)
    motor2_in4.value(1)
    pwm_motor1.duty_u16(velocidade)  # Ajusta a velocidade do motor 1
    pwm_motor2.duty_u16(velocidade)  # Ajusta a velocidade do motor 2
    print("Ação: Girando para a direita com velocidade:", velocidade)

def parar():
    motor1_in1.value(0)
    motor1_in2.value(0)
    motor2_in3.value(0)
    motor2_in4.value(0)
    pwm_motor1.duty_u16(0)  # Desativa o PWM
    pwm_motor2.duty_u16(0)  # Desativa o PWM
    print("Ação: Parando os motores")

# Configuração da rede Wi-Fi
ssid = 'DELTA_FIBRA_SERGIO CASA'
password = 'sergio1974#'

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("Tentando conectar ao Wi-Fi:", ssid)
    wlan.connect(ssid, password)

    # Piscar o LED enquanto a conexão não for estabelecida
    while not wlan.isconnected():
        led_wifi.on()   # Liga o LED
        time.sleep(0.5)  # Espera 0.5 segundos
        led_wifi.off()  # Desliga o LED
        time.sleep(0.5)  # Espera mais 0.5 segundos
        print("Tentando conectar ao Wi-Fi...")

    print("Conectado ao Wi-Fi com sucesso! IP:", wlan.ifconfig()[0])
    led_wifi.on()  # Liga o LED indicando que está conectado ao Wi-Fi
    return wlan.ifconfig()[0]

# Função para criar a interface web
def criar_website():
    html = """
    <html>
    <head>
        <title>Controle do Carro via Wi-Fi</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 20px;
            }
            button {
                font-size: 20px;
                padding: 10px;
                margin: 10px;
                cursor: pointer;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            input[type="range"] {
                width: 300px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <h1>Controle do Carro</h1>
        <button onclick="fetch('/avancar')">Avançar</button><br>
        <button onclick="fetch('/recuar')">Recuar</button><br>
        <button onclick="fetch('/esquerda')">Girar Esquerda</button><br>
        <button onclick="fetch('/direita')">Girar Direita</button><br>
        <button onclick="fetch('/parar')">Parar</button><br>
        <br>
        <h2>Controle de Velocidade</h2>
        <p>Velocidade: <span id="pwmValue">65535</span></p>
        <input type="range" id="pwmSlider" min="0" max="65535" value="65535" oninput="updatePWMValue(this.value)">
        <script>
            function updatePWMValue(value) {
                document.getElementById("pwmValue").innerText = value;
                fetch('/set_pwm?value=' + value);
            }
        </script>
    </body>
    </html>
    """
    return html

# Função para iniciar o servidor web
def iniciar_servidor(ip):
    addr = socket.getaddrinfo(ip, 8080)
    s = socket.socket()
    s.bind(addr[0][-1])
    s.listen(1)
    print('Servidor iniciado em:', ip)

    while True:
        cl, addr = s.accept()
        print('Conexão recebida de:', addr)
        request = cl.recv(1024)
        request = str(request)
        print('Requisição recebida:', request)

        # Comandos para controle dos motores
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
        elif '/set_pwm' in request:
            # Extraindo o valor do PWM enviado
            valor_pwm = int(request.split('value=')[1].split()[0])
            print("Novo valor PWM recebido:", valor_pwm)
            pwm_motor1.duty_u16(valor_pwm)
            pwm_motor2.duty_u16(valor_pwm)
            print("Velocidade ajustada para:", valor_pwm)
            resposta = f"Velocidade ajustada para: {valor_pwm} <a href='/'>Voltar</a>"
        else:
            resposta = criar_website()

        cl.send('HTTP/1.1 200 OK\r\n')
        cl.send('Content-Type: text/html\r\n\r\n')
        cl.send(resposta)
        cl.close()

# Conectar à rede Wi-Fi e iniciar o servidor
ip = conectar_wifi()
iniciar_servidor(ip)

