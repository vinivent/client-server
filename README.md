# Aplicação Cliente-Servidor para Transporte Confiável de Dados

### Descrição

Este projeto consiste no desenvolvimento de uma aplicação cliente-servidor que fornece um transporte confiável de dados. A comunicação entre cliente e servidor é realizada via sockets, e a aplicação é projetada para simular perdas de dados e erros, além de implementar controle de fluxo e controle de congestionamento.

# Objetivos

-   Implementar uma comunicação cliente-servidor através de sockets.
-   Propor e descrever um protocolo de aplicação, incluindo regras para requisições e respostas.
-   Implementar características de transporte confiável de dados:
    -   Soma de verificação
    -   Temporizador
    -   Número de sequência
    -   Reconhecimento
    -   Reconhecimento negativo
    -   Janela e paralelismo
-   Simular falhas de integridade e perdas de mensagens.
-   Permitir o envio de pacotes individuais ou em lotes.
-   Configurar o servidor para confirmação individual ou em grupo.

## Funcionalidades

### Cliente
1.  Enviar um único pacote ou vários pacotes em rajada.
2.  Incluir erros de integridade em pacotes específicos.
3.  Atualizar dinamicamente a janela de recepção do servidor.
4.  Atualizar a janela de congestionamento com base em perdas de pacotes e confirmações duplicadas.

### Servidor

1.  Marcar pacotes que não serão confirmados.
2.  Incluir erros de integridade nas confirmações enviadas.
3.  Sinalizar confirmações negativas para o cliente.
4.  Negociar entre repetição seletiva ou Go-Back-N.
5.  Informar e atualizar dinamicamente a janela de recepção ao cliente.