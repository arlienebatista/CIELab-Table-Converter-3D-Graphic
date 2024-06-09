import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tkinter import Tk, filedialog, ttk, messagebox

# Função para abrir o arquivo CSV
def open_file():
    root = Tk()
    root.withdraw()  # Ocultar a janela principal
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])  # Abre uma caixa de diálogo para selecionar o arquivo
    return file_path

# Função para carregar os dados e executar o restante do código
def load_data():
    file_path = open_file()
    if file_path:
        try:
            df = pd.read_csv(file_path)

            # Calcula o máximo e o mínimo dos valores L no conjunto de dados
            max_L = df['L'].max()
            min_L = df['L'].min()

            # Define os valores máximos e mínimos desejados de L
            desired_max_L = 100
            desired_min_L = 0

            # Ajusta os valores de L proporcionalmente dentro do intervalo desejado
            df['L'] = ((df['L'] - min_L) * (desired_max_L - desired_min_L) / (max_L - min_L) + desired_min_L)

            # Calcula as médias para cada nível de 'Trat'
            avg_df = df.groupby('Trat').mean().reset_index()

            # Cria uma lista vazia para armazenar os dataframes de dados de cor
            color_data_list = []

            # Loop pelos níveis únicos de 'Trat'
            for t in df['Trat'].unique():
                subset_df = df[df['Trat'] == t]
                a = subset_df['a'].mean()
                b = subset_df['b'].mean()
                L = subset_df['L'].mean()

                # Ponto branco de referência (D65)
                Xn, Yn, Zn = 0.950456, 1.0, 1.088754

                # Converte Lab para XYZ
                Y = (L + 16) / 116
                X = a / 500 + Y
                Z = Y - b / 200

                X = X ** 3 if X ** 3 > 0.008856 else (X - 16 / 116) / 7.787
                Y = Y ** 3 if Y ** 3 > 0.008856 else (Y - 16 / 116) / 7.787
                Z = Z ** 3 if Z ** 3 > 0.008856 else (Z - 16 / 116) / 7.787

                X *= Xn
                Y *= Yn
                Z *= Zn

                # Converte XYZ para sRGB
                R = 3.2404542 * X - 1.5371385 * Y - 0.4985314 * Z
                G = -0.9692660 * X + 1.8760108 * Y + 0.0415560 * Z
                B = 0.0556434 * X - 0.2040259 * Y + 1.0572252 * Z

                # Correção gama
                R = 1.055 * (R ** (1 / 2.4)) - 0.055 if R > 0.0031308 else 12.92 * R
                G = 1.055 * (G ** (1 / 2.4)) - 0.055 if G > 0.0031308 else 12.92 * G
                B = 1.055 * (B ** (1 / 2.4)) - 0.055 if B > 0.0031308 else 12.92 * B

                # Escala para [0, 1] e converter para [0, 255]
                sR, sG, sB = np.clip([R, G, B], 0, 1) * 255

                # Cria um dataframe com valores Lab e RGB, incluindo os níveis de 'Trat'
                color_data = pd.DataFrame({'Trat': [t], 'L': [L], 'a': [a], 'b': [b], 'sR': [sR], 'sG': [sG], 'sB': [sB]})

                # Armazena color_data na lista
                color_data_list.append(color_data)

            # Combina todos os dataframes de color_data em um só
            result_df = pd.concat(color_data_list, ignore_index=True)

            # Número de cores (níveis de Trat)
            num_colors = len(result_df)

            # Cria um gráfico de dispersão 3D
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(result_df['a'], result_df['b'], result_df['L'], c=result_df[['sR', 'sG', 'sB']].values / 255, s=100)

            ax.set_xlabel('a*')
            ax.set_ylabel('b*')
            ax.set_zlabel('L*')

            # Função para manipular o evento de fechamento da janela de plotagem
            def on_close(event):
                root.deiconify()  # Mostra a janela principal quando a janela de plotagem é fechada
                plt.close()       # Fecha a janela de plotagem

            fig.canvas.mpl_connect('close_event', on_close)  # Conecta a função on_close ao evento de fechamento da janela de plotagem

            plt.show()

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um problema ao processar o arquivo CSV: {str(e)}")

def close_program():
    root.quit()
    root.destroy()

# Cria a janela principal
root = Tk()
root.title("Graphic Color Lab 3D")

# Define as dimensões da janela
window_width = 400
window_height = 250

# Obtém as dimensões da tela
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calcula a posição central da janela
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

# Define a geometria da janela
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Estilo ttk para adicionar um tema
style = ttk.Style(root)
style.theme_use("clam")  # Você pode mudar o tema conforme necessário

# Rótulo para instruções
instructions_label = ttk.Label(root, text="Para gerar seu gráfico selecione um arquivo .csv com seus dados.", background=root.cget("background"))
instructions_label.pack(pady=10)

# Botão para abrir a caixa de diálogo para selecionar o arquivo
open_button = ttk.Button(root, text="Selecionar Arquivo", command=load_data)
open_button.pack(pady=20)

# Botão para fechar o programa
close_button = ttk.Button(root, text="Fechar", command=close_program)
close_button.pack(pady=10)

# Roda pé
rodape_label = ttk.Label(root, text="2024 @ Graphic Color Lab 3D v.1.0 ", background=root.cget("background"))
rodape_label.pack(pady=35)


# Inicia o loop principal da janela
root.mainloop()
