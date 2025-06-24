import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog
import cv2
from ultralytics import solutions
import threading
import datetime
import time
from PIL import Image, ImageTk  
import json
import os
import pystray
from pystray import MenuItem as item


# Caminho do ficheiro de configuração
CONFIG_FILE = "config.json"
janela = None  # Vamos controlar a janela globalmente
icone_tray = None  # Controlar o ícone da tray
alarme_parar = threading.Event()  # Event para controlar o stop da thread

# Função para guardar dados
def guardar_config(ip,user_cam,password_cam, hora_inicio, hora_fim, diretorio_imagens):
    config = {
        "ip": ip,
        "user_cam": user_cam, 
        "password_cam":password_cam,
        "hora_inicio": hora_inicio,
        "hora_fim": hora_fim,
        "diretorio_imagens": diretorio_imagens
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


# Função para carregar dados
def carregar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

# Função para verificar se estamos dentro do horário de alarme
def dentro_do_periodo(hora_inicio, hora_fim):
    agora = datetime.datetime.now().time()
    return hora_inicio <= agora <= hora_fim if hora_inicio < hora_fim else (agora >= hora_inicio or agora <= hora_fim)


# Função que inicia o processamento do vídeo
def iniciar_alarme(ip_camera, hora_inicio, hora_fim):
    cap = cv2.VideoCapture(ip_camera)
    if not cap.isOpened():
        messagebox.showerror("Erro", "Não foi possível abrir o vídeo ou câmara.")
        return

    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    video_writer = cv2.VideoWriter("security_output.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    from_email = "myyoloalarm@gmail.com"
    password = "---- ---- ---- ----"  # Substituir pela tua app password
    to_email = "xyz@gmail.com"

    securityalarm = solutions.SecurityAlarm(
        show=False,
        model="./weights/yolo11s.pt",
        records=1,
    )
    #securityalarm.authenticate(from_email, password, to_email)

    while cap.isOpened():
        
        while not alarme_parar.is_set():
            if dentro_do_periodo(hora_inicio, hora_fim):
                print("Alarme iniciado, monitorizando...")
                success, im0 = cap.read()
                if not success:
                    break
                results = securityalarm(im0)
                video_writer.write(results.plot_im)
            else:
                print("Fora do horário do alarme. Aguardando...")
                time.sleep(10)
        print("Alarme parado.")

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()


# Janela de Login
def verificar_login():
    utilizador = entrada_utilizador.get()
    senha = entrada_senha.get()

    if utilizador == "admin" and senha == "1234":
        janela_login.destroy()
        abrir_janela_principal()
    else:
        messagebox.showerror("Erro", "Credenciais inválidas.")

# Mostrar e esconder janela
def esconder_janela(event=None):
    global janela
    if janela:
        janela.withdraw()

def mostrar_janela():
    global janela
    if janela:
        janela.deiconify()

def sair_aplicacao():
    global icone_tray, janela
    alarme_parar.set()  # Para a thread do alarme
    if icone_tray:
        icone_tray.stop()
    if janela:
        janela.destroy()

def iniciar_tray():
    global icone_tray
    image = Image.open("yoloalarme.png").resize((64, 64))
    icone_tray = pystray.Icon("yoloalarm", image, "YOLOAlarm", menu=pystray.Menu(
        item('Mostrar', lambda: mostrar_janela()),
        item('Sair', lambda: sair_aplicacao())
    ))
    threading.Thread(target=icone_tray.run, daemon=True).start()

def choose_directory():
    global diretorio_imagens
    pasta = filedialog.askdirectory()
    if pasta:
        diretorio_imagens = pasta
        print(f"Novo diretório escolhido: {diretorio_imagens}")
                # Carregar config atual
        config = carregar_config()
        
        # Atualizar config com o novo diretório
        config["diretorio_imagens"] = diretorio_imagens

        # Guardar novamente o ficheiro
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

# Janela Principal
def abrir_janela_principal():
    global janela, alarme_parar, diretorio_imagens
    alarme_parar.clear()  # Reset event
    # Carregar configuração existente, se houver
    config = carregar_config()

    janela = tk.Tk()
    janela.title("Configuração do Alarme - YOLOAlarm")
    janela.geometry("400x600")  # Largura x Altura em píxeis

    # Cria o menu
    menu_bar = tk.Menu(janela)
    
    # Menu Opções
    options_menu = tk.Menu(menu_bar, tearoff=0)
    options_menu.add_command(label="Escolher diretório para guardar capturas", command=choose_directory)
    menu_bar.add_cascade(label="Opções", menu=options_menu)
    
    janela.config(menu=menu_bar)



    # Carregar imagem
    try:
        imagem = Image.open("yoloalarme.png").resize((150, 150))
        imagem_tk = ImageTk.PhotoImage(imagem)
        label_imagem = tk.Label(janela, image=imagem_tk)
        label_imagem.image = imagem_tk  # referência para não ser garbage collected
        label_imagem.pack(pady=10)
    except Exception as e:
        print("Imagem não carregada:", e)

    tk.Label(janela, text="Username da Câmara:").pack()
    entrada_usercam = tk.Entry(janela, width=40)
    entrada_usercam.pack()
    entrada_usercam.insert(0, config.get("user_cam", ""))


    tk.Label(janela, text="Password da Câmara:").pack()
    entrada_passwordcam = tk.Entry(janela, width=40)
    entrada_passwordcam.pack()
    entrada_passwordcam.insert(0, config.get("password_cam", ""))


    tk.Label(janela, text="IP da Câmara:").pack()
    entrada_ip = tk.Entry(janela, width=40)
    entrada_ip.pack()
    entrada_ip.insert(0, config.get("ip", ""))

    tk.Label(janela, text="Hora de Início do Alarme:").pack()

    frame_inicio = tk.Frame(janela)
    frame_inicio.pack()

    spin_hora_inicio = tk.Spinbox(frame_inicio, from_=0, to=23, width=3, format="%02.0f")
    spin_hora_inicio.pack(side=tk.LEFT)
    tk.Label(frame_inicio, text=":").pack(side=tk.LEFT)
    spin_minuto_inicio = tk.Spinbox(frame_inicio, from_=0, to=59, width=3, format="%02.0f")
    spin_minuto_inicio.pack(side=tk.LEFT)

   # Obter a hora e minuto separados
    hora_inicio = config.get("hora_inicio", "")
    if hora_inicio:
        partes = hora_inicio.split(":")
        if len(partes) == 2:
            spin_hora_inicio.delete(0, tk.END)
            spin_hora_inicio.insert(0, partes[0])
            spin_minuto_inicio.delete(0, tk.END)
            spin_minuto_inicio.insert(0, partes[1])


    tk.Label(janela, text="Hora de Fim do Alarme:").pack()

    frame_fim = tk.Frame(janela)
    frame_fim.pack()

    spin_hora_fim = tk.Spinbox(frame_fim, from_=0, to=23, width=3, format="%02.0f")
    spin_hora_fim.pack(side=tk.LEFT)
    tk.Label(frame_fim, text=":").pack(side=tk.LEFT)
    spin_minuto_fim = tk.Spinbox(frame_fim, from_=0, to=59, width=3, format="%02.0f")
    spin_minuto_fim.pack(side=tk.LEFT)


    # Obter a hora e minuto separados
    hora_fim = config.get("hora_fim", "")
    if hora_fim:
        partes = hora_fim.split(":")
        if len(partes) == 2:
            spin_hora_fim.delete(0, tk.END)
            spin_hora_fim.insert(0, partes[0])
            spin_minuto_fim.delete(0, tk.END)
            spin_minuto_fim.insert(0, partes[1])

    def iniciar():

        ip = entrada_ip.get()
        user_cam = entrada_usercam.get()
        password_cam = entrada_passwordcam.get()
        entrada_inicio_str = f"{spin_hora_inicio.get()}:{spin_minuto_inicio.get()}"
        entrada_fim_str = f"{spin_hora_fim.get()}:{spin_minuto_fim.get()}"
        try:
            h_inicio = datetime.datetime.strptime(entrada_inicio_str, "%H:%M").time()
            h_fim = datetime.datetime.strptime(entrada_fim_str, "%H:%M").time()
        except ValueError:
            messagebox.showerror("Erro", "Formato de hora inválido. Utilize HH:MM.")
            return
        
        # Guardar configuração
        guardar_config(ip,user_cam,password_cam, hora_inicio, hora_fim, diretorio_imagens)
        alarme_parar.clear()
        url_cam = f"rtsp://{user_cam}:{password_cam}@{ip}\stream1"
        print("url_cam:", url_cam)
        threading.Thread(target=iniciar_alarme, args=(0, h_inicio, h_fim), daemon=True).start()
        messagebox.showinfo("Informação", "Alarme iniciado! Pode minimizar janela.")

    def parar():
        alarme_parar.set()
        messagebox.showinfo("Info", "Alarme parado!")

    btn_iniciar = tk.Button(janela, text="Iniciar Alarme", command=iniciar)
    btn_iniciar.pack(pady=5)

    btn_parar = tk.Button(janela, text="Parar Alarme", command=parar)
    btn_parar.pack(pady=5)

    # Quando janela for minimizada, esconder e mostrar tray
    janela.bind("<Unmap>", esconder_janela)

    iniciar_tray()


# Interface Login
janela_login = tk.Tk()
janela_login.title("Login - YOLOAlarm")
janela_login.geometry("400x300")  # Largura x Altura em píxeis
#titulo = tk.Label(janela_login, text="Bem-vindo à Aplicação YOLOAlarm!", font=("Arial", 16))
#titulo.pack(pady=20)  # Espaçamento vertical

# Carregar imagem
imagem_path = "yoloalarme.png"  
imagem = Image.open(imagem_path)
imagem = imagem.resize((150, 150))  # Ajusta o tamanho conforme necessário
imagem_tk = ImageTk.PhotoImage(imagem)

# Label para imagem
label_imagem = tk.Label(janela_login, image=imagem_tk)
label_imagem.pack(pady=10)  # Centra a imagem e dá espaçamento

tk.Label(janela_login, text="Utilizador:").pack()
entrada_utilizador = tk.Entry(janela_login)
entrada_utilizador.pack()

tk.Label(janela_login, text="Senha:").pack()
entrada_senha = tk.Entry(janela_login, show="*")
entrada_senha.pack()

tk.Button(janela_login, text="Iniciar Sessão", command=verificar_login).pack(pady=10)

janela_login.mainloop()
