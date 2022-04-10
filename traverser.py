import filetree
import threading as thread
import pygame
pygame.init()

START = "C:/"
SIZES = ("B", "KB", "MB", "GB", "TB", "PB")

def file_size(n):
    size = 0
    while n > 1000:
        n /= 1000
        size += 1

    return str(round(n, 1)) + SIZES[size]

def centre_text(text, point, surface):
    surface.blit(text, (point[0]-(text.get_width()/2), point[1]-(text.get_height()/2)))


class TreeTraverser:
    
    def recalculate(self):
        self.__child_width = max(self.__win.get_width() / len(self.__node.get_children()), 300)
        self.__node_x = (len(self.__node.get_children()) // 2) * self.__child_width
        self.__x_offset = self.__node_x + (self.__child_width / 2) - (self.__win.get_width() / 2)
    
    def move_to_child(self, n):
        if 0 <= n < len(self.__node.get_children()) and len(self.__node.get_children()[n].get_children()) > 0:
            self.__traversal_stack.append(n)
            self.__node = self.__node.get_children()[n]
            self.recalculate()

    def move_to_parent(self):
        if len(self.__traversal_stack) > 0:
            self.__traversal_stack.pop()
            
            self.__node = self.__tree
            for index in self.__traversal_stack:
                self.__node = self.__node.get_children()[index]

            self.recalculate()

    def concurrent_create_tree(self, start):
        result = []
        t = thread.Thread(target = filetree.create_file_tree, args = (start,))
        t.start()
        t.join()
        self.__reading = False

    def generate_tree(self, start):
        result = []

        t = thread.Thread(target = self.concurrent_create_tree, args = (start,))
        t.start()
        
        self.__reading = True
        while self.__reading:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__run = False
                    break

            if not self.__run:
                pygame.quit()
                quit()
                break
                    
            self.__win.fill((0, 0, 0))
            centre_text(
                self.__read_font.render("Generating file tree...", True, (255, 255, 255)),
                (self.__win.get_width() / 2, (self.__win.get_height() / 2) - 40),
                self.__win
            )
            centre_text(
                self.__read_font.render(filetree.current_file, True, (255, 255, 255)),
                (self.__win.get_width() / 2, (self.__win.get_height() / 2) + 40),
                self.__win
            )
            pygame.display.update()

        t.join()
        
    def __init__(self, start):
        self.__run = True
        self.__clock = pygame.time.Clock()
        self.__win = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
        self.__font = pygame.font.SysFont("Comic Sans MS", 14)
        self.__read_font = pygame.font.SysFont("Comic Sans MS", 20)
        self.__frame_count = 0
        self.__held_offset = 0
        self.__held_left = False
        self.__held_right = False
        self.__held_speed = 3
        
        self.__traversal_stack = [-1]
        self.generate_tree(start)
        self.__tree = filetree.tree
        self.move_to_parent()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[1] < self.__win.get_height() / 2:
                    self.move_to_parent()
                else:
                    self.move_to_child(int((event.pos[0] + self.__x_offset) / self.__child_width))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.__held_offset = self.__frame_count % self.__held_speed
                    self.__held_left = True
                    self.__held_right = False
                if event.key == pygame.K_d:
                    self.__held_offset = self.__frame_count % self.__held_speed
                    self.__held_right = True
                    self.__held_left = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.__held_left = False
                if event.key == pygame.K_d:
                    self.__held_right = False

            if event.type == pygame.WINDOWRESIZED:
                self.recalculate()


        if self.__frame_count % self.__held_speed == self.__held_offset:
            if self.__held_left:
                self.__x_offset -= self.__child_width
            if self.__held_right:
                self.__x_offset += self.__child_width
            

        self.__win.fill((10, 10, 10))
        
        centre_text(
            self.__font.render(self.__node.get_name(), True, (255, 255, 255)),
            (-self.__x_offset + self.__node_x + (self.__child_width / 2), 150),
            self.__win
        )

        centre_text(
            self.__font.render(file_size(self.__node.get_value()), True, (255, 255, 255)),
            (-self.__x_offset + self.__node_x + (self.__child_width / 2), 200),
            self.__win
        )

        pygame.draw.rect(
            self.__win,
            (255, 255, 255),
            (-self.__x_offset + 50 + self.__node_x, 50, self.__child_width - 100, 200),
            width = 2
        )

        for i, child in enumerate(self.__node.get_children()):
            centre_text(
                text = self.__font.render(child.get_name(), True, (255, 255, 255)),
                point = (-self.__x_offset + ((i + 0.5) * self.__child_width), 50 + (self.__win.get_height() / 2) + 100),
                surface = self.__win
            )
            
            centre_text(
                text = self.__font.render(file_size(child.get_value()), True, (255, 255, 255)),
                point = (-self.__x_offset + ((i + 0.5) * self.__child_width), 50 + (self.__win.get_height() / 2) + 150),
                surface = self.__win
            )

            pygame.draw.line(
                self.__win,
                (200, 200, 200),
                (-self.__x_offset + self.__node_x + (self.__child_width / 2), 250),
                (-self.__x_offset + ((i + 0.5) * self.__child_width), 50 + (self.__win.get_height() / 2))
            )
            
            pygame.draw.rect(
                self.__win,
                (255, 255, 255),
                (-self.__x_offset + 50 + (i * self.__child_width), 50 + (self.__win.get_height() / 2), self.__child_width - 100, 200),
                width = 2
            )

        pygame.display.update()

        self.__frame_count += 1

    def frame_delay(self):
        self.__clock.tick(30)

    def get_running(self):
        return self.__run


if __name__ == "__main__":
    traverser = TreeTraverser(START)
    while traverser.get_running():
        traverser.update()
        traverser.frame_delay()

    pygame.quit()
