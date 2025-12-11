"""
UI Top Bar - Statistics display
"""
import customtkinter as ctk
from Core.constants import EMOJI


class TopBar:
    """Top statistics bar"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup()
    
    def setup(self):
        """Setup top bar"""
        top_bar = ctk.CTkFrame(self.parent, height=80, corner_radius=0, fg_color="#1a1a1a")
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_bar.grid_columnconfigure((0,1,2,3,4,5), weight=1)
        
        # Title
        ctk.CTkLabel(top_bar, text=f"{EMOJI['egg']} Egg Sorter Pro",
                    font=ctk.CTkFont(size=24, weight="bold")).grid(
                        row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Statistics
        stats_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        stats_frame.grid(row=0, column=1, columnspan=5, padx=20, pady=10, sticky="e")
        
        # ACCEPT stat
        accept_frame = ctk.CTkFrame(stats_frame, fg_color="#1e4d2b", corner_radius=8)
        accept_frame.pack(side="left", padx=5)
        self.accept_label = ctk.CTkLabel(accept_frame, 
            text=f"{EMOJI['check']} ACCEPT\n0",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#2ecc71")
        self.accept_label.pack(padx=20, pady=10)
        
        # REJECT stat
        reject_frame = ctk.CTkFrame(stats_frame, fg_color="#4d1e1e", corner_radius=8)
        reject_frame.pack(side="left", padx=5)
        self.reject_label = ctk.CTkLabel(reject_frame,
            text=f"{EMOJI['cross']} REJECT\n0",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#e74c3c")
        self.reject_label.pack(padx=20, pady=10)
        
        # FPS stat
        perf_frame = ctk.CTkFrame(stats_frame, fg_color="#1e3a4d", corner_radius=8)
        perf_frame.pack(side="left", padx=5)
        self.perf_label = ctk.CTkLabel(perf_frame,
            text=f"{EMOJI['lightning']} FPS\n0.0",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#3498db")
        self.perf_label.pack(padx=20, pady=10)
        
        # Tracked stat
        track_frame = ctk.CTkFrame(stats_frame, fg_color="#4d3a1e", corner_radius=8)
        track_frame.pack(side="left", padx=5)
        self.tracked_label = ctk.CTkLabel(track_frame,
            text=f"{EMOJI['target']} Tracked\n0",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#f39c12")
        self.tracked_label.pack(padx=20, pady=10)
        
        # Serial status
        serial_frame = ctk.CTkFrame(stats_frame, fg_color="#2b2b2b", corner_radius=8)
        serial_frame.pack(side="left", padx=5)
        self.serial_label = ctk.CTkLabel(serial_frame,
            text=f"{EMOJI['usb']} Serial\n⚫ Off",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="gray")
        self.serial_label.pack(padx=20, pady=10)
    
    def update_stats(self, accept=None, reject=None, fps=None, tracked=None):
        """Update statistics"""
        if accept is not None:
            self.accept_label.configure(text=f"{EMOJI['check']} ACCEPT\n{accept}")
        if reject is not None:
            self.reject_label.configure(text=f"{EMOJI['cross']} REJECT\n{reject}")
        if fps is not None:
            self.perf_label.configure(text=f"{EMOJI['lightning']} FPS\n{fps:.1f}")
        if tracked is not None:
            self.tracked_label.configure(text=f"{EMOJI['target']} Tracked\n{tracked}")
    
    def update_serial_status(self, connected):
        """Update serial connection status"""
        if connected:
            self.serial_label.configure(
                text=f"{EMOJI['usb']} Serial\n🟢 On",
                text_color="#2ecc71"
            )
        else:
            self.serial_label.configure(
                text=f"{EMOJI['usb']} Serial\n⚫ Off",
                text_color="gray"
            )