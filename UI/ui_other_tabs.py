"""
Other UI Tabs - Serial, Log, Chart
"""
import customtkinter as ctk
from Core.constants import EMOJI
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class SerialTab:
    """Serial communication tab"""
    
    def __init__(self, parent, config, callbacks):
        self.parent = parent
        self.config = config
        self.callbacks = callbacks
        self.tab = parent.add(f"{EMOJI['usb']} Serial Port")
        self.setup()
    
    def setup(self):
        """Setup serial tab"""
        self.tab.grid_columnconfigure((0,1), weight=1)
        
        # Left - Connection
        left_frame = ctk.CTkFrame(self.tab)
        left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(left_frame, text="Koneksi Arduino/ESP32",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Port selection
        port_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b")
        port_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(port_frame, text="Select COM Port:",
                    font=ctk.CTkFont(size=14)).pack(pady=(15, 10))
        
        port_select_frame = ctk.CTkFrame(port_frame, fg_color="transparent")
        port_select_frame.pack(pady=10, padx=20, fill="x")
        
        self.port_var = ctk.StringVar(value=self.config.serial_port or "Not Connected")
        self.port_menu = ctk.CTkOptionMenu(
            port_select_frame,
            values=["Not Connected"],
            variable=self.port_var,
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.port_menu.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(port_select_frame, text="🔍 Refresh", width=100, height=40,
                     command=self.callbacks['refresh_ports']).pack(side="left")
        
        # Baudrate
        baud_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b")
        baud_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(baud_frame, text="Baudrate:",
                    font=ctk.CTkFont(size=14)).pack(pady=(15, 10))
        
        self.baudrate_var = ctk.StringVar(value=str(self.config.serial_baudrate))
        ctk.CTkSegmentedButton(baud_frame, values=["9600", "115200"],
                              variable=self.baudrate_var, height=40).pack(
                                  pady=10, padx=20, fill="x")
        
        # Status
        status_frame = ctk.CTkFrame(left_frame, fg_color="#1a1a1a", corner_radius=10)
        status_frame.pack(pady=20, padx=20, fill="x")
        
        self.status_label = ctk.CTkLabel(
            status_frame, text="⚫ Disconnected",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="gray"
        )
        self.status_label.pack(pady=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(pady=10, padx=20, fill="x")
        
        self.connect_btn = ctk.CTkButton(
            btn_frame, text="🔌 Connect", command=self.callbacks['connect'],
            fg_color="#27ae60", hover_color="#229954", height=50,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.connect_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        self.disconnect_btn = ctk.CTkButton(
            btn_frame, text="⛔ Disconnect", command=self.callbacks['disconnect'],
            fg_color="#e74c3c", hover_color="#c0392b", height=50,
            state="disabled", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.disconnect_btn.pack(side="left", expand=True, fill="x", padx=(10, 0))
        
        # Test buttons
        test_frame = ctk.CTkFrame(left_frame, fg_color="#2b2b2b")
        test_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(test_frame, text="Test Commands:",
                    font=ctk.CTkFont(size=14)).pack(pady=(15, 10))
        
        test_btn_frame = ctk.CTkFrame(test_frame, fg_color="transparent")
        test_btn_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(test_btn_frame, text="✅ Test ACCEPT", 
                     command=lambda: self.callbacks['test']("ACCEPT"),
                     fg_color="#2ecc71", height=40).pack(
                         side="left", expand=True, fill="x", padx=(0, 10))
        
        ctk.CTkButton(test_btn_frame, text="❌ Test REJECT",
                     command=lambda: self.callbacks['test']("REJECT"),
                     fg_color="#e74c3c", height=40).pack(
                         side="left", expand=True, fill="x", padx=(10, 0))
        
        ctk.CTkLabel(test_frame, text="(Kirim sinyal ke Arduino untuk test)",
                    font=ctk.CTkFont(size=10), text_color="gray").pack(pady=(5, 15))
        
        # Right - Code example
        self._setup_code_example(self.tab)
    
    def _setup_code_example(self, parent):
        """Setup Arduino code example"""
        right_frame = ctk.CTkFrame(parent)
        right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(right_frame, text="Fitur Koneksi dan Pengujian Serial Arduino/ESP32",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        code_text = """
<>Pemilihan COM Port untuk menentukan jalur komunikasi antara aplikasi dan Arduino/ESP32

<>Tombol Refresh Port untuk mendeteksi ulang perangkat yang baru terhubung

<>Pengaturan Baudrate (9600 / 115200) agar komunikasi serial sesuai dengan konfigurasi Arduino

<>Indikator status koneksi untuk menampilkan kondisi terhubung atau terputus

<>Tombol Connect dan Disconnect untuk mengelola koneksi serial secara langsung

<>Test ACCEPT untuk menguji pengiriman perintah terima ke Arduino

<>Test REJECT untuk menguji pengiriman perintah tolak ke Arduino

<>Arduino Code Example sebagai referensi format perintah dan kode yang kompatibel dengan aplikasi"""
        
        code_box = ctk.CTkTextbox(right_frame, font=ctk.CTkFont(family="Courier", size=16))
        code_box.pack(pady=10, padx=20, fill="both", expand=True)
        code_box.insert("1.0", code_text)
        code_box.configure(state="disabled")
    
    def update_ports(self, ports):
        """Update available ports"""
        if ports:
            port_list = [f"{port[0]} - {port[1]}" for port in ports]
            self.port_menu.configure(values=port_list)
            if port_list:
                self.port_var.set(port_list[0])
        else:
            self.port_menu.configure(values=["No Ports Found"])
            self.port_var.set("No Ports Found")
    
    def update_status(self, connected):
        """Update connection status"""
        if connected:
            self.status_label.configure(text="🟢 Connected", text_color="#2ecc71")
            self.connect_btn.configure(state="disabled")
            self.disconnect_btn.configure(state="normal")
        else:
            self.status_label.configure(text="⚫ Disconnected", text_color="gray")
            self.connect_btn.configure(state="normal")
            self.disconnect_btn.configure(state="disabled")


class LogTab:
    """Log viewer tab"""
    
    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.tab = parent.add(f"{EMOJI['folder']} Logs")
        self.setup()
    
    def setup(self):
        """Setup log tab"""
        self.tab.grid_columnconfigure(0, weight=1)
        self.tab.grid_rowconfigure(1, weight=1)
        
        # Control buttons
        control_frame = ctk.CTkFrame(self.tab)
        control_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        control_frame.grid_columnconfigure((0,1,2), weight=1)
        
        ctk.CTkButton(control_frame, text=f"{EMOJI['refresh']} Refresh (F5)",
                     command=self.callbacks['refresh'], height=45,
                     font=ctk.CTkFont(size=13)).grid(
                         row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(control_frame, text=f"{EMOJI['down']} Export CSV",
                     command=self.callbacks['export'], fg_color="#27ae60",
                     height=45, font=ctk.CTkFont(size=13)).grid(
                         row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(control_frame, text="🗑️ Clear Logs",
                     command=self.callbacks['clear'], fg_color="#e74c3c",
                     height=45, font=ctk.CTkFont(size=13)).grid(
                         row=0, column=2, padx=10, pady=10, sticky="ew")
        
        # Log textbox
        self.log_textbox = ctk.CTkTextbox(self.tab, wrap="none",
                                         font=ctk.CTkFont(family="Courier", size=10))
        self.log_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
    
    def update_log(self, text):
        """Update log display"""
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.insert("1.0", text)


class ChartTab:
    """Chart visualization tab"""
    
    def __init__(self, parent):
        self.parent = parent
        self.tab = parent.add(f"{EMOJI['chart']} Chart")
        self.setup()
    
    def setup(self):
        """Setup chart tab"""
        self.tab.grid_columnconfigure(0, weight=1)
        self.tab.grid_rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 6), dpi=100, facecolor='#1e1e1e')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#2b2b2b')
        self.ax.set_title('Real-time Detection Statistics', 
                         color='white', fontsize=16, weight='bold')
        self.ax.set_xlabel('Detection Count', color='white', fontsize=12)
        self.ax.set_ylabel('Total Count', color='white', fontsize=12)
        self.ax.tick_params(colors='white', labelsize=10)
        for spine in self.ax.spines.values():
            spine.set_color('white')
        self.ax.grid(True, alpha=0.2, color='gray', linestyle='--')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
        
        self.line_accept, = self.ax.plot([], [], 'g-', label='ACCEPT', 
                                         linewidth=3, marker='o', markersize=4)
        self.line_reject, = self.ax.plot([], [], 'r-', label='REJECT',
                                         linewidth=3, marker='o', markersize=4)
        self.ax.legend(loc='upper left', facecolor='#2b2b2b', edgecolor='white',
                      labelcolor='white', fontsize=12, framealpha=0.9)
    
    def update_chart(self, x_data, accept_data, reject_data):
        """Update chart with new data"""
        try:
            self.line_accept.set_data(x_data, accept_data)
            self.line_reject.set_data(x_data, reject_data)
            
            if x_data:
                self.ax.set_xlim(0, max(x_data) + 1)
                max_y = max(max(accept_data + reject_data, default=1), 5)
                self.ax.set_ylim(0, max_y + 2)
            
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating chart: {e}")