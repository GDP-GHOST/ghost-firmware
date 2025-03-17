class Style():
  RED = "\033[31m"
  GREEN = "\033[32m"
  YELLOW = '\033[33m' 
  BLUE = "\033[34m"
  RESET = "\033[0m"

# Example Usage: print(f"{Messages.ERROR} Test Error")
class Messages():
  ERROR = f"{Style.RED}[ERROR]{Style.RESET}"
  WARNING = f"{Style.RED}[WARNING]{Style.RESET}"
  SUCCESS = f"{Style.GREEN}[SUCCESS]{Style.RESET}"
  LOG = f"{Style.BLUE}[LOG]{Style.RESET}"