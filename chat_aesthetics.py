import shutil

BRIGHT_RED="\033[91m"
BRIGHT_YELLOW = "\033[93m"
GREY = "\033[90m"
BRIGHT_CYAN= "\033[96m"
WHITE="\033[37m"   
BRIGHT_GREEN = "\033[92m"
RESET = "\033[0m"

def left():
    print(BRIGHT_RED+"You"+GREY+" > ", end="")
# Example usage
def right(text,l,m,r):
    # Get the width of the terminal window
    terminal_width = shutil.get_terminal_size().columns
    # Calculate the starting position for the text (far right)
    start_position = terminal_width - len(text)
    # Print spaces to move to the far right of the terminal
    print("\r"+" " * (start_position), end="")
    print(BRIGHT_CYAN+ str(l) + RESET, end="")
    print(GREY + str(m) + RESET, end="")
    print(WHITE+ str(r),sep="")
    print(BRIGHT_RED+"\nYou "+GREY+"> ",end="")

def centre(text):
    # Get the width of the terminal window
    terminal_width = shutil.get_terminal_size().columns
    # Calculate the starting position for the text
    start_position = (terminal_width - len(text)) // 2
    # Print spaces to center the text
    print(" " * start_position, end="")
    # Print the text
    print(text)

def default():
    print(RESET)

def terminal_size():
    return shutil.get_terminal_size().columns