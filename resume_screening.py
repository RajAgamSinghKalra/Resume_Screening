import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import seaborn as sns
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import classification_report, accuracy_score
import re
available_styles = plt.style.available
desired_style = 'seaborn-dark'
if desired_style in available_styles:
    plt.style.use(desired_style)
else:
    plt.style.use('dark_background')
def upload_file(filename=None):
    if not filename:
        filename = filedialog.askopenfilename(initialdir="/", title="Select File",
                                              filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    if filename:
        filename = filename.strip().strip('\'"')
        label_file_explorer.config(text="File Opened: " + filename.split('/')[-1])
        ra(filename)
def drop(event):
    print("Dropped file:", event.data)
    upload_file(event.data)
def ra(fName):
    global df
    try:
        df = pd.read_csv(fName, encoding='utf-8')
        output_text.insert(tk.END, "Data Loaded!\n")
        output_text.insert(tk.END, "Categories Found:\n")
        output_text.insert(tk.END, str(df['Category'].unique()) + "\n")
        catCnt = df['Category'].value_counts()
        output_text.insert(tk.END, "\nCategory Counts:\n")
        output_text.insert(tk.END, str(catCnt) + "\n")
        PCD(df)
        PPC(df)
        PWC(df.iloc[:, 0].apply(CT))
        VC(df, df.columns[0])
    except FileNotFoundError:
        messagebox.showerror("Error", "File not found: " + fName)
    except Exception as e:
        messagebox.showerror("Error", str(e))
def PCD(df):
    fig, ax = plt.subplots()
    sns.countplot(x="Category", data=df, palette="Set2", ax=ax)
    ax.set_title("Category Distribution")
    ax.tick_params(axis='x', labelsize=8)
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
def PPC(df):
    fig, ax = plt.subplots()
    sizes = df['Category'].value_counts()
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(sizes)))
    wedges, texts, autotexts = ax.pie(sizes, labels=sizes.index, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')
    ax.set_title('Category Pie Chart')
    plt.setp(autotexts, size=8, weight="bold", color="white")
    plt.setp(texts, size=8)
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
def PWC(text):
    wordcloud = WordCloud(width=800, height=400, background_color='black', colormap='plasma', max_font_size=150, random_state=42).generate(' '.join(text))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
def CT(text):
    text = re.sub('http\\S+\\s*', ' ', text)
    text = re.sub('@\\S+', '  ', text)
    text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"""), ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
def VC(df, colR):
    vectorizer = TfidfVectorizer(sublinear_tf=True, stop_words='english', max_features=1500)
    features = vectorizer.fit_transform(df[colR].apply(CT)).toarray()
    labels = df['Category']
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)
    classifier = OneVsRestClassifier(KNeighborsClassifier())
    classifier.fit(X_train, y_train)
    predictions = classifier.predict(X_test)
    output_text.insert(tk.END, "Classifier Stats\n")
    output_text.insert(tk.END, f'Train Accuracy: {accuracy_score(y_train, classifier.predict(X_train)):.2f}\n')
    output_text.insert(tk.END, f'Test Accuracy: {accuracy_score(y_test, predictions):.2f}\n')
    output_text.insert(tk.END, str(classification_report(y_test, predictions)) + "\n")
def EE(text):
    text = str(text)
    matches = re.findall(r'(\d+)\s+(years|year|months|month)', text.lower())
    total_months = 0
    for amount, unit in matches:
        if 'year' in unit:
            total_months += int(amount) * 12
        else:
            total_months += int(amount)
    return total_months
def STE():
    if 'df' not in globals() or df.empty:
        output_text.insert(tk.END, "No data loaded. Please load data first.\n")
        return
    id_col = None
    for col in df.columns:
        if "id" in col.lower() or "name" in col.lower():
            id_col = col
            break
    if not id_col:
        output_text.insert(tk.END, "No identifiable employee ID or name column found.\n")
        return
    if 'Category' not in df.columns:
        output_text.insert(tk.END, "No 'Category' column found in the data.\n")
        return
    try:
        df['Total Experience (months)'] = df.apply(lambda row: sum(EE(str(x)) for x in row), axis=1)
        top_exp = df.nlargest(10, 'Total Experience (months)')[[id_col, 'Total Experience (months)', 'Category']]
        output_text.insert(tk.END, f"Top 10 people with the most experience (sorted by {id_col}):\n")
        output_text.insert(tk.END, top_exp.to_string(index=False) + "\n")
    except Exception as e:
        print("An error occurred: ", e)
root = TkinterDnD.Tk()
root.title("Resume Analysis Tool")
root.geometry('1420x869')
root.config(bg='#333333')
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)
main_frame = tk.Frame(root, bg='#333333')
main_frame.pack(fill=tk.BOTH, expand=1)
my_canvas = tk.Canvas(main_frame, bg='#333333', highlightthickness=0)
my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
my_scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_canvas.yview, bg='#333333')
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
second_frame = tk.Frame(my_canvas, bg='#333333')
my_canvas.create_window((0,0), window=second_frame, anchor="nw")
plot_frame = tk.Frame(second_frame, bg='#333333', bd=2)
plot_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
frame = tk.Frame(second_frame, bg='#333333')
frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=20, pady=20)
open_file_btn = tk.Button(frame, text="Open File", command=lambda: upload_file(None), bg='#444444', fg='white')
open_file_btn.pack(side=tk.LEFT, padx=10)
top_exp_btn = tk.Button(frame, text="Top 10 Exp", command=STE, bg='#444444', fg='white')
top_exp_btn.pack(side=tk.LEFT, padx=10)
label_file_explorer = tk.Label(frame, text="No File Opened", bg='#333333', fg='white')
label_file_explorer.pack(side=tk.LEFT, padx=10)
output_text = scrolledtext.ScrolledText(frame, bg='#222222', fg='white', font=('consolas', 10))
output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
root.mainloop()