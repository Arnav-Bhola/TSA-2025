import pygame
import os

def round_image(image, radius):
    """Rounds the corners of an image using a mask."""
    size = image.get_size()
    mask = pygame.Surface(size, pygame.SRCALPHA)
    
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, *size), border_radius=radius)
    rounded_image = image.copy()
    rounded_image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    
    return rounded_image

class Shop(pygame.sprite.Sprite):
    def __init__(self, screen, font, items, rect):
        super().__init__()
        self.screen = screen
        self.font = font
        self.title_font = pygame.font.Font(None, 40)
        self.desc_font = pygame.font.Font(None, 24)
        self.items = items
        self.rect = rect
        self.image = pygame.Surface(rect.size, pygame.SRCALPHA)
        
        # Animation states
        self.is_open = False
        self.is_animating = False
        self.animation_speed = 15
        self.hidden_y = screen.get_height()
        self.shown_y = (screen.get_height() - self.rect.height) // 2
        self.rect.y = self.hidden_y
        
        # Shop display variables
        self.current_page = 0
        self.items_per_page = 3
        self.hovered_item = None
        self.icon_size = 80
        self.icon_padding = 30
        self.total_pages = (len(items) + self.items_per_page - 1) // self.items_per_page
        
        # Load assets
        self.icons = self._load_icons()
        self.arrow_left, self.arrow_right = self._load_arrows()
        self.arrow_rect_left = pygame.Rect(20, rect.height//2 - 25, 50, 50)
        self.arrow_rect_right = pygame.Rect(rect.width - 70, rect.height//2 - 25, 50, 50)
        
        # Visual effects
        self.hovering_left = False
        self.hovering_right = False
        self.last_hovered = None
        
    def _load_icons(self):
        """Load all item icons from assets"""
        icons = {}
        for i, item_key in enumerate(self.items.keys(), start=1):
            try:
                icon_path = f"assets/images/upgrades/upgrade{i}.png"
                icon = pygame.image.load(icon_path).convert_alpha()
                icon = round_image(icon, 20)  # Round the corners of the icon
                icons[item_key] = pygame.transform.scale(icon, (self.icon_size, self.icon_size))
            except:
                # Fallback if image missing
                icons[item_key] = self._create_fallback_icon(item_key)
        return icons
    
    def _load_arrows(self):
        """Load navigation arrows with fallbacks"""
        try:
            left = pygame.image.load('assets/images/arrow_left.svg').convert_alpha()
            right = pygame.image.load('assets/images/arrow_right.svg').convert_alpha()
            return pygame.transform.scale(left, (50, 50)), pygame.transform.scale(right, (50, 50))
        except:
            # Create simple arrows if images missing
            left = pygame.Surface((50, 50), pygame.SRCALPHA)
            right = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.polygon(left, (200,200,200), [(35,15), (15,25), (35,35)])
            pygame.draw.polygon(right, (200,200,200), [(15,15), (35,25), (15,35)])
            return left, right
    
    def _create_fallback_icon(self, name):
        """Create placeholder icon if image missing"""
        icon = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        pygame.draw.rect(icon, (100,100,100,150), (0,0,self.icon_size,self.icon_size), border_radius=10)
        text = self.font.render(name[:4], True, (255,255,255))
        icon.blit(text, (self.icon_size//2 - text.get_width()//2, self.icon_size//2 - text.get_height()//2))
        return icon
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        return lines
    
    def draw(self, coin_count):
        self.image.fill((0,0,0,0))
        
        # Background
        bg = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg, (30,30,30,200), bg.get_rect(), border_radius=20)
        self.image.blit(bg, (0,0))
        
        # Calculate total content height
        content_height = (
            40 +  # title space
            self.icon_size +  # icons
            40 +   # price space
            80 +   # description panel
            20     # bottom padding
        )
        
        # Vertical offset to center everything
        vertical_offset = (self.rect.height - content_height) // 2
        
        # Title (centered horizontally, positioned with vertical offset)
        title = self.title_font.render("UPGRADE SHOP", True, (255,255,255))
        self.image.blit(title, (self.rect.width//2 - title.get_width()//2, vertical_offset))
        
        # Calculate items area (centered horizontally, positioned with vertical offset)
        total_width = (self.items_per_page * self.icon_size) + ((self.items_per_page - 1) * self.icon_padding)
        start_x = (self.rect.width - total_width) // 2
        start_y = vertical_offset + 60  # Below title
        
        # Get current page items
        item_keys = list(self.items.keys())
        page_items = item_keys[self.current_page*self.items_per_page : (self.current_page+1)*self.items_per_page]
        
        # Draw items
        mouse_pos = pygame.mouse.get_pos()
        shop_pos = (self.rect.x, self.rect.y)
        self.hovered_item = None
        
        for i, item_key in enumerate(page_items):
            item = self.items[item_key]
            x = start_x + i * (self.icon_size + self.icon_padding)
            y = start_y
            
            # Hover detection
            icon_rect = pygame.Rect(shop_pos[0]+x, shop_pos[1]+y, self.icon_size, self.icon_size)
            if icon_rect.collidepoint(mouse_pos):
                self.hovered_item = item_key
                # Glow effect
                glow = pygame.Surface((self.icon_size+10, self.icon_size+10), pygame.SRCALPHA)
                pygame.draw.rect(glow, (255,255,255,50), glow.get_rect(), border_radius=15)
                self.image.blit(glow, (x-5,y-5))
            
            # Draw icon
            self.image.blit(self.icons[item_key], (x,y))
            
            # Price
            price_text = self.font.render(f"${item['price']}", True, (255,255,255))
            self.image.blit(price_text, (x + self.icon_size//2 - price_text.get_width()//2, y + self.icon_size + 5))
        
        # Description panel (centered horizontally, positioned with vertical offset)
        if self.hovered_item:
            item = self.items[self.hovered_item]
            desc_width = self.rect.width - 40
            desc_height = 80
            desc_x = 20
            desc_y = start_y + self.icon_size + 30  # Below prices
            
            # Background
            desc_bg = pygame.Surface((desc_width, desc_height), pygame.SRCALPHA)
            pygame.draw.rect(desc_bg, (50,50,50,150), desc_bg.get_rect(), border_radius=10)
            self.image.blit(desc_bg, (desc_x, desc_y))
            
            # Item name
            name = self.hovered_item.replace("_", " ").title()
            name_text = self.title_font.render(name, True, (255,255,255))
            self.image.blit(name_text, (desc_x + desc_width//2 - name_text.get_width()//2, desc_y + 10))
            
            # Description
            desc_lines = self._wrap_text(item['effect'], self.desc_font, desc_width - 20)
            for i, line in enumerate(desc_lines):
                desc_text = self.desc_font.render(line, True, (220,220,220))
                self.image.blit(desc_text, (desc_x + desc_width//2 - desc_text.get_width()//2, desc_y + 40 + i * 20))
        
        # Navigation arrows (position adjusted for vertical centering)
        self.arrow_rect_left = pygame.Rect(20, self.rect.height//2 - 25, 50, 50)
        self.arrow_rect_right = pygame.Rect(self.rect.width - 70, self.rect.height//2 - 25, 50, 50)
        self._draw_arrows(mouse_pos, shop_pos)
    
    def _draw_arrows(self, mouse_pos, shop_pos):
        """Draw and handle navigation arrows"""
        # Left arrow
        left_arrow = self.arrow_left.copy()
        if self.arrow_rect_left.move(shop_pos).collidepoint(mouse_pos):
            self.hovering_left = True
            left_arrow.fill((255,255,255,150), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            self.hovering_left = False
        
        # Right arrow
        right_arrow = self.arrow_right.copy()
        if self.arrow_rect_right.move(shop_pos).collidepoint(mouse_pos):
            self.hovering_right = True
            right_arrow.fill((255,255,255,150), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            self.hovering_right = False
        
        # Only show arrows if there are multiple pages
        if self.total_pages > 1:
            if self.current_page > 0:
                self.image.blit(left_arrow, self.arrow_rect_left)
            if self.current_page < self.total_pages - 1:
                self.image.blit(right_arrow, self.arrow_rect_right)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                self.toggle()
            elif event.key == pygame.K_LEFT and self.current_page > 0:
                self.current_page -= 1
            elif event.key == pygame.K_RIGHT and self.current_page < self.total_pages - 1:
                self.current_page += 1
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            shop_pos = (self.rect.x, self.rect.y)
            
            if self.hovering_left and self.current_page > 0:
                self.current_page -= 1
            elif self.hovering_right and self.current_page < self.total_pages - 1:
                self.current_page += 1
    
    def toggle(self):
        if not self.is_animating:
            self.is_open = not self.is_open
            self.is_animating = True
    
    def update_animation(self):
        if self.is_animating:
            if self.is_open:
                self.rect.y = max(self.shown_y, self.rect.y - self.animation_speed)
                if self.rect.y == self.shown_y:
                    self.is_animating = False
            else:
                self.rect.y = min(self.hidden_y, self.rect.y + self.animation_speed)
                if self.rect.y == self.hidden_y:
                    self.is_animating = False
    
    def update(self, coin_count):
        self.update_animation()
        self.draw(coin_count)