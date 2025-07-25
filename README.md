
# YOLOAlarm
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/f3785959-8c85-423b-9f14-932f79d8b5d4" />

Aplicação de monitorização com deteção inteligente de pessoas, utilizando YOLO para visão computacional e notificações no sistema. Inclui alarme configurável por horário, interface gráfica em Tkinter e integração com a bandeja do sistema.

---

## 🎯 Funcionalidades

✅ Deteção de pessoas em tempo real com YOLO  
✅ Notificações no sistema quando há deteção  
✅ Possibilidade de guardar capturas de imagem  
✅ Configuração de horário de funcionamento do alarme  
✅ Interface gráfica simples com Tkinter  
✅ Ícone na bandeja do sistema (system tray)  
✅ Possibilidade de abrir o diretório de capturas diretamente  

---

## 🛠️ Requisitos

- Python 3.8 ou superior
- Instalar as seguintes bibliotecas:

```bash
pip install ultralytics
pip install opencv-python
pip install Pillow
pip install pystray
pip install plyer
```

Ou, em alternativa, podes criar um ficheiro `requirements.txt` com o seguinte conteúdo:

```txt
ultralytics
opencv-python
Pillow
pystray
plyer
```

E depois instalar tudo com:

```bash
pip install -r requirements.txt
```

---

## 📦 Estrutura do Projeto

```
.
├── yoloalarme.png         # Ícone da aplicação
├── weights/               # Pasta com os pesos do YOLO
│   └── yolo11s.pt
├── config.json            # Ficheiro de configuração (criado pela app)
├── capturas/              # Diretório onde são guardadas as imagens (configurável)
├── app.py                 # Código principal da aplicação
└── README.md
```

---

## 🚀 Como utilizar

1. Executa o ficheiro `app.py`
<img width="500" height="500" alt="image" src="https://github.com/AnaRitaCarreira/detect_person/blob/main/captures/login.PNG?raw=true" />
2. Faz login com as credenciais:
   - Utilizador: `admin`
   - Senha: `1234`

<img width="500" height="500" alt="image" src="https://github.com/AnaRitaCarreira/detect_person/blob/main/captures/initial.PNG?raw=true" />

3. Configura o IP, utilizador e password da câmara  
4. Define o horário de funcionamento do alarme  
5. Escolhe o diretório onde guardar as imagens  
6. Clica em "Iniciar Alarme"  
7. A aplicação fica minimizada na tray e monitoriza conforme o horário definido  

---

## ⚠️ Notas Importantes

- É necessário o ficheiro de pesos `yolo11s.pt` na pasta `weights`  
- Se quiseres ativar o envio de e-mails, tens de descomentar e configurar a parte do `authenticate` no código  

---

## 👩‍💻 Desenvolvido por

Ana Carreira & Renato Macedo  
Powered by [Ultralytics YOLO](https://ultralytics.com/)  
