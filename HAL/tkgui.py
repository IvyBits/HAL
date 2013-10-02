import Tkinter as tk
import ttk
from ScrolledText import ScrolledText
from tkFont import Font
from threading import Thread
import sys, os, io
from glob import glob
from getpass import getuser
from Queue import Queue, Empty


class Application(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.root = master
        self.grid(sticky='WENS')
        self.createWidgets()
        self.queue = Queue()
        
        self.after(100, self.update_console)
        Thread(target=self.bootstrap).start()
    
    def write(self, text):
        self.queue.put(text)
        sys.stdout.write(text)
    
    def clear(self):
        self.queue.put(None)
    
    def update_console(self):
        try:
            while True:
                line = self.queue.get_nowait()
                if line is None:
                    self.console.delete(1.0, 'end')
                else:
                    self.console.insert('end', str(line))
                self.console.see('end')
                self.console.update_idletasks()
        except Empty:
            pass
        self.after(100, self.update_console)
    
    def bootstrap(self):
        from HAL import HAL

        write = self.write
        
        write('Initializing Engine...')
        self.hal = HAL()
        write(' done\n')

        try:
            dirname = sys.argv[1]
        except IndexError:
            dirname = os.getcwd()

        def loadfiles(pattern, attr, name):
            engine = getattr(self.hal, attr)
            for file in glob(os.path.join(dirname, pattern)):
                write('%s Engine: Loading %s...' % (name, file))
                engine.load(io.open(file, encoding='utf-8'))
                write(' Done\n')
        loadfiles('*.gen', 'matrix', 'Matrix')
        loadfiles('*.mtx', 'general', 'General')
        loadfiles('*.rgx', 'regex', 'Regex')
        loadfiles('*.ow',  'oneword', 'One Word')
        write('\n')

        user = getuser()
        prompt = '-%s: '%user
        halpro = '-HAL: '
        length = max(len(prompt), len(halpro))
        prompt.ljust(length)
        halpro.ljust(length)
        self.prompt, self.halpro = prompt, halpro
        self.context = {'USERNAME': user}

        write(halpro + 'Hello %s. I am HAL %s.' % (user, self.hal.version) + '\n\n')

        self.entry.bind('<Return>', self.answer)
    
    def answer(self, e=None):
        write = self.write
        input = self.input.get()
        answer = self.hal.answer(input, self.context)
        write(self.prompt + input + '\n')
        write(self.halpro + answer + '\n\n')
        self.input.set('')
    
    def createWidgets(self):
        font_console = Font(family='Consolas', size=11)
        self.input = tk.StringVar()
        self.config(borderwidth=10)

        self.console = ScrolledText(self, font=font_console, state='normal')
        self.entry = ttk.Entry(self, textvariable=self.input, font=font_console)
        submit = ttk.Button(self, text='Submit')

        self.console.grid(columnspan=3, sticky='WENS')
        tk.LabelFrame(self, height=5).grid(row=1)
        self.entry.grid(row=2, sticky='WE')
        tk.LabelFrame(self, width=5).grid(row=2, column=1)
        submit.grid(row=2, column=2)
        submit['command'] = self.answer
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.wm_title('HAL')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)


def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()