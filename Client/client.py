import socketio
import os
import subprocess
import ctypes
from pynput.mouse import Controller, Listener
import threading


# Conectando ao servidor
socketClient = socketio.Client()

@socketClient.event
def connect():
    print("Conectado ao servidor!")

@socketClient.event
def disconnect():
    print("Desconectado do servidor.")

@socketClient.on('message')
def on_message(data):
    print(f"Mensagem recebida: {data}")

@socketClient.on('execute_command')
def on_execute_command(data):
    print(f"Comando recebido de {data['from']}: {data['command']}")
    try:
 # Executa o comando no terminal
        process = subprocess.Popen(
            data['command'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
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

    socketClient.connect('http://localhost:3000')

    # await 
    while True:
        print("\nOpções:")
        print("1. Enviar mensagem")
        print("2. Enviar comando")
        choice = input("Escolha: ")

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

        elif choice == '2':
            target = input("Enviar comando para (ID): ")
            command = input("Comando: ")
            socketClient.emit('send_command', {'target': target, 'command': command})
        elif choice == '3':
            target = input("")
            command = input("")
            socketClient.emit('')

        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()
