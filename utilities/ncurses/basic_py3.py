import curses
import time

def test():
    curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr = curses.initscr()
    stdscr.keypad(True)    
    stdscr.addstr(5, 10, "Reverse Mode",
              curses.A_REVERSE)
    stdscr.addstr(10, 20, "Bold Mode",
              curses.A_BOLD)
    stdscr.refresh()  
    c = stdscr.getkey()  
    
    stdscr.addstr(15, 30, "key is  "+c,
              curses.A_UNDERLINE)

    stdscr.refresh()
    time.sleep(3)    
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    
    
test()    
