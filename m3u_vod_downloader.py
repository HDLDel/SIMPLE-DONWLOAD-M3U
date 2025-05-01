"""
Comandos necessários para instalar todas as dependências:

1. Instalar o VLC Media Player (necessário para a reprodução de vídeos):
   winget install VideoLAN.VLC

2. Instalar o aria2 (para downloads mais rápidos):
   winget install aria2

3. Instalar as bibliotecas Python necessárias:
   pip install python-vlc
   pip install requests
   pip install unidecode
   pip install aria2p

Após instalar todas as dependências, o programa estará pronto para uso.
"""

import os
import requests
import vlc
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import json
import re
import time
from unidecode import unidecode
import aria2p
import subprocess
import sys
import webbrowser

class M3UVODDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("M3U VOD Downloader")
        self.root.geometry("1200x800")  # Aumentei o tamanho para acomodar o player

        # Inicializa o aria2
        self.start_aria2c()
        self.aria2 = aria2p.API(aria2p.Client(host="http://localhost", port=6800))

        # Variáveis
        self.m3u_url = tk.StringVar()
        self.download_path = tk.StringVar(value=os.getcwd())
        self.user_agent = tk.StringVar(value="Mozilla/5.0")  # User-Agent padrão
        self.video_list = []
        self.filtered_video_list = []
        self.selected_videos = []
        self.download_progress = tk.DoubleVar()
        self.download_progress.set(0.0)
        self.cancel_download = False  # Variável para controlar o cancelamento
        self.download_queue = []  # Nova fila de downloads
        self.is_downloading = False  # Flag para controlar se há download em andamento
        self.config_file = "config.json"
        self.load_config()  # Carrega configurações ao iniciar

        # Player VLC
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Adiciona variável para armazenar o último item selecionado
        self.last_selected = None

        # Interface
        self.create_widgets()

    def create_widgets(self):
        # Frame principal com padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para entrada de URL e configurações
        frame_top = ttk.LabelFrame(main_frame, text="Configurações", padding="5")
        frame_top.pack(fill=tk.X, pady=(0, 10))

        # Grid para organizar os elementos
        frame_top.grid_columnconfigure(1, weight=1)

        # URL e botão Load
        ttk.Label(frame_top, text="M3U URL:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(frame_top, textvariable=self.m3u_url).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(frame_top, text="Carregar", command=self.load_m3u).grid(row=0, column=2, padx=5, pady=5)

        # Caminho de download e botão Browse
        ttk.Label(frame_top, text="Pasta de Download:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(frame_top, textvariable=self.download_path).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(frame_top, text="Procurar", command=self.browse_directory).grid(row=1, column=2, padx=5, pady=5)

        # User-Agent
        ttk.Label(frame_top, text="User-Agent:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(frame_top, textvariable=self.user_agent).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(frame_top, text="Salvar Config", command=self.save_config).grid(row=2, column=2, padx=5, pady=5)

        # Frame para barra de progresso
        frame_progress = ttk.LabelFrame(main_frame, text="Progresso do Download", padding="5")
        frame_progress.pack(fill=tk.X, pady=(0, 10))

        # Barra de progresso e informações
        self.progress_bar = ttk.Progressbar(frame_progress, variable=self.download_progress, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        progress_info = ttk.Frame(frame_progress)
        progress_info.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(progress_info, text="0%")
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        self.speed_label = ttk.Label(progress_info, text="0 MB/s")
        self.speed_label.pack(side=tk.LEFT, padx=5)
        
        self.download_info_label = ttk.Label(progress_info, text="", wraplength=800)
        self.download_info_label.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(progress_info, text="Cancelar", command=self.cancel_current_download)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
        self.cancel_button.config(state="disabled")

        # Frame para controles do player
        frame_controls = ttk.LabelFrame(main_frame, text="Controles do Player", padding="5")
        frame_controls.pack(fill=tk.X, pady=(0, 10))

        # Botões de controle do player
        controls = [
            ("Reproduzir", self.play_selected),
            ("Pausar", self.pause_video),
            ("Parar", self.stop_video),
            ("Avançar", self.forward),
            ("Retroceder", self.rewind),
            ("Vol. +", self.volume_up),
            ("Vol. -", self.volume_down),
            ("Abrir no Navegador", self.open_in_browser),
            ("Limpar Pastas", self.clean_folders),
            ("Download Selecionados", self.download_selected)
        ]

        for text, command in controls:
            ttk.Button(frame_controls, text=text, command=command).pack(side=tk.LEFT, padx=5)

        # Frame central para lista e player
        frame_central = ttk.Frame(main_frame)
        frame_central.pack(fill=tk.BOTH, expand=True)

        # Lista de vídeos
        frame_list = ttk.LabelFrame(frame_central, text="Lista de Vídeos", padding="5")
        frame_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Barra de busca
        search_frame = ttk.Frame(frame_list)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Buscar", command=self.filter_videos).pack(side=tk.LEFT, padx=5)

        # Checkbox para selecionar todos
        self.select_all_var = tk.BooleanVar()
        self.select_all_check = ttk.Checkbutton(frame_list, text="Selecionar Todos", 
                                               variable=self.select_all_var, 
                                               command=self.toggle_select_all)
        self.select_all_check.pack(anchor=tk.W, pady=(0, 5))

        # Treeview com scrollbar
        tree_frame = ttk.Frame(frame_list)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Configuração do Treeview com mais colunas
        self.tree = ttk.Treeview(tree_frame, columns=("Select", "Name", "Type", "Season"), show="headings")
        self.tree.heading("Select", text="")
        self.tree.heading("Name", text="Nome")
        self.tree.heading("Type", text="Tipo")
        self.tree.heading("Season", text="Temporada")
        
        self.tree.column("Select", width=50, anchor=tk.CENTER)
        self.tree.column("Name", width=400, anchor=tk.W)
        self.tree.column("Type", width=100, anchor=tk.CENTER)
        self.tree.column("Season", width=100, anchor=tk.CENTER)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Adiciona o evento de clique
        self.tree.bind("<Button-1>", self.on_treeview_click)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)

        # Frame para o player
        frame_player = ttk.LabelFrame(frame_central, text="Player", padding="5")
        frame_player.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Canvas para o player
        self.canvas = tk.Canvas(frame_player, bg="black", width=640, height=360)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_path.set(directory)

    def load_m3u(self):
        url = self.m3u_url.get()
        if not url:
            messagebox.showerror("Error", "Please enter a valid M3U URL.")
            return

        try:
            headers = {"User-Agent": self.user_agent.get()}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            lines = response.text.splitlines()

            self.video_list = []
            self.tree.delete(*self.tree.get_children())

            for i in range(len(lines)):
                if lines[i].startswith("#EXTINF:"):
                    name = lines[i].split('tvg-name="')[1].split('"')[0]
                    url_video = lines[i + 1]
                    
                    # Extrai informações adicionais
                    content_type = "Filme"
                    season = "-"
                    
                    # Verifica se é série
                    match = re.search(r"(.*?)\s*(S\d{2})\s*E\d{2}", name)
                    if match:
                        content_type = "Série"
                        season = match.group(2)
                    
                    self.video_list.append({
                        "name": name,
                        "url": url_video,
                        "type": content_type,
                        "season": season
                    })
                    
                    self.tree.insert("", tk.END, values=("☐", name, content_type, season))

            self.filtered_video_list = self.video_list
            self.save_m3u_to_json()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load M3U: {e}")

    def save_m3u_to_json(self):
        try:
            json_path = os.path.join(os.getcwd(), "m3u_content.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.video_list, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save M3U content: {e}")

    def normalize_text(self, text):
        """Normaliza o texto substituindo símbolos por suas equivalências"""
        # Primeiro substitui símbolos específicos
        replacements = {
            '&': 'e',
            '+': 'mais',
            '@': 'at',
            '$': 's',
            '%': 'porcento',
            '=': 'igual',
            '#': 'numero'
        }
        
        for symbol, replacement in replacements.items():
            text = text.replace(symbol, f' {replacement} ')
            
        # Remove acentos
        text = unidecode(text.lower())
        
        # Remove outros símbolos mantendo letras, números e espaços
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove espaços extras
        text = ' '.join(text.split())
        
        return text

    def filter_videos(self):
        """Filtra os vídeos usando normalização de texto"""
        # Normaliza o termo de busca
        search_term = self.normalize_text(self.search_entry.get())
        
        self.tree.delete(*self.tree.get_children())

        if search_term:
            self.filtered_video_list = []
            for video in self.video_list:
                # Normaliza o nome do vídeo
                video_name = self.normalize_text(video["name"])
                
                if search_term in video_name:
                    self.filtered_video_list.append(video)
        else:
            self.filtered_video_list = self.video_list

        # Atualiza a interface com os resultados
        for video in self.filtered_video_list:
            self.tree.insert("", tk.END, values=(
                "☐",
                video["name"],
                video.get("type", "Filme"),
                video.get("season", "-")
            ))
            
        # Atualiza o status da busca
        total_videos = len(self.filtered_video_list)
        if search_term:
            self.download_info_label.config(text=f"Encontrados {total_videos} vídeos para '{self.search_entry.get()}'")
        else:
            self.download_info_label.config(text=f"Total de {total_videos} vídeos")
        
        # Reseta o estado do checkbox "Selecionar Todos"
        self.select_all_var.set(False)

    def update_select_all_state(self):
        """Atualiza o estado do checkbox 'Selecionar Todos' baseado nos itens selecionados"""
        all_items = self.tree.get_children()
        if not all_items:  # Se não houver itens
            self.select_all_var.set(False)
            return
            
        # Verifica se todos os itens estão selecionados
        all_selected = all(self.tree.set(item, "Select") == "☑" for item in all_items)
        self.select_all_var.set(all_selected)

    def toggle_select_all(self):
        """Seleciona ou desseleciona todos os itens"""
        is_selected = self.select_all_var.get()
        for item in self.tree.get_children():
            self.tree.set(item, "Select", "☑" if is_selected else "☐")

    def on_treeview_click(self, event):
        """Gerencia o clique na TreeView para seleção de itens"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # Coluna "Select"
                item = self.tree.identify_row(event.y)
                if item:  # Verifica se um item foi identificado
                    if event.state & 1 and self.last_selected:  # Shift pressionado e tem item anterior
                        # Pega todos os itens da TreeView
                        all_items = self.tree.get_children()
                        
                        # Encontra os índices do item atual e do último selecionado
                        current_index = all_items.index(item)
                        last_index = all_items.index(self.last_selected)
                        
                        # Determina o início e fim da seleção
                        start_index = min(current_index, last_index)
                        end_index = max(current_index, last_index)
                        
                        # Seleciona todos os itens no intervalo
                        for i in range(start_index, end_index + 1):
                            self.tree.set(all_items[i], "Select", "☑")
                    else:
                        # Comportamento normal de alternar seleção
                        current_value = self.tree.set(item, "Select")
                        new_value = "☑" if current_value == "☐" else "☐"
                        self.tree.set(item, "Select", new_value)
                        self.last_selected = item  # Atualiza o último item selecionado
                    
                    # Atualiza o checkbox "Selecionar Todos"
                    self.update_select_all_state()

    def download_selected(self):
        selected_items = []
        for item in self.tree.get_children():
            if self.tree.set(item, "Select") == "☑":
                selected_items.append(item)

        if not selected_items:
            messagebox.showwarning("Warning", "No videos selected.")
            return

        download_path = self.download_path.get()
        if not os.path.exists(download_path):
            messagebox.showerror("Error", "Invalid download path.")
            return

        # Adiciona os vídeos selecionados à fila
        for item in selected_items:
            video = self.filtered_video_list[int(self.tree.index(item))]
            self.download_queue.append((video["name"], video["url"], download_path))

        # Inicia o processamento da fila se não houver download em andamento
        if not self.is_downloading:
            self.process_download_queue()

    def process_download_queue(self):
        if not self.download_queue:
            self.is_downloading = False
            return

        self.is_downloading = True
        name, url, path = self.download_queue.pop(0)
        Thread(target=self.download_video_with_callback, args=(name, url, path)).start()

    def download_video_with_callback(self, name, url, path):
        try:
            self.download_video(name, url, path)
        finally:
            # Processa o próximo item da fila quando o download atual terminar
            self.root.after(1000, self.process_download_queue)

    def start_aria2c(self):
        try:
            # Tenta iniciar o servidor aria2c
            subprocess.Popen(["aria2c", "--enable-rpc", "--rpc-listen-all=true"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            time.sleep(2)  # Aguarda o servidor iniciar
        except FileNotFoundError:
            messagebox.showerror("Error", "aria2c não encontrado. Por favor, instale o aria2 primeiro.")
            sys.exit(1)

    def download_video(self, name, url, path):
        try:
            self.cancel_download = False
            self.cancel_button.config(state="normal")
            self.download_info_label.config(text=f"Baixando: {name}")
            
            # Extrai o nome do conteúdo e a temporada
            content_name, season = self.extract_content_info(name)

            # Cria a pasta do conteúdo
            content_folder = os.path.join(path, content_name)
            if not os.path.exists(content_folder):
                os.makedirs(content_folder)

            # Se for uma série, cria a pasta da temporada
            if season:
                season_folder = os.path.join(content_folder, season)
                if not os.path.exists(season_folder):
                    os.makedirs(season_folder)
                file_path = os.path.join(season_folder, f"{name}.mp4")
            else:
                file_path = os.path.join(content_folder, f"{name}.mp4")

            # Configuração do download com aria2
            options = {
                "dir": os.path.dirname(file_path),
                "out": os.path.basename(file_path),
                "max-connection-per-server": "16",
                "split": "16",
                "user-agent": self.user_agent.get(),
                "continue": "true",
                "max-concurrent-downloads": "1"
            }

            # Inicia o download
            download = self.aria2.add_uris([url], options=options)
            
            while not self.cancel_download and download.is_active:
                try:
                    download.update()
                    downloaded = download.completed_length
                    total = download.total_length
                    
                    if total > 0:
                        progress = (downloaded / total) * 100
                        speed = download.download_speed / (1024 * 1024)  # Converte para MB/s
                        
                        self.download_progress.set(progress)
                        self.progress_label.config(text=f"{progress:.1f}%")
                        self.speed_label.config(text=f"{speed:.1f} MB/s")
                        self.root.update_idletasks()
                    
                    time.sleep(0.1)
                except Exception:
                    break

            if self.cancel_download:
                download.remove(force=True)
                if os.path.exists(file_path):
                    os.remove(file_path)
                self.download_info_label.config(text="Download cancelado")
                return

        except Exception as e:
            messagebox.showerror("Error", f"Erro ao baixar {name}: {e}")
        finally:
            self.download_progress.set(0.0)
            self.progress_label.config(text="0%")
            self.speed_label.config(text="0 MB/s")
            self.download_info_label.config(text="")
            self.cancel_button.config(state="disabled")

    def extract_content_info(self, name):
        # Extrai o nome do conteúdo e a temporada (se for uma série)
        # Formato esperado: "Nome da Série S01 E01" ou similar
        match = re.search(r"(.*?)\s*(S\d{2})\s*E\d{2}", name)
        if match:
            content_name = match.group(1).strip()
            season = match.group(2).strip()
            return content_name, season
        else:
            return name, None

    def play_selected(self):
        selected_items = []
        for item in self.tree.get_children():
            if self.tree.set(item, "Select") == "☑":
                selected_items.append(item)

        if not selected_items:
            messagebox.showwarning("Warning", "No videos selected.")
            return

        video = self.filtered_video_list[int(self.tree.index(selected_items[0]))]
        media = self.instance.media_new(video["url"])
        self.player.set_media(media)
        self.player.set_hwnd(self.canvas.winfo_id())  # Configura o player para usar o Canvas
        self.player.play()

    def pause_video(self):
        if self.player.is_playing():
            self.player.pause()

    def stop_video(self):
        self.player.stop()

    def forward(self):
        # Avança 10 segundos
        self.player.set_time(self.player.get_time() + 10000)

    def rewind(self):
        # Retrocede 10 segundos
        self.player.set_time(max(self.player.get_time() - 10000, 0))

    def volume_up(self):
        # Aumenta o volume em 10%
        self.player.audio_set_volume(min(self.player.audio_get_volume() + 10, 100))

    def volume_down(self):
        # Diminui o volume em 10%
        self.player.audio_set_volume(max(self.player.audio_get_volume() - 10, 0))

    def cancel_current_download(self):
        if self.is_downloading:
            self.cancel_download = True
            self.download_info_label.config(text="Cancelando download...")

    def load_config(self):
        """Carrega configurações do arquivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.m3u_url.set(config.get('m3u_url', ''))
                    self.download_path.set(config.get('download_path', os.getcwd()))
                    self.user_agent.set(config.get('user_agent', 'Mozilla/5.0'))
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")

    def save_config(self):
        """Salva configurações em arquivo JSON"""
        config = {
            'm3u_url': self.m3u_url.get(),
            'download_path': self.download_path.get(),
            'user_agent': self.user_agent.get()
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def open_in_browser(self):
        """Abre o vídeo selecionado no navegador padrão"""
        selected_items = []
        for item in self.tree.get_children():
            if self.tree.set(item, "Select") == "☑":
                selected_items.append(item)

        if not selected_items:
            messagebox.showwarning("Aviso", "Nenhum vídeo selecionado.")
            return

        video = self.filtered_video_list[int(self.tree.index(selected_items[0]))]
        webbrowser.open(video["url"])

    def clean_folders(self):
        """Limpa as pastas de download"""
        try:
            # Pede confirmação antes de limpar
            if not messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar todas as pastas de download?"):
                return

            # Obtém o diretório base de downloads
            base_dir = self.download_path.get()
            
            # Lista para armazenar arquivos e pastas a serem removidos
            items_to_remove = []
            
            # Percorre o diretório base
            for root, dirs, files in os.walk(base_dir):
                # Adiciona arquivos à lista
                for file in files:
                    if file.endswith(('.mp4', '.mkv', '.avi', '.mov')):
                        items_to_remove.append(os.path.join(root, file))
                
                # Adiciona pastas vazias à lista
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if not os.listdir(dir_path):  # Se a pasta estiver vazia
                        items_to_remove.append(dir_path)
            
            # Remove os itens
            for item in items_to_remove:
                try:
                    if os.path.isfile(item):
                        os.remove(item)
                    elif os.path.isdir(item):
                        os.rmdir(item)
                except Exception as e:
                    print(f"Erro ao remover {item}: {e}")
            
            messagebox.showinfo("Sucesso", "Pastas de download limpas com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao limpar pastas: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = M3UVODDownloader(root)
    root.mainloop()