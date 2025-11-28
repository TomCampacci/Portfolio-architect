# theme_colors.py - Light Premium Theme
# Professional color palette for Portfolio Manager

class LightPremiumTheme:
    """
    Light Premium Theme - Clean, professional, trustworthy
    Inspired by major financial institutions like Fidelity
    """
    
    # Backgrounds
    MAIN_BG = "#F5F7FA"              # Main window background - soft blue-gray
    SECONDARY_BG = "#FFFFFF"          # Secondary panels - pure white
    CARD_BG = "#FFFFFF"               # Card backgrounds - pure white
    
    # Headers and Panels
    HEADER = "#003B5C"                # Main header - deep navy blue
    PANEL_HEADER = "#004D73"          # Panel headers - slightly lighter navy
    
    # Accent Colors
    PRIMARY = "#0073CF"               # Primary actions - bright professional blue
    SUCCESS = "#28A745"               # Success/validation - green
    WARNING = "#FFC107"               # Warning/attention - amber
    ERROR = "#DC3545"                 # Error/danger - red
    
    # Text Colors
    TEXT_PRIMARY = "#212529"          # Main text - near black
    TEXT_SECONDARY = "#6C757D"        # Secondary text - gray
    TEXT_MUTED = "#ADB5BD"            # Muted text - light gray
    TEXT_ON_DARK = "#FFFFFF"          # Text on dark backgrounds - white
    
    # Borders and Separators
    BORDER = "#DEE2E6"                # Standard borders - light gray
    BORDER_FOCUS = "#0073CF"          # Focused borders - primary blue
    DIVIDER = "#E9ECEF"               # Subtle dividers
    
    # Input Fields
    INPUT_BG = "#FFFFFF"              # Input background - white
    INPUT_BG_FOCUS = "#F8F9FA"        # Input focused - very light gray
    INPUT_BG_DISABLED = "#E9ECEF"     # Input disabled - light gray
    INPUT_PLACEHOLDER = "#ADB5BD"     # Placeholder text - muted
    
    # Status Colors
    STATUS_PENDING = "#6C757D"        # Pending - gray
    STATUS_VALIDATING = "#FFC107"     # Validating - amber
    STATUS_SUCCESS = "#28A745"        # Success - green
    STATUS_ERROR = "#DC3545"          # Error - red
    
    # Button Colors
    BTN_PRIMARY_BG = "#0073CF"        # Primary button background
    BTN_PRIMARY_HOVER = "#005FA3"     # Primary button hover
    BTN_SUCCESS_BG = "#28A745"        # Success button background
    BTN_SUCCESS_HOVER = "#218838"     # Success button hover
    BTN_WARNING_BG = "#FFC107"        # Warning button background
    BTN_WARNING_HOVER = "#E0A800"     # Warning button hover
    BTN_DANGER_BG = "#DC3545"         # Danger button background
    BTN_DANGER_HOVER = "#C82333"      # Danger button hover
    BTN_SECONDARY_BG = "#6C757D"      # Secondary button background
    BTN_SECONDARY_HOVER = "#5A6268"   # Secondary button hover
    
    # Hover and Active States
    HOVER_BG = "#F8F9FA"              # Hover background - very light gray
    ACTIVE_BG = "#E9ECEF"             # Active/selected background
    
    # Shadows and Elevation
    SHADOW_SM = "#00000010"           # Small shadow (10% opacity)
    SHADOW_MD = "#00000020"           # Medium shadow (20% opacity)
    SHADOW_LG = "#00000030"           # Large shadow (30% opacity)
    
    # Special Colors
    HIGHLIGHT = "#E7F3FF"             # Highlight background - light blue
    INFO = "#17A2B8"                  # Info - cyan
    
    # Chart/Graph Colors (for consistency)
    CHART_POSITIVE = "#28A745"        # Positive values - green
    CHART_NEGATIVE = "#DC3545"        # Negative values - red
    CHART_NEUTRAL = "#0073CF"         # Neutral - blue
    
    @classmethod
    def get_all_colors(cls):
        """Return dictionary of all theme colors"""
        return {
            name: value for name, value in vars(cls).items()
            if not name.startswith('_') and isinstance(value, str) and value.startswith('#')
        }


# Convenience aliases for shorter code
T = LightPremiumTheme


