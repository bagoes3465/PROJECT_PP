"""
UI Components - Base classes and reusable components
"""
import customtkinter as ctk
from Core.constants import EMOJI


class ToastNotification:
    """Toast notification system"""
    
    @staticmethod
    def show(parent, message, alert_type="info"):
        """
        Show toast notification
        
        Args:
            parent: Parent widget
            message: Message to display
            alert_type: "reject", "accept", or "info"
        """
        try:
            colors = {
                "reject": ("#e74c3c", "#c0392b"),
                "accept": ("#2ecc71", "#27ae60"),
                "info": ("#3498db", "#2980b9")
            }
            bg_color, border_color = colors.get(alert_type, colors["info"])
            
            # Create toast container
            toast_container = ctk.CTkFrame(parent, fg_color="transparent")
            toast_container.place(relx=0.5, rely=0.1, anchor="n")
            
            # Shadow frame
            shadow = ctk.CTkFrame(toast_container, fg_color="#000000", 
                                corner_radius=12, border_width=0)
            shadow.pack(padx=3, pady=3)
            
            # Main toast frame
            toast_frame = ctk.CTkFrame(shadow, fg_color=bg_color, 
                                    corner_radius=10, border_width=3,
                                    border_color=border_color)
            toast_frame.pack()
            
            # Icon
            icons = {
                "reject": "🚨",
                "accept": "✅",
                "info": "ℹ️"
            }
            icon = icons.get(alert_type, "ℹ️")
            
            # Content
            content_frame = ctk.CTkFrame(toast_frame, fg_color="transparent")
            content_frame.pack(padx=20, pady=15)
            
            ctk.CTkLabel(content_frame, text=icon, 
                        font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
            
            ctk.CTkLabel(content_frame, text=message, 
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color="white", wraplength=400).pack(side="left")
            
            # Close button
            close_btn = ctk.CTkButton(content_frame, text="✕", width=30, height=30,
                                    fg_color="transparent", hover_color=border_color,
                                    font=ctk.CTkFont(size=16, weight="bold"),
                                    command=lambda: ToastNotification._close(toast_container))
            close_btn.pack(side="left", padx=(15, 0))
            
            # Auto hide
            parent.after(4000, lambda: ToastNotification._close(toast_container))
            
        except Exception as e:
            print(f"Error showing toast: {e}")
    
    @staticmethod
    def _close(widget):
        """Close toast"""
        try:
            if widget.winfo_exists():
                widget.destroy()
        except:
            pass


class StatCard(ctk.CTkFrame):
    """Reusable stat card component"""
    
    def __init__(self, parent, title, value, emoji, color, **kwargs):
        super().__init__(parent, fg_color=color, corner_radius=8, **kwargs)
        
        self.label = ctk.CTkLabel(
            self,
            text=f"{emoji} {title}\n{value}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.label.pack(padx=20, pady=10)
    
    def update_value(self, value):
        """Update stat value"""
        current_text = self.label.cget("text")
        lines = current_text.split("\n")
        if len(lines) >= 2:
            lines[1] = str(value)
            self.label.configure(text="\n".join(lines))


class SettingSlider(ctk.CTkFrame):
    """Reusable slider setting component"""
    
    def __init__(self, parent, title, from_, to, initial_value, command, unit="", **kwargs):
        super().__init__(parent, fg_color="#2b2b2b", **kwargs)
        
        ctk.CTkLabel(self, text=title,
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        self.slider = ctk.CTkSlider(self, from_=from_, to=to, 
                                   command=self._on_change, height=20)
        self.slider.set(initial_value)
        self.slider.pack(pady=10, padx=20, fill="x")
        
        self.value_label = ctk.CTkLabel(self, 
                                       text=f"{initial_value}{unit}",
                                       font=ctk.CTkFont(size=16, weight="bold"))
        self.value_label.pack(pady=(0, 15))
        
        self.unit = unit
        self.external_command = command
    
    def _on_change(self, value):
        """Handle slider change"""
        if self.unit == " px" or self.unit == "±" or "pixel" in self.unit:
            display_value = int(value)
        else:
            display_value = value
        
        self.value_label.configure(text=f"{display_value}{self.unit}")
        
        if self.external_command:
            self.external_command(value)
    
    def get(self):
        """Get current value"""
        return self.slider.get()
    
    def set(self, value):
        """Set value"""
        self.slider.set(value)


class InfoPanel(ctk.CTkFrame):
    """Reusable info panel component"""
    
    def __init__(self, parent, title, text, **kwargs):
        super().__init__(parent, **kwargs)
        
        ctk.CTkLabel(self, text=title,
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        ctk.CTkLabel(self, text=text, justify="left",
                    font=ctk.CTkFont(size=16)).pack(pady=20, padx=20, anchor="w")
        