"""
Camera Image Processing Module
Optimized for real-time egg detection
"""
import cv2
import numpy as np


class CameraProcessor:
    """Real-time image enhancement processor"""
    
    def __init__(self):
        # Basic settings
        self.brightness = 0
        self.contrast = 1.0
        self.sharpness = 0.0
        self.gamma = 1.0
        
        # Advanced settings
        self.enable_clahe = False
        self.enable_denoise = False
        self.enable_white_balance = False
        
        # Performance
        self.target_resolution = (640, 480)
        self.enable_processing = True
        
        # CLAHE object
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    
    def process_frame(self, frame):
        """
        Process single frame with all enabled enhancements
        
        Args:
            frame: BGR image from camera
            
        Returns:
            enhanced frame
        """
        if not self.enable_processing:
            return frame
        
        enhanced = frame.copy()
        
        # 1. Resize if needed
        if enhanced.shape[:2][::-1] != self.target_resolution:
            enhanced = cv2.resize(enhanced, self.target_resolution)
        
        # 2. Denoising (if enabled)
        if self.enable_denoise:
            enhanced = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
        
        # 3. White Balance (if enabled)
        if self.enable_white_balance:
            enhanced = self._auto_white_balance(enhanced)
        
        # 4. CLAHE (if enabled)
        if self.enable_clahe:
            enhanced = self._apply_clahe(enhanced)
        
        # 5. Brightness & Contrast
        if self.brightness != 0 or self.contrast != 1.0:
            enhanced = self._adjust_brightness_contrast(enhanced)
        
        # 6. Gamma Correction
        if self.gamma != 1.0:
            enhanced = self._adjust_gamma(enhanced)
        
        # 7. Sharpness
        if self.sharpness > 0:
            enhanced = self._apply_sharpening(enhanced)
        
        return enhanced
    
    def _adjust_brightness_contrast(self, img):
        """Adjust brightness and contrast"""
        # Convert to float for better precision
        img_float = img.astype(np.float32)
        
        # Apply contrast and brightness
        img_float = img_float * self.contrast + self.brightness
        
        # Clip values to valid range
        img_float = np.clip(img_float, 0, 255)
        
        return img_float.astype(np.uint8)
    
    def _adjust_gamma(self, img):
        """Apply gamma correction"""
        inv_gamma = 1.0 / self.gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 
                         for i in range(256)]).astype(np.uint8)
        return cv2.LUT(img, table)
    
    def _apply_sharpening(self, img):
        """Apply sharpening filter"""
        # Gaussian blur
        blurred = cv2.GaussianBlur(img, (0, 0), 3)
        
        # Sharpening
        sharpened = cv2.addWeighted(img, 1.0 + self.sharpness, 
                                   blurred, -self.sharpness, 0)
        
        return sharpened
    
    def _apply_clahe(self, img):
        """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)"""
        # Convert to LAB color space
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        l = self.clahe.apply(l)
        
        # Merge and convert back
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    def _auto_white_balance(self, img):
        """Simple auto white balance using gray world assumption"""
        result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])
        
        result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
        result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
        
        result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
        return result
    
    def set_brightness(self, value):
        """Set brightness (-50 to +50)"""
        self.brightness = max(-50, min(50, value))
    
    def set_contrast(self, value):
        """Set contrast (0.5 to 3.0)"""
        self.contrast = max(0.5, min(3.0, value))
    
    def set_sharpness(self, value):
        """Set sharpness (0 to 2.0)"""
        self.sharpness = max(0, min(2.0, value))
    
    def set_gamma(self, value):
        """Set gamma (0.5 to 2.0)"""
        self.gamma = max(0.5, min(2.0, value))
    
    def set_resolution(self, width, height):
        """Set target resolution"""
        self.target_resolution = (width, height)
    
    def toggle_clahe(self, enabled):
        """Toggle CLAHE"""
        self.enable_clahe = enabled
    
    def toggle_denoise(self, enabled):
        """Toggle denoising"""
        self.enable_denoise = enabled
    
    def toggle_white_balance(self, enabled):
        """Toggle white balance"""
        self.enable_white_balance = enabled
    
    def toggle_processing(self, enabled):
        """Toggle all processing"""
        self.enable_processing = enabled
    
    def reset_to_default(self):
        """Reset all settings to default"""
        self.brightness = 0
        self.contrast = 1.0
        self.sharpness = 0.0
        self.gamma = 1.0
        self.enable_clahe = False
        self.enable_denoise = False
        self.enable_white_balance = False
        self.enable_processing = True
    
    def get_settings_dict(self):
        """Get current settings as dictionary"""
        return {
            'brightness': self.brightness,
            'contrast': self.contrast,
            'sharpness': self.sharpness,
            'gamma': self.gamma,
            'enable_clahe': self.enable_clahe,
            'enable_denoise': self.enable_denoise,
            'enable_white_balance': self.enable_white_balance,
            'enable_processing': self.enable_processing,
            'target_resolution': self.target_resolution
        }
    
    def load_settings_dict(self, settings):
        """Load settings from dictionary"""
        self.brightness = settings.get('brightness', 0)
        self.contrast = settings.get('contrast', 1.0)
        self.sharpness = settings.get('sharpness', 0.0)
        self.gamma = settings.get('gamma', 1.0)
        self.enable_clahe = settings.get('enable_clahe', False)
        self.enable_denoise = settings.get('enable_denoise', False)
        self.enable_white_balance = settings.get('enable_white_balance', False)
        self.enable_processing = settings.get('enable_processing', True)
        self.target_resolution = tuple(settings.get('target_resolution', (640, 480)))