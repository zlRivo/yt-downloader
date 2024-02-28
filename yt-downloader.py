from pytube import YouTube
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import pathlib
import json
import os

YT_DOWNLOADER_CONFIG = 'YT Downloader/yt-dl-config.json'
CONFIG_TARGET_DIR_KEY = 'target_dir'

MP3_EXTENSION = '.mp3'
MP4_EXTENSION = '.mp4'

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('YT Downloader')
        self.root.geometry('300x160')

        self.config = None

        # Create menu bar
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label='Choose target directory', command=self.choose_target_directory)
        self.menu_bar.add_cascade(label='Edit', menu=self.file_menu)

        # Add menu bar
        self.root.config(menu=self.menu_bar)

        # Video URL
        self.vid_url_lbl = tk.Label(self.root, text='Video URL:')
        self.vid_url_lbl.pack()

        self.vid_url_entry = tk.Entry(self.root)
        self.vid_url_entry.pack()

        # Filename
        self.dest_filename = tk.Label(self.root, text='Filename:')
        self.dest_filename.pack()

        self.dest_filename = tk.Entry(self.root)
        self.dest_filename.pack()

        # Radio buttons
        self.radio_frame = tk.Frame(self.root)

        self.radio_val = tk.IntVar()
        self.r1_mp3 = tk.Radiobutton(self.radio_frame, text='MP3', variable=self.radio_val, value=0)
        self.r1_mp3.grid(column=0, row=0, sticky=tk.W)

        self.r1_mp4 = tk.Radiobutton(self.radio_frame, text='MP4', variable=self.radio_val, value=1)
        self.r1_mp4.grid(column=1, row=0, sticky=tk.W)

        self.radio_frame.pack()

        # Download button
        self.dl_button = tk.Button(self.root, text='Download', command=self.download_video)
        self.dl_button.pack()

        # Full config file path
        self.config_file = pathlib.Path(os.getenv('LOCALAPPDATA')).joinpath(YT_DOWNLOADER_CONFIG)

        self.init_config()

        if not self.read_config():
            self.show_config_file_error_dialog()
    
    def download_video(self):
        download_dir = pathlib.Path(self.config[CONFIG_TARGET_DIR_KEY])
        if not download_dir.is_dir():
            return
        
        only_audio, extension = (True, MP3_EXTENSION) if self.radio_val.get() == 0 else (False, MP4_EXTENSION)

        # Download file
        yt = YouTube(self.vid_url_entry.get())
        video = yt.streams.filter(only_audio=only_audio).first()
        output_name = video.download(output_path=download_dir)
        os.rename(output_name, download_dir.joinpath(self.dest_filename.get() + extension)) # Rename file
        messagebox.showinfo('Info', 'Completed.')
    
    def show_config_file_error_dialog(self):
        if messagebox.askyesno('Error', message='Failed to load config file. Recreate it?', icon='error'):
            os.remove(self.config_file)
            self.init_config()
    
    def init_config(self):
        # Create directory if needed
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

        # Create file with default config if not existing
        if not self.config_file.exists():
            self.config = dict()
            self.config[CONFIG_TARGET_DIR_KEY] = ''
            self.save_config()
    
    def read_config(self) -> bool:
        with self.config_file.open('r') as f:
            try:
                config = json.load(f)
                if (not CONFIG_TARGET_DIR_KEY in config or type(config[CONFIG_TARGET_DIR_KEY]) != str):
                    self.config = None
                    return False

                self.config = config
                return True
            except json.JSONDecodeError:
                self.config = None
                return False
            
    def save_config(self) -> bool:
        with self.config_file.open('w') as f:
            try:
                json.dump(self.config, f, indent=4)
                return True
            except:
                return False
    
    def update_config(self, key, val) -> bool:
        self.config[key] = val
        return self.save_config()
    
    def choose_target_directory(self):
        if (target_dir := filedialog.askdirectory(title='Choose target directory')) != '':
            result = self.update_config(CONFIG_TARGET_DIR_KEY, target_dir)
            if result != True:
                messagebox.showerror('Error', 'Failed to update config')

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    App().run()