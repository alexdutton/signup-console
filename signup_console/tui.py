import curses
import functools
import time
import Queue
import pyfiglet

class TUI(object):
    delay = 0.07
    def __init__(self, ):
        self.scr = curses.initscr()
        self.queue = Queue.Queue()
        self.loading = False
        self.waiting_to_clear = None

    def start(self):
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        self.scr.keypad(1)
        self.scr.nodelay(1)

        fig = pyfiglet.Figlet(font='standard')
        t = fig.renderText('RAFFLE!')
        lines = t.split('\n')
        width = max(map(len, lines))
        h, w = self.scr.getmaxyx()
        x = (w - width) / 2
        for y, line in enumerate(lines, 1):
            self.scr.addstr(y, x, line)
        self.scr.refresh()


    def addstr(self, y, x, str, attrs=0):
        self.queue.put(functools.partial(self.scr.addstr, y, x, str[0], attrs))
        for ch in str[1:]:
            self.queue.put(functools.partial(self.scr.addstr, ch))

    def loop(self, on_input):
        buffer = []
        while True:
            try:
                f = self.queue.get(timeout=self.delay)
            except Queue.Empty:
                ch = self.scr.getch()
                if ch == ord('\n'):
                    on_input(''.join(buffer))
                    buffer[:] = []
                    continue
                elif 1 <= ch < 255:
                    buffer.append(chr(ch))
                    continue
            else:
                f()
                self.scr.refresh()
            time.sleep(self.delay)

    def await_input(self, on_input, finish):
        buffer = []
        while not finish.is_set():
            c = self.scr.getch()
            if c == ord('\n'):
                on_input(''.join(buffer))
                buffer[:] = []
            elif 1 <= c < 255:
                buffer.append(chr(c))

    def show_result(self, result, done):
        self.queue.empty()
        self.queue.put(functools.partial(self.scr.move, 7, 0))
        self.queue.put(self.scr.clrtobot)
        h, w = self.scr.getmaxyx()
        #self.scr.erase()
        #self.addstr(0, 0, str(result))
        if result.get('person'):
            name = result['person']['title']
            self.addstr(8, (w - 6) / 2, 'Hello!')
            self.addstr(10, (w - len(name)) / 2, name)

        status = result['status']
        if isinstance(status, list):
            status = status[0]

        if status == 'added-already':
            status = 'You are already entered!'
        elif status == 'added':
            status = 'You are now entered for the raffle!'
        elif status == 'not-found':
            status = "We couldn't work out who you are :-("
        else:
            status = '???'

        self.addstr(13, (w - len(status)) / 2, status)

        self.addstr(h-1, 0, '-' * (w-1))
        self.queue.put(functools.partial(self.scr.move, 7, 0))
        self.queue.put(self.scr.clrtobot)

        if done:
            self.queue.put(done)


    def finish(self):
        curses.nocbreak()
        self.scr.keypad(0)
        curses.echo()
        curses.endwin()

    def set_loading(self, value):
        self.loading = value