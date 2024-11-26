# Socket Control

#### Este projeto é uma aplicação cliente-servidor que combina controle remoto de mouse, transmissão de vídeo via webcam e execução de comandos. Ele utiliza Socket.IO para comunicação em tempo real e várias bibliotecas Python para funções específicas. 
---

## 📦 **Bibliotecas Utilizadas**

- **socketio**  
  Garante a comunicação entre clientes e o servidor.

- **os**  
  Realiza interações com o sistema operacional.

- **subprocess**  
  Permite a execução de comandos diretamente no terminal a partir do código.

- **ctypes**  
  Biblioteca para acessar funções do sistema operacional em baixo nível.

- **pynput**  
  Gerencia o controle e monitoramento do mouse.

- **threading**  
  Roda funções em threads paralelas. Usado para capturar o mouse e rodar a transmissão de vídeo sem bloquear o restante do código.

- **cv2 (OpenCV)**  
  Captura frames da webcam, codifica e exibe.

- **base64**  
  Codifica frames da webcam em strings para transmissão.

- **time**  
  Cria delays e controla a taxa de quadros da transmissão de vídeo.

- **numpy**  
  Manipula os frames como arrays para processamento de imagens.

---

## ✨ **Funcionalidades Principais**

### **Transmissão de Vídeo**
Captura vídeo da webcam do cliente e transmite para outro cliente em tempo real.

### **Controle Remoto de Mouse**
Permite limitar a área de movimento ou inverter os comandos do mouse.

### **Execução de Comandos**
Executa comandos personalizados ou pré-definidos, como desligar o monitor.

### **Mensagens em Tempo Real**
Envie mensagens privadas ou para todos os clientes conectados.

---

## 🛠️ **Como Usar**
### Clone o Projeto
    git clone https://github.com/NayanBecker/Socket-server-client
  
### **1. Configurar o Servidor**
1. Certifique-se de ter o **Node.js** instalado.
2. Instale as dependências:
   ```bash
   npm install
3. Inicie o servidor:
    ````bash
    node server.js
### **2. Configurar o Servidor**
1. Certifique-se de ter o **Python** instalado.
2. Instale as dependências necessárias:
    ````bash
    pip install python-socketio pynput opencv-python-headless numpy
3. Execute o cliente:
   ````bash
   python client.py




    
