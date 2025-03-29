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
    def __init__(self, screen, font, turtle, crab, rect):
        super().__init__()
        self.screen = screen
        self.font = font
        self.turtle = turtle
        self.crab = crab
        
        # Define shop items with absolute paths
        self.items = {
            "turtle_health": {
                "price": 20,
                "effect": "Add +1 health to Turtle",
                "action": self.upgrade_turtle_health,
                "icon": os.path.join("assets", "images", "crab.png"),
                "purchased": False
            },
            "crab_health": {
                "price": 20,
                "effect": "Add +1 health to Crab",
                "action": self.upgrade_crab_health,
                "icon": os.path.join("assets", "images", "turtle.png"),
                "purchased": False
            },
            "crab_damage": {
                "price": 30,
                "effect": "Double Crab's damage (One-time)",
                "action": self.upgrade_crab_damage,
                "icon": os.path.join("assets", "images","crab_scute.png"),
                "purchased": False
            }
        }
        
        self.title_font = pygame.font.Font(None, 40)
        self.desc_font = pygame.font.Font(None, 24)
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
        self.total_pages = (len(self.items) + self.items_per_page - 1) // self.items_per_page
        
        # Load assets
        self.icons = self._load_icons()
        self.arrow_left, self.arrow_right = self._load_arrows()
        self.arrow_rect_left = pygame.Rect(20, rect.height//2 - 25, 50, 50)
        self.arrow_rect_right = pygame.Rect(rect.width - 70, rect.height//2 - 25, 50, 50)
        
        # Visual effects
        self.hovering_left = False
        self.hovering_right = False
        self.last_hovered = None
        
    def upgrade_turtle_health(self, coin_count):
        if coin_count >= 20:
            self.turtle.health += 1
            return 20  # Return coins to deduct
        return 0
    
    def upgrade_crab_health(self, coin_count):
        if coin_count >= 20:
            self.crab.health += 1
            return 20  # Return coins to deduct
        return 0
    
    def upgrade_crab_damage(self, coin_count):
        if coin_count >= 30 and not self.items["crab_damage"]["purchased"]:
            self.crab.damage_multiplier = 2
            self.items["crab_damage"]["purchased"] = True
            self.items["crab_damage"]["effect"] = "Damage doubled!"  # Update description
            return 30
        return 0

    def _load_icons(self):
        """Load all item icons from assets with better error handling"""
        icons = {}
        for item_key, item in self.items.items():
            try:
                # Try loading from absolute path first
                if os.path.exists(item["icon"]):
                    icon = pygame.image.load(item["icon"]).convert_alpha()
                else:
                    # Try relative path if absolute fails
                    icon = pygame.image.load(os.path.join(*item["icon"].split(os.sep))).convert_alpha()
                
                icon = round_image(icon, 20)
                icons[item_key] = pygame.transform.scale(icon, (self.icon_size, self.icon_size))
            except Exception as e:
                print(f"Failed to load icon {item['icon']}: {e}")
                # Fallback if image missing
                icons[item_key] = self._create_fallback_icon(item_key)
        return icons
    
    def _load_arrows(self):
        """Load navigation arrows with fallbacks"""
        arrow_path = os.path.join("assets", "images", "upgrades")
        try:
            left = pygame.image.load(os.path.join(arrow_path, "arrow_left.svg")).convert_alpha()
            right = pygame.image.load(os.path.join(arrow_path, "arrow_right.svg")).convert_alpha()
            return pygame.transform.scale(left, (50, 50)), pygame.transform.scale(right, (50, 50))
        except Exception as e:
            print(f"Failed to load arrows: {e}")
            # Create simple arrows if images missing
            left = pygame.Surface((50, 50), pygame.SRCALPHA)
            right = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.polygon(left, (200,200,200), [(35,15), (15,25), (35,35)])
            pygame.draw.polygon(right, (200,200,200), [(15,15), (35,25), (15,35)])
            return left, right
    
    def _create_fallback_icon(self, name):
        """Create placeholder icon if image missing"""
        icon = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        color = (100,200,100) if "health" in name else (200,100,100)
        pygame.draw.rect(icon, (*color, 150), (0,0,self.icon_size,self.icon_size), border_radius=10)
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
        
        # Title
        title = self.title_font.render("UPGRADE SHOP", True, (255,255,255))
        self.image.blit(title, (self.rect.width//2 - title.get_width()//2, 20))
        
        # Coins
        coins_text = self.font.render(f"Coins: {coin_count}", True, (255,255,0))
        self.image.blit(coins_text, (self.rect.width - coins_text.get_width() - 20, 20))
        
        # Calculate items area
        total_width = (self.items_per_page * self.icon_size) + ((self.items_per_page - 1) * self.icon_padding)
        start_x = (self.rect.width - total_width) // 2
        start_y = 80
        
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
            
            # Draw icon (always draw, not just when hovered)
            if item_key == "crab_damage" and item["purchased"]:
                gray_icon = self.icons[item_key].copy()
                gray_icon.fill((100,100,100,150), special_flags=pygame.BLEND_RGBA_MULT)
                self.image.blit(gray_icon, (x,y))
            else:
                self.image.blit(self.icons[item_key], (x,y))
            
            # Price (show "PURCHASED" if one-time upgrade was bought)
            if item_key == "crab_damage" and item["purchased"]:
                price_text = self.font.render("PURCHASED", True, (100,255,100))
            else:
                price_text = self.font.render(f"${item['price']}", True, (255,255,255))
            self.image.blit(price_text, (x + self.icon_size//2 - price_text.get_width()//2, y + self.icon_size + 5))
        # Description panel
        if self.hovered_item:
            item = self.items[self.hovered_item]
            desc_width = self.rect.width - 40
            desc_height = 80
            desc_x = 20
            desc_y = start_y + self.icon_size + 30
            
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
        
        # Navigation arrows
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
    
    def handle_input(self, event, coin_count):
        """Handle shop input and return coins spent"""
        coins_spent = 0
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                self.toggle()
            elif event.key == pygame.K_LEFT and self.current_page > 0:
                self.current_page -= 1
            elif event.key == pygame.K_RIGHT and self.current_page < self.total_pages - 1:
                self.current_page += 1
            elif event.key == pygame.K_RETURN and self.hovered_item:
                # Purchase selected item
                item = self.items[self.hovered_item]
                # Don't allow repurchasing one-time upgrades
                if not (self.hovered_item == "crab_damage" and item["purchased"]):
                    coins_spent = item["action"](coin_count)
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            shop_pos = (self.rect.x, self.rect.y)
            
            if self.hovering_left and self.current_page > 0:
                self.current_page -= 1
            elif self.hovering_right and self.current_page < self.total_pages - 1:
                self.current_page += 1
            elif self.hovered_item:
                # Purchase hovered item
                item = self.items[self.hovered_item]
                # Don't allow repurchasing one-time upgrades
                if not (self.hovered_item == "crab_damage" and item["purchased"]):
                    coins_spent = item["action"](coin_count)
        
        return coins_spent
    
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