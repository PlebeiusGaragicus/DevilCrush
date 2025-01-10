import sys
import platform
import time
import logging
logger = logging.getLogger()

import pygame

from src.config import *



class App(Singleton):
    viewmanager: ViewManager = None
    running: bool = None


    @classmethod
    def get_instance(cls) -> 'App':
        if cls._instance:
            return cls._instance
        else:
            return cls.configure_instance()

    @classmethod
    def configure_instance(cls) -> 'App':
        if cls._instance:
            raise Exception("Instance already configured")
        app = cls.__new__(cls)
        cls._instance = app

        setup_logging()


        #### setup app variables
        pygame.init()
        pygame.font.init() # really needed?
        app.clock = pygame.time.Clock()



        _info = pygame.display.Info()
        app.width, app.height = _info.current_w, _info.current_h

        if platform.system() == "Darwin":
            app.height -= 34 # TODO - this is a hack for the macbook air menu bar / camera cutout

            app.screen = pygame.display.set_mode((app.width, app.height), flags=pygame.NOFRAME | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SRCALPHA)
            # this 'hack' ensures that the newly created window becomes active
            time.sleep(0.1)
            pygame.display.toggle_fullscreen()
            time.sleep(0.1)
            pygame.display.toggle_fullscreen()
        else:
            app.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN | pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF)


        logger.debug("Display size: %s x %s", app.width, app.height)

        pygame.display.set_allow_screensaver(False)


        # global APP_SCREEN
        globals.APP_SCREEN = app.screen
        # global SCREEN_WIDTH
        globals.SCREEN_WIDTH = app.width
        # global SCREEN_HEIGHT
        globals.SCREEN_HEIGHT = app.height

        pygame.display.set_caption( "Devil Crush!" )

        #### setup views
        app.viewmanager = ViewManager()
        from fishyfrens.view.splash import SplashScreenView
        app.viewmanager.add_view("splash_screen", SplashScreenView())
        from fishyfrens.view.gameplay import GameplayView
        app.viewmanager.add_view("gameplay", GameplayView())


        return cls._instance


    def start(self):
        logger.debug("App.start()")

        self.viewmanager.run_view("splash_screen")

        self.running = True
        while self.running:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        continue
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.running = False
                        continue

                    self.viewmanager.handle_event(event)

                self.viewmanager.update()
                self.viewmanager.draw()

                # pygame.display.update() # TODO is this needed?
                pygame.display.flip()
                self.clock.tick(FPS)

            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt")
                self.running = False

            except NotImplementedError as e:
                logger.exception(e)
                self.running = False

            except Exception as e:
                # TODO - do something useful and cool here.. make my own exception view like the seedsigner!
                logger.exception(e)
                self.running = False

        pygame.quit()
        sys.exit()

    def stop(self):
        self.running = False
        # pygame.quit()
        # sys.exit()
