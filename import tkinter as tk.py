import tkinter as tk
import math

# Function to evaluate expression
def click(value):
    current = entry.get()
    entry.delete(0, tk.END)
    entry.insert(tk.END, current + str(value))

def clear():
    entry.delete(0, tk.END)

def calculate():
    try:
        expression = entry.get()

        expression = expression.replace("^", "**")
        expression = expression.replace("π", str(math.pi))
        expression = expression.replace("e", str(math.e))

        result = eval(expression, {
            "__builtins__": None
        }, {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log10,
            "ln": math.log,
            "factorial": math.factorial,
            "pi": math.pi,
            "e": math.e
        })

        entry.delete(0, tk.END)
        entry.insert(tk.END, str(result))
    except:
        entry.delete(0, tk.END)
        entry.insert(tk.END, "Error")

root = tk.Tk()
root.title("Scientific Calculator")
root.geometry("420x550")

entry = tk.Entry(root, font=("Arial", 22), justify="right")
entry.grid(row=0, column=0, columnspan=5, padx=10, pady=10, ipadx=8, ipady=10)

buttons = [
    ['7','8','9','/','sqrt('],
    ['4','5','6','*','^'],
    ['1','2','3','-','%'],
    ['0','.','+','(',')'],
    ['sin(','cos(','tan(','log(','ln('],
    ['π','e','factorial(','1/','C'],
    ['=']
]

for i, row in enumerate(buttons):
    for j, btn in enumerate(row):
        if btn == "=":
            tk.Button(root, text=btn, font=("Arial",18),
                      command=calculate).grid(row=i+1, column=0,
                      columnspan=5, sticky="nsew", padx=2, pady=2)
        elif btn == "C":
            tk.Button(root, text=btn, font=("Arial",18),
                      command=clear).grid(row=i+1, column=j,
                      sticky="nsew", padx=2, pady=2)
        elif btn == "1/":
            tk.Button(root, text=btn, font=("Arial",18),
                      command=lambda: click("1/")).grid(row=i+1,
                      column=j, sticky="nsew", padx=2, pady=2)
        else:
            tk.Button(root, text=btn, font=("Arial",18),
                      command=lambda b=btn: click(b)).grid(
                      row=i+1, column=j,
                      sticky="nsew", padx=2, pady=2)

for i in range(8):
    root.grid_rowconfigure(i, weight=1)

for j in range(5):
    root.grid_columnconfigure(j, weight=1)

root.mainloop()